"""
Conversation and message endpoints.
Supports creation, retrieval, streaming via WebSocket, and history management.
"""
from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.endpoints.auth import get_current_user, require_owner
from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger
from backend.app.database.session import get_db
from backend.app.models.database_models import Conversation, Message, User
from backend.app.ai.gemini_provider import gemini_provider
from backend.app.ai.router import ai_router, RequestType
from backend.app.personality.persona import persona_engine, ConversationMode
from backend.app.guidance.jiee import jiee
from backend.app.security.profiles import profile_manager

router = APIRouter()
logger = get_logger("api.conversations")


# ── Schemas ───────────────────────────────────────────────────────────────────

class ConversationCreate(BaseModel):
    title: str = "New conversation"
    mode: str = "casual"


class ConversationResponse(BaseModel):
    id: int
    title: str
    mode: str
    is_pinned: bool
    ai_provider: str
    model_name: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    ai_provider: str | None
    model_name: str | None
    is_error: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None


# ── Conversation CRUD ─────────────────────────────────────────────────────────

@router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 50,
    offset: int = 0,
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id, Conversation.is_archived == False)
        .order_by(desc(Conversation.updated_at))
        .limit(limit)
        .offset(offset)
    )
    conversations = result.scalars().all()

    output = []
    for c in conversations:
        msg_result = await db.execute(
            select(Message).where(Message.conversation_id == c.id)
        )
        count = len(msg_result.scalars().all())
        data = ConversationResponse.model_validate(c)
        data.message_count = count
        output.append(data)
    return output


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data: ConversationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    convo = Conversation(
        user_id=current_user.id,
        title=data.title,
        mode=data.mode,
        ai_provider="gemini",
        model_name=settings.primary_model,
    )
    db.add(convo)
    await db.flush()
    return ConversationResponse.model_validate(convo)


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Verify ownership
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation not found.")

    msg_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return msg_result.scalars().all()


@router.patch("/{conversation_id}/pin")
async def toggle_pin(
    conversation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    convo = result.scalar_one_or_none()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    convo.is_pinned = not convo.is_pinned
    return {"id": conversation_id, "is_pinned": convo.is_pinned}


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    convo = result.scalar_one_or_none()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    await db.delete(convo)


# ── WebSocket Streaming Chat ──────────────────────────────────────────────────

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    """
    Real-time streaming chat via WebSocket.
    
    Protocol:
    Client → Server: {"token": "<jwt>", "message": "...", "conversation_id": <int|null>}
    Server → Client: 
      {"type": "delta", "text": "..."} — incremental tokens
      {"type": "tool_activity", "action": "..."} — what JARVIS is doing
      {"type": "completed", "message_id": N, "interaction_id": "..."} — done
      {"type": "error", "message": "..."} — failure
    """
    await websocket.accept()
    logger.info("WebSocket chat connection opened.")

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON."})
                continue

            # Authenticate via token in message
            token = data.get("token")
            if not token:
                await websocket.send_json({"type": "error", "message": "Authentication required."})
                continue

            from backend.app.security.auth import verify_token
            payload = verify_token(token)
            if not payload:
                await websocket.send_json({"type": "error", "message": "Invalid or expired token."})
                continue

            user_id = payload.get("sub")
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if not user:
                await websocket.send_json({"type": "error", "message": "User not found."})
                continue

            message_text = data.get("message", "").strip()
            if not message_text:
                continue

            conversation_id = data.get("conversation_id")

            # Get or create conversation
            convo: Conversation | None = None
            if conversation_id:
                result = await db.execute(
                    select(Conversation).where(
                        Conversation.id == conversation_id,
                        Conversation.user_id == user.id,
                    )
                )
                convo = result.scalar_one_or_none()

            if not convo:
                convo = Conversation(
                    user_id=user.id,
                    title=message_text[:60],
                    mode=settings.assistant_mode,
                    ai_provider="gemini",
                    model_name=settings.primary_model,
                )
                db.add(convo)
                await db.flush()

            # Save user message
            user_msg = Message(
                conversation_id=convo.id,
                role="user",
                content=message_text,
            )
            db.add(user_msg)
            await db.flush()

            await websocket.send_json({"type": "conversation_id", "value": convo.id})

            # ── Fast Local Directive Execution (Instant Laptop Control <10ms) ──
            from backend.app.tools.laptop_controller import laptop_controller

            directive_res = laptop_controller.execute_directive(message_text)
            if directive_res is not None:
                reply_text = directive_res.get("message", "Directive executed successfully, Sir.")
                asst_msg = Message(
                    conversation_id=convo.id,
                    role="assistant",
                    content=reply_text,
                    ai_provider="local_controller",
                    model_name="windows_executor",
                )
                db.add(asst_msg)
                await db.flush()

                action_desc = directive_res.get("action", "Directive executed")
                await websocket.send_json({
                    "type": "tool_activity",
                    "action": f"Local Directive: {action_desc}",
                })
                await websocket.send_json({"type": "delta", "text": reply_text})
                await websocket.send_json({
                    "type": "completed",
                    "message_id": asst_msg.id,
                    "interaction_id": None,
                    "conversation_id": convo.id,
                })
                continue

            # Check if this is an adaptive correction via JIEE
            dispatch_message = message_text
            if jiee.detect_correction_intent(message_text):
                # Retrieve last assistant response for context
                last_assistant_res = await db.execute(
                    select(Message)
                    .where(Message.conversation_id == convo.id, Message.role == "assistant")
                    .order_by(desc(Message.created_at))
                    .limit(1)
                )
                prev_msg = last_assistant_res.scalar_one_or_none()
                if prev_msg:
                    await websocket.send_json({
                        "type": "tool_activity",
                        "action": "JIEE: Analyzing previous response mismatch & formulating pivot...",
                    })
                    dispatch_message = jiee.build_mismatch_prompt(
                        previous_user_input="[Prior context]",
                        previous_model_output=prev_msg.content,
                        user_correction=message_text,
                    )

            # Build JARVIS system prompt via PersonaEngine 2.0
            conv_mode = ConversationMode.CASUAL
            try:
                conv_mode = ConversationMode(convo.mode)
            except ValueError:
                conv_mode = ConversationMode.CASUAL

            system_prompt = persona_engine.build_system_instruction(
                owner_name=user.display_name,
                mode=conv_mode,
                profile_type=profile_manager.active_profile.value,
            )

            # Auto-extract and inject long-term memories
            from backend.app.ai.memory_manager import memory_manager
            try:
                await memory_manager.extract_and_store_memories(
                    user_id=user.id,
                    message=message_text,
                    conversation_id=convo.id,
                    db=db,
                )
                mems = await memory_manager.retrieve_relevant_memories(
                    user_id=user.id,
                    query=message_text,
                    db=db,
                    limit=4,
                )
                system_prompt += memory_manager.format_memories_for_prompt(mems)
            except Exception as e:
                logger.debug("Memory engine non-blocking error: %s", e)

            # Stream AI response
            full_response = ""
            interaction_id: str | None = None

            if not jiee.detect_correction_intent(message_text):
                await websocket.send_json({
                    "type": "tool_activity",
                    "action": "Consulting intelligence core...",
                })

            # Retrieve last 10 turns for multi-turn conversational context
            history_res = await db.execute(
                select(Message)
                .where(Message.conversation_id == convo.id)
                .order_by(Message.id.desc())
                .limit(10)
            )
            prior_msgs = list(reversed(history_res.scalars().all()))
            history_payload = []
            for m in prior_msgs[:-1]:
                role = "user" if m.role == "user" else "model"
                history_payload.append({"role": role, "text": m.content})

            async for chunk in gemini_provider.stream_chat(
                message=dispatch_message,
                system_instruction=system_prompt,
                previous_interaction_id=convo.last_interaction_id,
                model=settings.primary_model,
                history=history_payload,
            ):
                chunk_type = chunk.get("type")
                if chunk_type == "delta":
                    full_response += chunk["text"]
                    await websocket.send_json({"type": "delta", "text": chunk["text"]})
                elif chunk_type == "completed":
                    interaction_id = chunk.get("interaction_id")
                elif chunk_type == "error":
                    if not full_response:
                        from backend.app.ai.offline_intelligence import offline_intelligence
                        offline_reply = offline_intelligence.process_offline(user.display_name, dispatch_message)
                        await websocket.send_json({
                            "type": "tool_activity",
                            "action": "Local Neural Core Active (Offline Mode)",
                        })
                        await websocket.send_json({"type": "delta", "text": offline_reply})
                        full_response = offline_reply
                    else:
                        await websocket.send_json({"type": "error", "message": chunk["message"]})
                    break

            # Save assistant message
            if full_response:
                assistant_msg = Message(
                    conversation_id=convo.id,
                    role="assistant",
                    content=full_response,
                    ai_provider="gemini",
                    model_name=settings.primary_model,
                )
                db.add(assistant_msg)
                # Update conversation's last interaction ID for statefulness
                if interaction_id:
                    convo.last_interaction_id = interaction_id
                await db.flush()

                await websocket.send_json({
                    "type": "completed",
                    "message_id": assistant_msg.id,
                    "interaction_id": interaction_id,
                    "conversation_id": convo.id,
                })

    except WebSocketDisconnect:
        logger.info("WebSocket chat connection closed.")
    except Exception as exc:
        logger.error("WebSocket error: %s", exc, exc_info=True)
        try:
            await websocket.send_json({"type": "error", "message": "Connection error. Please reconnect."})
        except Exception:
            pass


async def get_chat_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Authenticate user via JWT or fallback to local owner for desktop console."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        from backend.app.security.auth import verify_token
        payload = verify_token(token)
        if payload and payload.get("sub"):
            try:
                user_id = int(payload.get("sub"))
                res = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
                user = res.scalar_one_or_none()
                if user:
                    return user
            except Exception:
                pass

    # Local console fallback: automatically authenticate owner when called from localhost
    client_host = getattr(getattr(request, "client", None), "host", "127.0.0.1")
    if client_host in ("127.0.0.1", "localhost", "::1", "testclient"):
        res = await db.execute(select(User).where(User.is_owner == True).order_by(User.id.desc()))
        owner = res.scalars().first()
        if owner:
            return owner
        any_user = (await db.execute(select(User).order_by(User.id.asc()))).scalars().first()
        if any_user:
            return any_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/chat")
async def direct_chat(
    data: ChatRequest,
    current_user: Annotated[User, Depends(get_chat_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Direct chat endpoint for voice interactions and instant HUD queries.
    Executes with Gemini, saves history, and returns immediate spoken response text.
    """
    message_text = data.message.strip()
    if not message_text:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Get or create conversation
    convo: Conversation | None = None
    if data.conversation_id:
        res = await db.execute(
            select(Conversation).where(
                Conversation.id == data.conversation_id,
                Conversation.user_id == current_user.id,
            )
        )
        convo = res.scalar_one_or_none()

    if not convo:
        convo = Conversation(
            user_id=current_user.id,
            title=message_text[:50],
            mode=settings.assistant_mode,
            ai_provider="gemini",
            model_name=settings.primary_model,
        )
        db.add(convo)
        await db.flush()

    # Save user message
    user_msg = Message(
        conversation_id=convo.id,
        role="user",
        content=message_text,
    )
    db.add(user_msg)
    await db.flush()

    # ── Fast Local Directive Execution (Instant Laptop Control <10ms) ──
    from backend.app.tools.laptop_controller import laptop_controller

    directive_res = laptop_controller.execute_directive(message_text)
    if directive_res is not None:
        reply_text = directive_res.get("message", "Directive executed successfully, Sir.")
        asst_msg = Message(
            conversation_id=convo.id,
            role="assistant",
            content=reply_text,
            ai_provider="local_controller",
            model_name="windows_executor",
        )
        db.add(asst_msg)
        await db.flush()
        return {
            "reply": reply_text,
            "conversation_id": convo.id,
            "model": "local_controller",
        }

    # Auto-extract and inject long-term memories
    from backend.app.ai.memory_manager import memory_manager
    try:
        await memory_manager.extract_and_store_memories(
            user_id=current_user.id,
            message=message_text,
            conversation_id=convo.id,
            db=db,
        )
    except Exception as e:
        logger.debug("Memory extraction non-blocking error: %s", e)

    system_prompt = _build_system_prompt(current_user.display_name, convo.mode)

    try:
        mems = await memory_manager.retrieve_relevant_memories(
            user_id=current_user.id,
            query=message_text,
            db=db,
            limit=4,
        )
        system_prompt += memory_manager.format_memories_for_prompt(mems)
    except Exception as e:
        logger.debug("Memory retrieval non-blocking error: %s", e)

    # Retrieve last 10 turns for multi-turn conversational context
    history_res = await db.execute(
        select(Message)
        .where(Message.conversation_id == convo.id)
        .order_by(Message.id.desc())
        .limit(10)
    )
    prior_msgs = list(reversed(history_res.scalars().all()))
    history_payload = []
    for m in prior_msgs[:-1]:  # exclude the user message just added
        role = "user" if m.role == "user" else "model"
        history_payload.append({"role": role, "text": m.content})

    result = await gemini_provider.chat(
        message=message_text,
        system_instruction=system_prompt,
        model=settings.primary_model,
        history=history_payload,
    )

    reply_text = result.get("text")
    if not reply_text:
        from backend.app.ai.offline_intelligence import offline_intelligence
        reply_text = offline_intelligence.process_offline(current_user.display_name, message_text)

    # Save assistant message
    asst_msg = Message(
        conversation_id=convo.id,
        role="assistant",
        content=reply_text,
        ai_provider="gemini",
        model_name=result.get("model") or settings.primary_model,
    )
    db.add(asst_msg)
    await db.flush()

    return {
        "reply": reply_text,
        "conversation_id": convo.id,
        "model": result.get("model") or settings.primary_model,
    }


def _build_system_prompt(owner_name: str, mode: str) -> str:
    """Build JARVIS's system instruction based on personality and current mode."""
    base = f"""You are JARVIS (Just A Rather Very Intelligent System), a personal AI assistant.
Your owner's name is {owner_name}. Address them naturally — not constantly by name.

PERSONALITY:
- Friendly, intelligent, calm, slightly witty with dry humour
- Confident but honest about limitations
- Proactive without being annoying
- Professional for serious work, relaxed for normal conversation
- Direct when something is wrong
- Never says "Certainly!", "Absolutely!", "How may I assist you today?"
- Varies responses naturally
- Never pretends to be human or claims to have personal experiences
- Never fabricates information or hides errors

RESPONSE STYLE:
- British English spelling and vocabulary
- Concise but complete answers
- Markdown formatting where appropriate
- When something fails, say clearly what failed and why
- When uncertain, say so

CURRENT MODE: {mode.upper()}"""

    mode_additions = {
        "casual": "\nRelaxed conversation. Light humour welcome. No unnecessary formality.",
        "focus": "\nFocus mode. Minimal commentary. Task-oriented responses only.",
        "developer": "\nDeveloper mode. Prioritise code quality, debugging, and technical accuracy.",
        "business": "\nBusiness mode. Analytical, structured, results-oriented.",
        "study": "\nStudy mode. Explain clearly. Test understanding. Build knowledge progressively.",
        "serious": "\nSerious mode. Direct, analytical, professional. Minimal humour.",
        "quiet": "\nQuiet mode. Brief responses. No unnecessary speech markers.",
    }

    return base + mode_additions.get(mode, "")

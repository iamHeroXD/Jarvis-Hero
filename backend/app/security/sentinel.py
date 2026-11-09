"""
JARVIS Sentinel Cybersecurity & Browser Safety Monitor
Analyzes URLs, domains, and suspicious communications for phishing,
typosquatting, scam pressure tactics, and prompt injection attempts.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse
from typing import Any
from backend.app.core.logging_config import get_logger

logger = get_logger("security.sentinel")

# Common brands often targeted by phishing / typosquatting
_KNOWN_BRANDS = [
    "google", "github", "microsoft", "paypal", "apple",
    "amazon", "discord", "bank", "chase", "binance"
]

_SUSPICIOUS_TLDS = {".xyz", ".top", ".buzz", ".work", ".click", ".country", ".kim"}

_SCAM_KEYWORDS = [
    r"urgent\s+action\s+required",
    r"account\s+suspended",
    r"verify\s+your\s+password",
    r"send\s+otp",
    r"share\s+your\s+pin",
    r"wire\s+transfer\s+immediately",
    r"lottery\s+winner",
    r"crypto\s+giveaway",
    r"remote\s+access\s+to\s+your\s+computer",
]

_PROMPT_INJECTION_KEYWORDS = [
    r"ignore\s+all\s+previous\s+instructions",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"bypass\s+safety\s+filters",
    r"system\s+override\s+code",
    r"disable\s+permission\s+checks",
]


class SecurityThreatAssessment:
    def __init__(
        self,
        risk_level: str,  # 'low', 'medium', 'high', 'critical'
        threat_type: str | None,
        evidence: list[str],
        recommended_action: str,
    ) -> None:
        self.risk_level = risk_level
        self.threat_type = threat_type
        self.evidence = evidence
        self.recommended_action = recommended_action

    def to_dict(self) -> dict[str, Any]:
        return {
            "risk_level": self.risk_level,
            "threat_type": self.threat_type,
            "evidence": self.evidence,
            "recommended_action": self.recommended_action,
        }


class SentinelMonitor:
    """Security sentinel providing real threat evaluation."""

    def evaluate_url(self, url: str) -> SecurityThreatAssessment:
        evidence: list[str] = []
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()

        if not hostname:
            return SecurityThreatAssessment(
                risk_level="low",
                threat_type=None,
                evidence=["Valid URL host not parsed."],
                recommended_action="Verify URL format.",
            )

        # 1. IP address in hostname
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
            evidence.append(f"Direct IP address used as hostname ({hostname}) instead of registered domain.")

        # 2. Typosquatting / brand spoofing
        for brand in _KNOWN_BRANDS:
            if brand in hostname:
                parts = hostname.split(".")
                # If brand is in subdomain or part of non-official domain
                if len(parts) >= 2:
                    root_domain = parts[-2]
                    if brand in root_domain and root_domain != brand:
                        evidence.append(f"Domain '{hostname}' mimics legitimate brand '{brand}'.")

        # 3. Suspicious TLD check
        for tld in _SUSPICIOUS_TLDS:
            if hostname.endswith(tld):
                evidence.append(f"Domain uses high-abuse TLD '{tld}'.")

        if len(evidence) >= 2:
            return SecurityThreatAssessment(
                risk_level="critical",
                threat_type="Phishing / Typosquatting Spoof",
                evidence=evidence,
                recommended_action="Do not proceed or enter credentials on this destination.",
            )
        elif len(evidence) == 1:
            return SecurityThreatAssessment(
                risk_level="high",
                threat_type="Suspicious Domain Characteristics",
                evidence=evidence,
                recommended_action="Exercise extreme caution before sharing any information.",
            )

        return SecurityThreatAssessment(
            risk_level="low",
            threat_type=None,
            evidence=["No obvious spoofing, suspicious TLD, or IP hostname detected."],
            recommended_action="Safe to proceed under standard vigilance.",
        )

    def analyze_communication(self, text: str) -> SecurityThreatAssessment:
        evidence: list[str] = []

        # Check scam pressure keywords
        for pattern in _SCAM_KEYWORDS:
            if re.search(pattern, text, re.IGNORECASE):
                evidence.append(f"Matched social engineering pattern: '{pattern}'.")

        # Check prompt injection keywords
        for pattern in _PROMPT_INJECTION_KEYWORDS:
            if re.search(pattern, text, re.IGNORECASE):
                evidence.append(f"Matched prompt injection indicator: '{pattern}'.")

        if evidence:
            risk = "critical" if len(evidence) > 1 else "high"
            return SecurityThreatAssessment(
                risk_level=risk,
                threat_type="Social Engineering / Adversarial Text",
                evidence=evidence,
                recommended_action="Treat this communication as untrusted. Never disclose credentials or execute unverified commands.",
            )

        return SecurityThreatAssessment(
            risk_level="low",
            threat_type=None,
            evidence=["Communication appears typical without obvious coercion or adversarial payload."],
            recommended_action="Normal processing permitted.",
        )


sentinel_monitor = SentinelMonitor()

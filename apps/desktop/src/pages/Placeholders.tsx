// Placeholder pages for navigation — full implementation in later phases

export function MemoryPage() {
  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold text-text-primary mb-2">Memory</h1>
      <p className="text-text-secondary text-sm">Long-term memory management — Phase 3.</p>
    </div>
  );
}

export function AgentsPage() {
  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold text-text-primary mb-2">Agents</h1>
      <p className="text-text-secondary text-sm">ATLAS, ORACLE, NEXUS, ATHENA, ECHO, SENTINEL — Phase 6.</p>
    </div>
  );
}

export function ProjectsPage() {
  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold text-text-primary mb-2">Projects</h1>
      <p className="text-text-secondary text-sm">Project management and workspace — Phase 5.</p>
    </div>
  );
}

export function TasksPage() {
  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold text-text-primary mb-2">Tasks</h1>
      <p className="text-text-secondary text-sm">Task engine, reminders, and scheduling — Phase 7.</p>
    </div>
  );
}

export function AutomationsPage() {
  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold text-text-primary mb-2">Automations</h1>
      <p className="text-text-secondary text-sm">Scheduled jobs and automation workflows — Phase 7.</p>
    </div>
  );
}

export function ActivityPage() {
  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold text-text-primary mb-2">Activity</h1>
      <p className="text-text-secondary text-sm">Audit log and activity history — Phase 1+.</p>
    </div>
  );
}

export function SystemPage() {
  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold text-text-primary mb-2">System</h1>
      <p className="text-text-secondary text-sm">Detailed system monitoring — Phase 8.</p>
    </div>
  );
}

export function SettingsPage() {
  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold text-text-primary mb-2">Settings</h1>
      <p className="text-text-secondary text-sm">Application configuration — available throughout development.</p>
      <div className="mt-6 card p-4">
        <p className="text-text-secondary text-sm">
          Configure your Gemini API key and other settings here.
          Full settings UI arrives in Phase 10.
        </p>
      </div>
    </div>
  );
}

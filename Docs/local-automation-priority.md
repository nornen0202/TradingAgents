# Local automation scheduling priority

Install the time-sensitive local automation lanes with Windows Task Scheduler priority **4**. The previous implicit default, **7**, uses background CPU scheduling. The October 29 production processes also had low I/O priority (1) and low memory priority (2), while direct execution of the same archive queries was much faster. Normalizing the active research process to CPU Normal, I/O Normal (2), and memory Normal (5) allowed its postprocessing to progress without restarting or changing its analysis artifacts.

All five installers now set `-Priority 4` explicitly. Existing triggers, hidden launchers, instance policies, limits, authorization markers and trading controls are unchanged. Priority 4 is ordinary interactive priority, not high or real-time priority.

For an existing installation, back up the task definitions and change only `Settings.Priority` on its `LocalAutomation-*` tasks. Preserve each task's enabled state. Task updates affect future launches; an already running process retains its current resource priorities unless separately normalized. Do not restart a healthy analysis merely to adopt the scheduling setting.

References: [Microsoft TaskSettings priority](https://learn.microsoft.com/en-us/windows/win32/taskschd/tasksettings-priority) and [Microsoft task schema resource-priority mapping](https://github.com/MicrosoftDocs/win32/blob/docs/desktop-src/TaskSchd/taskschedulerschema-priority-settingstype-element.md).

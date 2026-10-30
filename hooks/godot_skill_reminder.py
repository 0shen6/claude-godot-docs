"""Claude Code hook: remind Claude to use the godot-docs skill when working on GDScript.

UserPromptSubmit: if the session's folder (or a parent) holds project.godot, add a reminder
to the prompt. PreToolUse on Write/Edit: if the target is a .gd file, add the reminder to
the tool call. Anything else prints nothing. Never blocks; always exits 0.
"""
import json
import os
import sys

REMINDER = (
    "Godot 4.5 GDScript work: load the godot-docs skill and confirm every Godot API you use "
    "with `gdocs` (read / lookup / search --also) before writing or editing GDScript. "
    "Godot 3 names look plausible; don't rely on memory."
)
GODOT_SUFFIXES = (".gd", ".tscn", ".tres")


def in_godot_project(start):
    path = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(path, "project.godot")):
            return True
        parent = os.path.dirname(path)
        if parent == path:
            return False
        path = parent


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    event = data.get("hook_event_name")
    if event == "UserPromptSubmit":
        if in_godot_project(data.get("cwd") or os.getcwd()):
            print(REMINDER)
    elif event == "PreToolUse":
        file_path = (data.get("tool_input") or {}).get("file_path") or ""
        if file_path.lower().endswith(GODOT_SUFFIXES):
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": REMINDER,
            }}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass

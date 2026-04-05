#!/usr/bin/env python3
import json
import subprocess
import sys

ACTIVE_OPACITY = 1.0
INACTIVE_OPACITY = float(sys.argv[1]) if len(sys.argv) > 1 else 0.8


def swaymsg(*args):
    return subprocess.run(["swaymsg"] + list(args), capture_output=True, text=True).stdout


def set_opacity(con_id, opacity):
    swaymsg(f"[con_id={con_id}]", "opacity", str(opacity))


def get_all_windows(tree):
    windows = []
    if tree.get("type") in ("con", "floating_con") and tree.get("pid"):
        windows.append(tree["id"])
    for node in tree.get("nodes", []) + tree.get("floating_nodes", []):
        windows.extend(get_all_windows(node))
    return windows


def get_focused(tree):
    if tree.get("focused"):
        return tree["id"]
    for node in tree.get("nodes", []) + tree.get("floating_nodes", []):
        found = get_focused(node)
        if found:
            return found
    return None


tree = json.loads(swaymsg("-t", "get_tree"))
focused = get_focused(tree)
for wid in get_all_windows(tree):
    set_opacity(wid, ACTIVE_OPACITY if wid == focused else INACTIVE_OPACITY)

last_focused = focused

proc = subprocess.Popen(
    ["swaymsg", "-t", "subscribe", "-m", '["window"]'],
    stdout=subprocess.PIPE,
    text=True,
)

for line in proc.stdout:
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        continue
    change = event.get("change")
    container = event.get("container", {})
    con_id = container.get("id")
    if not con_id:
        continue
    if change == "focus":
        if last_focused and last_focused != con_id:
            set_opacity(last_focused, INACTIVE_OPACITY)
        set_opacity(con_id, ACTIVE_OPACITY)
        last_focused = con_id
    elif change == "new":
        set_opacity(con_id, INACTIVE_OPACITY)
    elif change == "close":
        if last_focused == con_id:
            last_focused = None

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shield Kali Linux Full Tools Launcher (Sudo-Optimized)
Compatible with ethical acknowledgment: Abdullah Ahmed Ali
Discovers all installed kali tools and runs them safely with sudo
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

ETHICAL_ACK = """
===============================================================
Ethical Use Acknowledgment
===============================================================
I, Abdullah Ahmed Ali, acknowledge ethical and legal usage only
on my own devices and network. Full responsibility accepted.
===============================================================
"""

def require_ethical():
    print(ETHICAL_ACK)
    while True:
        ans = input("Agree and accept responsibility (yes/نعم): ").strip().lower()
        if ans in ("yes", "نعم"):
            print("\nAcknowledgment confirmed. Scanning tools...")
            return
        if ans in ("no", "لا", "exit", "quit"):
            print("Cancelled.")
            sys.exit(0)

def is_root():
    if os.name == "nt":
        return False
    return os.geteuid() == 0

def check_sudo_access():
    res = subprocess.run(["sudo", "-n", "true"], capture_output=True)
    return res.returncode == 0

def discover_kali_tools():
    tools = {}
    try:
        pkg_res = subprocess.run(
            ["dpkg-query", "-W", "-f=${Package}\n", "kali-*"],
            capture_output=True, text=True
        )
        packages = pkg_res.stdout.strip().split("\n")
        for pkg in packages:
            if not pkg:
                continue
            files_res = subprocess.run(["dpkg", "-L", pkg], capture_output=True, text=True)
            for line in files_res.stdout.splitlines():
                path = line.strip()
                if (os.path.isfile(path) and os.access(path, os.X_OK)
                        and not path.startswith("/usr/share")):
                    cmd = os.path.basename(path)
                    if cmd and cmd not in tools:
                        tools[cmd] = {"pkg": pkg, "path": path}
    except Exception:
        pass
    return dict(sorted(tools.items()))

def run_tool_sudo(cmd: str, args: str = ""):
    full_cmd = [cmd] + args.split() if args else [cmd]
    if not is_root():
        full_cmd = ["sudo"] + full_cmd
    print(f"\nRunning: {' '.join(full_cmd)}")
    print("=" * 60)
    try:
        proc = subprocess.run(full_cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
        print("=" * 60)
        if proc.returncode == 0:
            print("Done successfully.")
        else:
            print(f"Exit code: {proc.returncode}")
    except KeyboardInterrupt:
        print("\nInterrupted.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    require_ethical()
    os.system("clear" if os.name == "posix" else "cls")

    if os.name != "nt" and not is_root() and not check_sudo_access():
        print("No valid sudo access.")
        print("Run with: sudo python3 kali_launcher.py")
        sys.exit(1)

    print("Discovering installed Kali tools...")
    tools = discover_kali_tools()

    if not tools:
        print("No Kali tools found.")
        print("Install: sudo apt install kali-linux-large")
        sys.exit(1)

    tool_list = list(tools.items())
    page_size = 20
    page = 0

    while True:
        start = page * page_size
        end = start + page_size
        current_page = tool_list[start:end]
        total_pages = (len(tool_list) - 1) // page_size + 1

        print(f"\nKali Tools ({len(tool_list)}) | Page {page+1}/{total_pages}")
        print("-" * 60)
        for idx, (cmd, info) in enumerate(current_page, start + 1):
            print(f"  {idx:3}. {cmd:<20} {info['pkg']}")

        print("\nOptions: <number>=run  s=search  n/p=next/prev  c=custom  q=quit")
        choice = input("\nChoice: ").strip().lower()

        if choice == "q":
            print("Goodbye.")
            sys.exit(0)

        if choice == "c":
            cmd_input = input("Enter full command: ").strip()
            if cmd_input:
                parts = cmd_input.split()
                run_tool_sudo(parts[0], " ".join(parts[1:]))
            input("\nPress Enter to continue...")
            os.system("clear" if os.name == "posix" else "cls")
            continue

        if choice == "s":
            q = input("Search: ").strip().lower()
            matches = [t for t in tool_list if q in t[0].lower() or q in t[1]["pkg"].lower()]
            if not matches:
                print("No results.")
                continue
            for idx, (cmd, info) in enumerate(matches, 1):
                print(f"  {idx}. {cmd} | {info['pkg']}")
            sel = input("Select number (or Enter to cancel): ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(matches):
                cmd, info = matches[int(sel) - 1]
                args = input("Extra args (optional): ").strip()
                run_tool_sudo(cmd, args)
            input("\nPress Enter to continue...")
            os.system("clear" if os.name == "posix" else "cls")
            continue

        if choice in ("n", "next"):
            if end < len(tool_list):
                page += 1
            else:
                print("Last page.")
            continue
        if choice in ("p", "prev"):
            if page > 0:
                page -= 1
            else:
                print("First page.")
            continue

        if choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(tool_list):
                cmd, info = tool_list[num - 1]
                args = input(f"Extra args for {cmd} (optional): ").strip()
                run_tool_sudo(cmd, args)
            else:
                print("Number out of range.")
            input("\nPress Enter to continue...")
            os.system("clear" if os.name == "posix" else "cls")
        else:
            print("Unknown option.")

if __name__ == "__main__":
    main()

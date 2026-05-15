import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import subprocess
from observer.activity_logger import init_db, log_event

IGNORED_COMMANDS = {'cls', 'clear', 'history', 'pwd', 'ls', 'dir', 'cd'}

def run_command(command: str):
    cwd = os.getcwd()
    parts = command.strip().split()
    if not parts:
        return
    base_cmd = parts[0].lower()
    if base_cmd in IGNORED_COMMANDS:
        result = subprocess.run(command, shell=True)
        return

    log_event("shell_command", command, cwd)
    print(f"[GruntKill] Logged: {command}")
    result = subprocess.run(command, shell=True)
    return result

def start_shell():
    init_db()
    print("✓ GruntKill shell started — type commands normally")
    print("  Type 'exit' to quit\n")
    while True:
        try:
            cmd = input(f"gk:{os.getcwd()}$ ").strip()
            if cmd.lower() == 'exit':
                print("✓ Shell exited")
                break
            if cmd:
                run_command(cmd)
        except KeyboardInterrupt:
            print("\n✓ Shell exited")
            break

if __name__ == "__main__":
    start_shell()
    
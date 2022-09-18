"""Script to run database-related scripts

This is slightly ugly, but running the scripts directly isn't possible because of imports
This could be cleaned up a bit using importlib but this is safer
"""
import asyncio
import sys
from typing import Callable

from database.scripts.db00_example import main as debug_add_courses

script_mapping: dict[str, Callable] = {"debug_add_courses.py": debug_add_courses}


if __name__ == "__main__":
    scripts = sys.argv[1:]
    if not scripts:
        print("No scripts provided.", file=sys.stderr)
        exit(1)

    for script in scripts:
        script_main = script_mapping.get(script.removeprefix("database/scripts/"), None)
        if script_main is None:
            print(f'Script "{script}" not found.', file=sys.stderr)
            exit(1)

        asyncio.run(script_main())
        print(f"Successfully ran {script}")

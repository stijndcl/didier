"""Script to run database-related scripts

This is slightly ugly, but running the scripts directly isn't possible because of imports
This could be cleaned up a bit using importlib but this is safer
"""
import asyncio
import importlib
import sys
from typing import Callable


async def main():
    """Try to parse all command-line arguments into modules and run them sequentially"""
    scripts = sys.argv[1:]
    if not scripts:
        print("No scripts provided.", file=sys.stderr)
        exit(1)

    for script in scripts:
        script = script.replace("/", ".").removesuffix(".py")
        module = importlib.import_module(script)

        try:
            script_main: Callable = module.main
            await script_main()
            print(f"Successfully ran {script}")
        except AttributeError:
            print(f'Script "{script}" not found.', file=sys.stderr)
            exit(1)


if __name__ == "__main__":
    asyncio.run(main())

"""Entry point for the Game Boy emulator.

Usage:
    python -m gbemu <rom_file>
"""

import sys

from .GBEmu import GBEmu


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <rom_file>")
        sys.exit(1)

    rom_path = sys.argv[1]
    emu = GBEmu()
    emu.loadROM(rom_path)
    emu.start()


if __name__ == "__main__":
    main()

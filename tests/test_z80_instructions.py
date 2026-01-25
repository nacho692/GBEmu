"""
Comprehensive Z80 instruction tests using type-safe test infrastructure.

This module provides unified test cases for all Z80 CPU instructions with:
- Type-safe register and flag access using enums
- Memory value operations with typed objects
- Expected state verification in single unified approach
- Quick feedback for initial instruction validation
"""

import pytest
from enum import Enum
from dataclasses import dataclass, field
from typing import Union, List

# Add src path for imports
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from gbemu.Z80 import Z80


class Register(Enum):
    """CPU register enumeration for type-safe access."""

    A = "AF.high"
    F = "AF.low"
    AF = "AF.value"
    B = "BC.high"
    C = "BC.low"
    BC = "BC.value"
    D = "DE.high"
    E = "DE.low"
    DE = "DE.value"
    H = "HL.high"
    L = "HL.low"
    HL = "HL.value"
    SP = "SP.value"
    PC = "PC.value"


class Flag(Enum):
    """Flag enumeration for type-safe flag operations."""

    ZERO = "ZERO"
    SUB = "SUB"
    HALF_CARRY = "HALF_CARRY"
    CARRY = "CARRY"


@dataclass
class RegisterValue:
    """Register assignment for test setup/verification."""

    register: Register
    value: int


@dataclass
class MemoryValue:
    """Memory assignment for test setup/verification."""

    address: int
    value: int


@dataclass
class FlagValue:
    """Flag assignment for test setup/verification."""

    flag: Flag
    value: bool


@dataclass
class InstructionTestCase:
    """Unified test case structure for Z80 instructions."""

    name: str
    opcode: int
    setup: List[Union[RegisterValue, MemoryValue, FlagValue]]
    expected: List[Union[RegisterValue, MemoryValue, FlagValue]]
    description: str
    cycles: int


class CPUStateValidator:
    """Type-safe CPU state validation utilities."""

    # Register access mapping
    REGISTER_GETTERS = {
        Register.A: lambda cpu: cpu._AF.high,
        Register.F: lambda cpu: cpu._AF.low,
        Register.AF: lambda cpu: cpu._AF.value,
        Register.B: lambda cpu: cpu._BC.high,
        Register.C: lambda cpu: cpu._BC.low,
        Register.BC: lambda cpu: cpu._BC.value,
        Register.D: lambda cpu: cpu._DE.high,
        Register.E: lambda cpu: cpu._DE.low,
        Register.DE: lambda cpu: cpu._DE.value,
        Register.H: lambda cpu: cpu._HL.high,
        Register.L: lambda cpu: cpu._HL.low,
        Register.HL: lambda cpu: cpu._HL.value,
        Register.SP: lambda cpu: cpu._SP.value,
        Register.PC: lambda cpu: cpu._PC.value,
    }

    REGISTER_SETTERS = {
        Register.A: lambda cpu, val: setattr(cpu._AF, "high", val),
        Register.F: lambda cpu, val: setattr(cpu._AF, "low", val),
        Register.AF: lambda cpu, val: setattr(cpu._AF, "value", val),
        Register.B: lambda cpu, val: setattr(cpu._BC, "high", val),
        Register.C: lambda cpu, val: setattr(cpu._BC, "low", val),
        Register.BC: lambda cpu, val: setattr(cpu._BC, "value", val),
        Register.D: lambda cpu, val: setattr(cpu._DE, "high", val),
        Register.E: lambda cpu, val: setattr(cpu._DE, "low", val),
        Register.DE: lambda cpu, val: setattr(cpu._DE, "value", val),
        Register.H: lambda cpu, val: setattr(cpu._HL, "high", val),
        Register.L: lambda cpu, val: setattr(cpu._HL, "low", val),
        Register.HL: lambda cpu, val: setattr(cpu._HL, "value", val),
        Register.SP: lambda cpu, val: setattr(cpu._SP, "value", val),
        Register.PC: lambda cpu, val: setattr(cpu._PC, "value", val),
    }

    # Flag access mapping
    FLAG_GETTERS = {
        Flag.ZERO: lambda cpu: (cpu._AF.low & 0x80) != 0,
        Flag.SUB: lambda cpu: (cpu._AF.low & 0x40) != 0,
        Flag.HALF_CARRY: lambda cpu: (cpu._AF.low & 0x20) != 0,
        Flag.CARRY: lambda cpu: (cpu._AF.low & 0x10) != 0,
    }

    FLAG_SETTERS = {
        Flag.ZERO: lambda cpu, val: setattr(
            cpu._AF, "low", (cpu._AF.low | 0x80) if val else (cpu._AF.low & ~0x80)
        )
        or (cpu._AF.low | 0x80)
        if val
        else (cpu._AF.low & ~0x80),
        Flag.SUB: lambda cpu, val: setattr(
            cpu._AF, "low", (cpu._AF.low | 0x40) if val else (cpu._AF.low & ~0x40)
        )
        or (cpu._AF.low | 0x40)
        if val
        else (cpu._AF.low & ~0x40),
        Flag.HALF_CARRY: lambda cpu, val: setattr(
            cpu._AF, "low", (cpu._AF.low | 0x20) if val else (cpu._AF.low & ~0x20)
        )
        or (cpu._AF.low | 0x20)
        if val
        else (cpu._AF.low & ~0x20),
        Flag.CARRY: lambda cpu, val: setattr(
            cpu._AF, "low", (cpu._AF.low | 0x10) if val else (cpu._AF.low & ~0x10)
        )
        or (cpu._AF.low | 0x10)
        if val
        else (cpu._AF.low & ~0x10),
    }

    @staticmethod
    def setup_state(
        cpu: Z80, setup_list: List[Union[RegisterValue, MemoryValue, FlagValue]]
    ):
        """Setup CPU state including initial flag conditions."""
        for item in setup_list:
            if isinstance(item, RegisterValue):
                CPUStateValidator.REGISTER_SETTERS[item.register](cpu, item.value)
            elif isinstance(item, MemoryValue):
                cpu._mem.wb(item.address, item.value)
            elif isinstance(item, FlagValue):
                current_flags = cpu._AF.low
                new_flags = CPUStateValidator.FLAG_SETTERS[item.flag](cpu, item.value)
                cpu._AF.low = new_flags

    @staticmethod
    def verify_state(
        cpu: Z80, expected_list: List[Union[RegisterValue, MemoryValue, FlagValue]]
    ) -> bool:
        """Verify CPU state including expected flag values."""
        for item in expected_list:
            if isinstance(item, RegisterValue):
                actual = CPUStateValidator.REGISTER_GETTERS[item.register](cpu)
                if actual != item.value:
                    print(
                        f"Register {item.register}: expected 0x{item.value:02X}, got 0x{actual:02X}"
                    )
                    return False
            elif isinstance(item, MemoryValue):
                actual = cpu._mem.rb(item.address)
                if actual != item.value:
                    print(
                        f"Memory 0x{item.address:04X}: expected 0x{item.value:02X}, got 0x{actual:02X}"
                    )
                    return False
            elif isinstance(item, FlagValue):
                actual = CPUStateValidator.FLAG_GETTERS[item.flag](cpu)
                if actual != item.value:
                    print(f"Flag {item.flag}: expected {item.value}, got {actual}")
                    return False
            else:
                raise TypeError(f"Unknown expected type: {type(item)}")
        return True

    @staticmethod
    def execute_instruction(cpu: Z80, opcode: int):
        """Execute single instruction and handle PC increment."""
        # Store initial PC for instruction fetch
        initial_pc = cpu._PC.value

        # Execute the instruction (it should handle its own PC increment)
        cpu._opmap[opcode]()

        # If PC didn't change during instruction execution, increment by 1
        if cpu._PC.value == initial_pc:
            cpu._PC.value += 1

    @staticmethod
    def assert_state(cpu: Z80, test_case: InstructionTestCase):
        """Unified assertion for registers, memory, and flags."""
        # Verify expected state
        assert CPUStateValidator.verify_state(cpu, test_case.expected), (
            f"{test_case.name} failed state verification"
        )

        # If no FlagValue objects in expected, assume flags unchanged
        if not any(isinstance(item, FlagValue) for item in test_case.expected):
            # Get initial flag state from setup
            initial_flags = {}
            for item in test_case.setup:
                if isinstance(item, FlagValue):
                    initial_flags[item.flag] = item.value

            # Verify initial flags haven't changed
            for flag, expected_value in initial_flags.items():
                actual = CPUStateValidator.FLAG_GETTERS[flag](cpu)
                if actual != expected_value:
                    # If flag was not in initial flags, assume it should be False
                    if flag not in initial_flags and actual:
                        raise AssertionError(
                            f"Flag {flag} unexpectedly set in {test_case.name}"
                        )
                    elif actual != expected_value:
                        raise AssertionError(
                            f"Flag {flag} changed in {test_case.name}: expected {expected_value}, got {actual}"
                        )


# 8-Bit Register Load Test Cases - Comprehensive register-to-register transfers
LD_REGISTER_CASES = [
    # Instructions loading into A (0x78-0x7F)
    InstructionTestCase(
        name="LD A,B",
        opcode=0x78,
        setup=[RegisterValue(Register.B, 0x42)],
        expected=[RegisterValue(Register.A, 0x42)],
        description="Copy B to A",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD A,C",
        opcode=0x79,
        setup=[RegisterValue(Register.C, 0x55)],
        expected=[RegisterValue(Register.A, 0x55)],
        description="Copy C to A",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD A,D",
        opcode=0x7A,
        setup=[RegisterValue(Register.D, 0x11)],
        expected=[RegisterValue(Register.A, 0x11)],
        description="Copy D to A",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD A,E",
        opcode=0x7B,
        setup=[RegisterValue(Register.E, 0x22)],
        expected=[RegisterValue(Register.A, 0x22)],
        description="Copy E to A",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD A,H",
        opcode=0x7C,
        setup=[RegisterValue(Register.H, 0x33)],
        expected=[RegisterValue(Register.A, 0x33)],
        description="Copy H to A",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD A,L",
        opcode=0x7D,
        setup=[RegisterValue(Register.L, 0x44)],
        expected=[RegisterValue(Register.A, 0x44)],
        description="Copy L to A",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD A,A",
        opcode=0x7F,
        setup=[RegisterValue(Register.A, 0xFF)],
        expected=[RegisterValue(Register.A, 0xFF)],
        description="Copy A to A (identity)",
        cycles=1,
    ),
    # Instructions loading into B (0x40-0x47)
    InstructionTestCase(
        name="LD B,B",
        opcode=0x40,
        setup=[RegisterValue(Register.B, 0x99)],
        expected=[RegisterValue(Register.B, 0x99)],
        description="Copy B to B (identity)",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD B,C",
        opcode=0x41,
        setup=[RegisterValue(Register.C, 0x77)],
        expected=[RegisterValue(Register.B, 0x77)],
        description="Copy C to B",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD B,D",
        opcode=0x42,
        setup=[RegisterValue(Register.D, 0x12)],
        expected=[RegisterValue(Register.B, 0x12)],
        description="Copy D to B",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD B,E",
        opcode=0x43,
        setup=[RegisterValue(Register.E, 0x34)],
        expected=[RegisterValue(Register.B, 0x34)],
        description="Copy E to B",
        cycles=1,
    ),
]

# Rotation/Shift Operations Test Cases (RL, RR, RLC, RRC, SLA, SRA, SRL, SWAP) - FIXED TESTED
ROTATION_SHIFT_CASES = [
    # SWAP Operations - swap nibbles
    InstructionTestCase(
        name="SWAP A - swap nibbles",
        opcode=0x37,  # CB prefix + 0x37
        setup=[
            RegisterValue(Register.A, 0x0F),  # 0b00001111
        ],
        expected=[
            RegisterValue(Register.A, 0xF0),  # 0b11110000 (nibbles swapped)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Swap nibbles in A - 0x0F -> 0xF0",
        cycles=2,
    ),
    InstructionTestCase(
        name="SWAP B - swap nibbles",
        opcode=0x30,  # CB prefix + 0x30
        setup=[
            RegisterValue(Register.B, 0x8A),  # 0b10001010
        ],
        expected=[
            RegisterValue(Register.B, 0xA8),  # 0b10101000 (nibbles swapped)
        ],
        description="Swap nibbles in B - 0x8A -> 0xA8",
        cycles=2,
    ),
    InstructionTestCase(
        name="SWAP [HL] - swap nibbles in memory",
        opcode=0x36,  # CB prefix + 0x36
        setup=[
            RegisterValue(Register.HL, 0xC200),
            MemoryValue(0xC200, 0x37),  # 0b00110111
        ],
        expected=[
            MemoryValue(0xC200, 0x73),  # 0b01110011 (nibbles swapped)
        ],
        description="Swap nibbles at [HL]",
        cycles=4,
    ),
    # RLC Operations - rotate left circular
    InstructionTestCase(
        name="RLC A - rotate left circular",
        opcode=0x07,  # CB prefix + 0x07
        setup=[
            RegisterValue(Register.A, 0x85),  # 0b10000101
        ],
        expected=[
            RegisterValue(
                Register.A, 0x0B
            ),  # 0b00001011 (rotated left, bit 7 -> carry)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out = original bit 7
        ],
        description="Rotate A left circular with carry out",
        cycles=2,
    ),
    InstructionTestCase(
        name="RLC A - rotate left with zero result",
        opcode=0x07,  # CB prefix + 0x07
        setup=[
            RegisterValue(Register.A, 0x00),  # 0b00000000
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # 0b00000000 (rotated left, no change)
            FlagValue(Flag.ZERO, True),  # Zero result
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),  # No carry out
        ],
        description="Rotate A left with zero result",
        cycles=2,
    ),
    # RR Operations - rotate right through carry
    InstructionTestCase(
        name="RR A - rotate right through carry",
        opcode=0x1F,  # CB prefix + 0x1F
        setup=[
            RegisterValue(Register.A, 0x40),  # 0b01000000
            FlagValue(Flag.CARRY, True),  # Carry in = 1
        ],
        expected=[
            RegisterValue(
                Register.A, 0xA0
            ),  # 0b10100000 (rotate right: old bit 0 becomes carry, carry becomes bit 7)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),  # Carry out = original bit 0
        ],
        description="Rotate A right through carry",
        cycles=2,
    ),
    InstructionTestCase(
        name="RR A - rotate right through carry with carry out",
        opcode=0x1F,  # CB prefix + 0x1F
        setup=[
            RegisterValue(Register.A, 0x01),  # 0b00000001 (bit 0 = 1)
            FlagValue(Flag.CARRY, False),  # Carry in = 0
        ],
        expected=[
            RegisterValue(
                Register.A, 0x00
            ),  # 0b00000000 (rotate right: bit 0 -> carry, carry -> bit 7)
            FlagValue(Flag.ZERO, True),  # Zero result
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out = original bit 0
        ],
        description="Rotate A right through carry with carry out",
        cycles=2,
    ),
    # SLA Operations - shift left arithmetic
    InstructionTestCase(
        name="SLA A - shift left arithmetic",
        opcode=0x27,  # CB prefix + 0x27
        setup=[
            RegisterValue(Register.A, 0x85),  # 0b10000101
        ],
        expected=[
            RegisterValue(
                Register.A, 0x0A
            ),  # 0b00001010 (shifted left, bit 7 -> carry)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out from bit 7 overflow
        ],
        description="Shift A left arithmetic with carry",
        cycles=2,
    ),
    InstructionTestCase(
        name="SLA A - shift left arithmetic without overflow",
        opcode=0x27,  # CB prefix + 0x27
        setup=[
            RegisterValue(Register.A, 0x2F),  # 0b00101111
        ],
        expected=[
            RegisterValue(Register.A, 0x5E),  # 0b01011110 (0x2F << 1)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),  # No carry out
        ],
        description="Shift A left arithmetic without overflow",
        cycles=2,
    ),
    # SRA Operations - shift right arithmetic preserving sign
    InstructionTestCase(
        name="SRA A - shift right arithmetic preserving sign",
        opcode=0x2F,  # CB prefix + 0x2F
        setup=[
            RegisterValue(Register.A, 0x85),  # 0b10000101
        ],
        expected=[
            RegisterValue(
                Register.A, 0xC2
            ),  # 0b11000010 (preserve sign bit 7, shift right)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out from bit 0
        ],
        description="Shift A right arithmetic preserving sign",
        cycles=2,
    ),
    InstructionTestCase(
        name="SRA A - shift right preserving sign bit set",
        opcode=0x2F,  # CB prefix + 0x2F
        setup=[
            RegisterValue(Register.A, 0x80),  # 0b10000000 (sign bit set)
        ],
        expected=[
            RegisterValue(
                Register.A, 0xC0
            ),  # 0b11000000 (preserve sign bit 7, shift right)
            FlagValue(Flag.ZERO, False),  # Result is 0xC0, not zero
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),  # No carry from bit 0
        ],
        description="Shift A right arithmetic preserving sign bit set",
        cycles=2,
    ),
    InstructionTestCase(
        name="SRA A - shift right to zero",
        opcode=0x2F,  # CB prefix + 0x2F
        setup=[
            RegisterValue(Register.A, 0x01),  # 0b00000001 (sign bit clear)
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # 0b00000000 (shift right)
            FlagValue(Flag.ZERO, True),  # Zero result
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out from original bit 0
        ],
        description="Shift A right arithmetic to zero",
        cycles=2,
    ),
    # SRL Operations - shift right logical
    InstructionTestCase(
        name="RLC A - rotate left circular",
        opcode=0x07,  # CB prefix + 0x07
        setup=[
            RegisterValue(Register.A, 0x85),  # 0b10000101
        ],
        expected=[
            RegisterValue(
                Register.A, 0x0B
            ),  # 0b00001011 (rotated left, bit 7 -> carry)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out = original bit 7
        ],
        description="Rotate A left circular with carry out",
        cycles=2,
    ),
    InstructionTestCase(
        name="RLC A - rotate left to zero",
        opcode=0x07,  # CB prefix + 0x07
        setup=[
            RegisterValue(Register.A, 0x80),  # 0b10000000
        ],
        expected=[
            RegisterValue(Register.A, 0x01),  # 0b00000001 (rotated left)
            FlagValue(Flag.ZERO, False),  # Result is 0x01, not zero
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out from bit 7
        ],
        description="Rotate A left with carry out",
        cycles=2,
    ),
    InstructionTestCase(
        name="SRL A - shift right logical to zero",
        opcode=0x3F,  # CB prefix + 0x3F
        setup=[
            RegisterValue(Register.A, 0x01),  # 0b00000001
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # 0b00000000 (shifted right)
            FlagValue(Flag.ZERO, True),  # Zero result
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out from original bit 0
        ],
        description="Shift A right logical to zero",
        cycles=2,
    ),
]


# 8-Bit ADD Arithmetic Test Cases - Comprehensive flag testing
ADD_ARITHMETIC_CASES = [
    # Basic ADD operations
    InstructionTestCase(
        name="ADD A,B - normal case",
        opcode=0x80,
        setup=[RegisterValue(Register.A, 0x10), RegisterValue(Register.B, 0x20)],
        expected=[
            RegisterValue(Register.A, 0x30),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add B to A without overflow",
        cycles=1,
    ),
    InstructionTestCase(
        name="ADD A,B - zero result",
        opcode=0x80,
        setup=[RegisterValue(Register.A, 0xFF), RegisterValue(Register.B, 0x01)],
        expected=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, True),
        ],
        description="Add B to A resulting in zero",
        cycles=1,
    ),
    InstructionTestCase(
        name="ADD A,C - half carry only",
        opcode=0x81,
        setup=[RegisterValue(Register.A, 0x0F), RegisterValue(Register.C, 0x01)],
        expected=[
            RegisterValue(Register.A, 0x10),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add C to A with half carry",
        cycles=1,
    ),
    InstructionTestCase(
        name="ADD A,D - carry only",
        opcode=0x82,
        setup=[RegisterValue(Register.A, 0xF0), RegisterValue(Register.D, 0x20)],
        expected=[
            RegisterValue(Register.A, 0x10),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),
        ],
        description="Add D to A with carry",
        cycles=1,
    ),
    InstructionTestCase(
        name="ADD A,E - both half carry and carry",
        opcode=0x83,
        setup=[RegisterValue(Register.A, 0x8F), RegisterValue(Register.E, 0x81)],
        expected=[
            RegisterValue(Register.A, 0x10),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, True),
        ],
        description="Add E to A with both half carry and carry",
        cycles=1,
    ),
    InstructionTestCase(
        name="ADD A,A - double",
        opcode=0x87,
        setup=[RegisterValue(Register.A, 0x40)],
        expected=[
            RegisterValue(Register.A, 0x80),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add A to itself",
        cycles=1,
    ),
    InstructionTestCase(
        name="ADD A,A - overflow to zero",
        opcode=0x87,
        setup=[RegisterValue(Register.A, 0x80)],
        expected=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),  # Fixed: 0x8 + 0x8 = 0x10, no half carry
            FlagValue(Flag.CARRY, True),
        ],
        description="Add A to itself with overflow",
        cycles=1,
    ),
]

# SUB Arithmetic Test Cases
SUB_ARITHMETIC_CASES = [
    InstructionTestCase(
        name="SUB A,B - normal case",
        opcode=0x90,
        setup=[RegisterValue(Register.A, 0x30), RegisterValue(Register.B, 0x10)],
        expected=[
            RegisterValue(Register.A, 0x20),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Subtract B from A without borrow",
        cycles=1,
    ),
    InstructionTestCase(
        name="SUB A,C - zero result",
        opcode=0x91,
        setup=[RegisterValue(Register.A, 0x55), RegisterValue(Register.C, 0x55)],
        expected=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Subtract C from A resulting in zero",
        cycles=1,
    ),
    InstructionTestCase(
        name="SUB A,D - with borrow",
        opcode=0x92,
        setup=[RegisterValue(Register.A, 0x10), RegisterValue(Register.D, 0x20)],
        expected=[
            RegisterValue(Register.A, 0xF0),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(
                Flag.HALF_CARRY, False
            ),  # Fixed: 0x10 - 0x20 = 0xF0, no half carry
            FlagValue(Flag.CARRY, True),
        ],
        description="Subtract D from A with borrow",
        cycles=1,
    ),
    InstructionTestCase(
        name="SUB A,A - clear A",
        opcode=0x97,
        setup=[RegisterValue(Register.A, 0xFF)],
        expected=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Subtract A from itself",
        cycles=1,
    ),
]

# INC/DEC Test Cases
INC_DEC_CASES = [
    InstructionTestCase(
        name="INC A - normal",
        opcode=0x3C,
        setup=[RegisterValue(Register.A, 0x10)],
        expected=[
            RegisterValue(Register.A, 0x11),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="Increment A normally",
        cycles=1,
    ),
    InstructionTestCase(
        name="INC B - to zero",
        opcode=0x04,
        setup=[RegisterValue(Register.B, 0xFF)],
        expected=[
            RegisterValue(Register.B, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="Increment B with overflow to zero",
        cycles=1,
    ),
    InstructionTestCase(
        name="DEC C - normal",
        opcode=0x0D,
        setup=[RegisterValue(Register.C, 0x20)],
        expected=[
            RegisterValue(Register.C, 0x1F),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(
                Flag.HALF_CARRY, True
            ),  # Fixed: 0x20 - 0x01 = 0x1F, half carry occurs
        ],
        description="Decrement C normally",
        cycles=1,
    ),
    InstructionTestCase(
        name="DEC D - to zero",
        opcode=0x15,
        setup=[RegisterValue(Register.D, 0x01)],
        expected=[
            RegisterValue(Register.D, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="Decrement D to zero",
        cycles=1,
    ),
    InstructionTestCase(
        name="DEC E - with borrow",
        opcode=0x1D,
        setup=[RegisterValue(Register.E, 0x00)],
        expected=[
            RegisterValue(Register.E, 0xFF),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="Decrement E with borrow",
        cycles=1,
    ),
]

# Logical Operations Test Cases (AND, OR, XOR)
LOGICAL_OPERATIONS_CASES = [
    # AND Operations
    InstructionTestCase(
        name="AND A,B - normal case",
        opcode=0xA0,
        setup=[RegisterValue(Register.A, 0xF0), RegisterValue(Register.B, 0x0F)],
        expected=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),  # AND clears SUB
            FlagValue(Flag.HALF_CARRY, True),  # AND sets half carry
            FlagValue(Flag.CARRY, False),  # AND clears carry
        ],
        description="AND B with A - complementary bits",
        cycles=1,
    ),
    InstructionTestCase(
        name="AND A,C - same bits",
        opcode=0xA1,
        setup=[RegisterValue(Register.A, 0x55), RegisterValue(Register.C, 0x55)],
        expected=[
            RegisterValue(Register.A, 0x55),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, False),
        ],
        description="AND C with A - same bit pattern",
        cycles=1,
    ),
    InstructionTestCase(
        name="AND A,A - clear A",
        opcode=0xA7,
        setup=[RegisterValue(Register.A, 0xFF)],
        expected=[
            RegisterValue(Register.A, 0xFF),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, False),
        ],
        description="AND A with itself - identity",
        cycles=1,
    ),
    # OR Operations
    InstructionTestCase(
        name="OR A,B - complementary bits",
        opcode=0xB0,
        setup=[RegisterValue(Register.A, 0xF0), RegisterValue(Register.B, 0x0F)],
        expected=[
            RegisterValue(Register.A, 0xFF),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),  # OR clears SUB
            FlagValue(Flag.HALF_CARRY, False),  # OR clears half carry
            FlagValue(Flag.CARRY, False),  # OR clears carry
        ],
        description="OR B with A - complementary bits",
        cycles=1,
    ),
    InstructionTestCase(
        name="OR A,C - same zero bits",
        opcode=0xB1,
        setup=[RegisterValue(Register.A, 0x00), RegisterValue(Register.C, 0x00)],
        expected=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="OR C with A - both zero",
        cycles=1,
    ),
    InstructionTestCase(
        name="OR A,A - identity",
        opcode=0xB7,
        setup=[RegisterValue(Register.A, 0x55)],
        expected=[
            RegisterValue(Register.A, 0x55),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="OR A with itself - identity",
        cycles=1,
    ),
    # XOR Operations
    InstructionTestCase(
        name="XOR A,B - same bits",
        opcode=0xA8,
        setup=[RegisterValue(Register.A, 0x55), RegisterValue(Register.B, 0x55)],
        expected=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),  # XOR clears SUB
            FlagValue(Flag.HALF_CARRY, False),  # XOR clears half carry
            FlagValue(Flag.CARRY, False),  # XOR clears carry
        ],
        description="XOR B with A - same pattern results in zero",
        cycles=1,
    ),
    InstructionTestCase(
        name="XOR A,C - complementary bits",
        opcode=0xA9,
        setup=[RegisterValue(Register.A, 0xFF), RegisterValue(Register.C, 0x00)],
        expected=[
            RegisterValue(Register.A, 0xFF),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="XOR C with A - complementary bits",
        cycles=1,
    ),
    InstructionTestCase(
        name="XOR A,A - clear A",
        opcode=0xAF,
        setup=[RegisterValue(Register.A, 0x8F)],
        expected=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="XOR A with itself - clears A",
        cycles=1,
    ),
]

# CP (Compare) Operations Test Cases
CP_OPERATIONS_CASES = [
    InstructionTestCase(
        name="CP A,B - equal",
        opcode=0xB8,
        setup=[RegisterValue(Register.A, 0x55), RegisterValue(Register.B, 0x55)],
        expected=[
            RegisterValue(Register.A, 0x55),  # A unchanged
            FlagValue(Flag.ZERO, True),  # A == B
            FlagValue(Flag.SUB, True),  # CP sets SUB
            FlagValue(Flag.HALF_CARRY, False),  # 0x55 - 0x55 = 0, no half carry
            FlagValue(Flag.CARRY, False),  # No borrow needed
        ],
        description="Compare A with B - equal values",
        cycles=1,
    ),
    InstructionTestCase(
        name="CP A,C - A less than C",
        opcode=0xB9,
        setup=[RegisterValue(Register.A, 0x10), RegisterValue(Register.C, 0x20)],
        expected=[
            RegisterValue(Register.A, 0x10),  # A unchanged
            FlagValue(Flag.ZERO, False),  # A != C
            FlagValue(Flag.SUB, True),  # CP sets SUB
            FlagValue(Flag.HALF_CARRY, False),  # 0x10 - 0x20, no half carry
            FlagValue(Flag.CARRY, True),  # Borrow needed
        ],
        description="Compare A with C - A less than C",
        cycles=1,
    ),
    InstructionTestCase(
        name="CP A,D - A greater than D",
        opcode=0xBA,
        setup=[RegisterValue(Register.A, 0x80), RegisterValue(Register.D, 0x40)],
        expected=[
            RegisterValue(Register.A, 0x80),  # A unchanged
            FlagValue(Flag.ZERO, False),  # A != D
            FlagValue(Flag.SUB, True),  # CP sets SUB
            FlagValue(
                Flag.HALF_CARRY, False
            ),  # Fixed: 0x80 - 0x40 = 0x40, no half carry
            FlagValue(Flag.CARRY, False),  # No borrow needed
        ],
        description="Compare A with D - A greater than D",
        cycles=1,
    ),
    InstructionTestCase(
        name="CP A,A - always zero",
        opcode=0xBF,
        setup=[RegisterValue(Register.A, 0xFF)],
        expected=[
            RegisterValue(Register.A, 0xFF),  # A unchanged
            FlagValue(Flag.ZERO, True),  # A == A
            FlagValue(Flag.SUB, True),  # CP sets SUB
            FlagValue(
                Flag.HALF_CARRY, False
            ),  # No half carry when subtracting from self
            FlagValue(Flag.CARRY, False),  # No borrow needed
        ],
        description="Compare A with itself",
        cycles=1,
    ),
]

# ADC (Add with Carry) Operations Test Cases
ADC_OPERATIONS_CASES = [
    InstructionTestCase(
        name="ADC A,B - no carry",
        opcode=0x88,
        setup=[
            RegisterValue(Register.A, 0x10),
            RegisterValue(Register.B, 0x20),
            FlagValue(Flag.CARRY, False),
        ],
        expected=[
            RegisterValue(Register.A, 0x30),  # 0x10 + 0x20 + 0
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add B to A with carry - carry flag clear",
        cycles=1,
    ),
    InstructionTestCase(
        name="ADC A,C - with carry",
        opcode=0x89,
        setup=[
            RegisterValue(Register.A, 0x10),
            RegisterValue(Register.C, 0x20),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x31),  # 0x10 + 0x20 + 1
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add C to A with carry - carry flag set",
        cycles=1,
    ),
    InstructionTestCase(
        name="ADC A,D - overflow with carry",
        opcode=0x8A,
        setup=[
            RegisterValue(Register.A, 0xFE),
            RegisterValue(Register.D, 0x01),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # 0xFE + 0x01 + 1 = 0x100
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),  # 0xE + 0x1 + 1 = 0x10, half carry
            FlagValue(Flag.CARRY, True),  # Overflow
        ],
        description="Add D to A with carry - overflow",
        cycles=1,
    ),
]

# SBC (Subtract with Carry/Borrow) Operations Test Cases
SBC_OPERATIONS_CASES = [
    InstructionTestCase(
        name="SBC A,B - no borrow",
        opcode=0x98,
        setup=[
            RegisterValue(Register.A, 0x30),
            RegisterValue(Register.B, 0x10),
            FlagValue(Flag.CARRY, False),
        ],
        expected=[
            RegisterValue(Register.A, 0x20),  # 0x30 - 0x10 - 0
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Subtract B from A with borrow - no borrow",
        cycles=1,
    ),
    InstructionTestCase(
        name="SBC A,C - with borrow",
        opcode=0x99,
        setup=[
            RegisterValue(Register.A, 0x30),
            RegisterValue(Register.C, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x1F),  # 0x30 - 0x10 - 1
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),  # SBC sets SUB
            FlagValue(Flag.HALF_CARRY, True),  # Fixed: borrow from bit 4 (0 < 0+1)
            FlagValue(Flag.CARRY, False),  # No borrow: (0x10+1) <= 0x30
        ],
        description="Subtract C from A with borrow - borrow flag set",
        cycles=1,
    ),
    InstructionTestCase(
        name="SBC A,D - with borrow overflow",
        opcode=0x9A,
        setup=[
            RegisterValue(Register.A, 0x10),
            RegisterValue(Register.D, 0x20),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0xEF),  # 0x10 - 0x20 - 1 = 0xEF
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),  # SBC sets SUB
            FlagValue(Flag.HALF_CARRY, True),  # Half carry occurs
            FlagValue(Flag.CARRY, True),  # Borrow needed
        ],
        description="Subtract D from A with borrow - borrow needed",
        cycles=1,
    ),
]

# Memory LD Operations Test Cases
MEMORY_LD_CASES = [
    InstructionTestCase(
        name="LD A,[HL] - load from memory",
        opcode=0x7E,
        setup=[
            RegisterValue(Register.HL, 0xC000),
            RegisterValue(Register.A, 0x00),  # Initial A value
            MemoryValue(0xC000, 0x42),  # Memory content
        ],
        expected=[
            RegisterValue(Register.A, 0x42),  # A should have loaded from memory
        ],
        description="Load A from memory location pointed by HL",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD [HL],A - store to memory",
        opcode=0x77,
        setup=[
            RegisterValue(Register.HL, 0xC001),
            RegisterValue(Register.A, 0x55),  # A value to store
            MemoryValue(0xC001, 0x00),  # Initial memory content
        ],
        expected=[
            MemoryValue(0xC001, 0x55),  # Memory should have A's value
        ],
        description="Store A to memory location pointed by HL",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD B,[HL] - load from memory",
        opcode=0x46,
        setup=[
            RegisterValue(Register.HL, 0xC002),
            RegisterValue(Register.B, 0x00),  # Initial B value
            MemoryValue(0xC002, 0x33),  # Memory content
        ],
        expected=[
            RegisterValue(Register.B, 0x33),  # B should have loaded from memory
        ],
        description="Load B from memory location pointed by HL",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD [HL],C - store to memory",
        opcode=0x71,
        setup=[
            RegisterValue(Register.HL, 0xC003),
            RegisterValue(Register.C, 0x77),  # C value to store
            MemoryValue(0xC003, 0x00),  # Initial memory content
        ],
        expected=[
            MemoryValue(0xC003, 0x77),  # Memory should have C's value
        ],
        description="Store C to memory location pointed by HL",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD [HL],D - complex memory operation",
        opcode=0x72,
        setup=[
            RegisterValue(Register.HL, 0xC004),
            RegisterValue(Register.D, 0x99),  # D value to store
            MemoryValue(0xC004, 0xAA),  # Initial memory content
            FlagValue(Flag.ZERO, True),  # Flags should be preserved
            FlagValue(Flag.CARRY, False),
        ],
        expected=[
            MemoryValue(0xC004, 0x99),  # Memory should have D's value
        ],
        description="Store D to memory with flag preservation",
        cycles=2,
    ),
]

# Bit Operations Test Cases (BIT, SET, RES)
BIT_OPERATIONS_CASES = [
    # BIT Operations - test bits and set flags
    InstructionTestCase(
        name="BIT 0,A - test bit 0",
        opcode=0x47,  # CB prefix + 0x47
        setup=[
            RegisterValue(Register.A, 0x01),  # Bit 0 is set
        ],
        expected=[
            RegisterValue(Register.A, 0x01),  # A unchanged
            FlagValue(Flag.ZERO, False),  # Bit is set, so Z=0
            FlagValue(Flag.SUB, False),  # BIT clears SUB
            FlagValue(Flag.HALF_CARRY, True),  # BIT sets half carry
        ],
        description="Test bit 0 in A - bit is set",
        cycles=2,
    ),
    InstructionTestCase(
        name="BIT 1,B - test bit 1 not set",
        opcode=0x50,  # CB prefix + 0x50
        setup=[
            RegisterValue(Register.B, 0x01),  # Bit 1 is not set (0b00000001)
        ],
        expected=[
            RegisterValue(Register.B, 0x01),  # B unchanged
            FlagValue(Flag.ZERO, True),  # Bit is not set, so Z=1
            FlagValue(Flag.SUB, False),  # BIT clears SUB
            FlagValue(Flag.HALF_CARRY, True),  # BIT sets half carry
        ],
        description="Test bit 1 in B - bit is not set",
        cycles=2,
    ),
    InstructionTestCase(
        name="BIT 7,H - test highest bit",
        opcode=0x7C,  # CB prefix + 0x7C
        setup=[
            RegisterValue(Register.H, 0x80),  # Bit 7 is set
        ],
        expected=[
            RegisterValue(Register.H, 0x80),  # H unchanged
            FlagValue(Flag.ZERO, False),  # Bit is set, so Z=0
            FlagValue(Flag.SUB, False),  # BIT clears SUB
            FlagValue(Flag.HALF_CARRY, True),  # BIT sets half carry
        ],
        description="Test bit 7 in H - highest bit is set",
        cycles=2,
    ),
    # SET Operations - set bits, no flags affected
    InstructionTestCase(
        name="SET 2,C - set bit 2",
        opcode=0xD1,  # CB prefix + 0xD1 (correct opcode for SET 2,C)
        setup=[
            RegisterValue(Register.C, 0x01),  # 0b00000001
            FlagValue(Flag.ZERO, True),  # Flags should be preserved
            FlagValue(Flag.CARRY, False),
        ],
        expected=[
            RegisterValue(Register.C, 0x05),  # 0b00000101 (bit 2 set)
        ],
        description="Set bit 2 in C",
        cycles=2,
    ),
    InstructionTestCase(
        name="SET 5,D - set already set bit",
        opcode=0xEA,  # CB prefix + 0xEA
        setup=[
            RegisterValue(Register.D, 0x20),  # Bit 5 already set
        ],
        expected=[
            RegisterValue(Register.D, 0x20),  # Should remain the same
        ],
        description="Set bit 5 in D - already set",
        cycles=2,
    ),
    InstructionTestCase(
        name="SET 7,E - set highest bit",
        opcode=0xFB,  # CB prefix + 0xFB
        setup=[
            RegisterValue(Register.E, 0x7F),  # All bits except 7 set
        ],
        expected=[
            RegisterValue(Register.E, 0xFF),  # Should set bit 7
        ],
        description="Set bit 7 in E - highest bit",
        cycles=2,
    ),
    # RES Operations - reset bits, no flags affected
    InstructionTestCase(
        name="RES 0,A - reset bit 0",
        opcode=0x87,  # CB prefix + 0x87 (correct opcode)
        setup=[
            RegisterValue(Register.A, 0xFF),  # All bits set
        ],
        expected=[
            RegisterValue(Register.A, 0xFE),  # 0b11111110 (bit 0 cleared)
        ],
        description="Reset bit 0 in A",
        cycles=2,
    ),
    InstructionTestCase(
        name="RES 4,B - reset middle bit",
        opcode=0xA0,  # CB prefix + 0xA0
        setup=[
            RegisterValue(Register.B, 0xFF),  # All bits set
        ],
        expected=[
            RegisterValue(Register.B, 0xEF),  # 0b11101111 (bit 4 cleared)
        ],
        description="Reset bit 4 in B",
        cycles=2,
    ),
    InstructionTestCase(
        name="RES 7,C - reset already cleared bit",
        opcode=0xB9,  # CB prefix + 0xB9 (correct opcode for RES 7,C)
        setup=[
            RegisterValue(Register.C, 0x7F),  # Bit 7 already cleared
        ],
        expected=[
            RegisterValue(Register.C, 0x7F),  # Should remain same
        ],
        description="Reset bit 7 in C - already cleared",
        cycles=2,
    ),
]

# Edge case tests for LD instructions - Boundary values and flag preservation
LD_EDGE_CASES = [
    InstructionTestCase(
        name="LD A,B - max value",
        opcode=0x78,
        setup=[
            RegisterValue(Register.B, 0xFF),
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0xFF),
            FlagValue(Flag.ZERO, True),  # Flags should be preserved
            FlagValue(Flag.CARRY, True),
        ],
        description="Load max value with flag preservation",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD A,B - zero value",
        opcode=0x78,
        setup=[
            RegisterValue(Register.B, 0x00),
            RegisterValue(Register.A, 0xFF),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, False),  # Flags should be preserved
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="Load zero value with flag preservation",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD H,L - high bit patterns",
        opcode=0x6C,
        setup=[
            RegisterValue(Register.H, 0x80),  # High bit set
            RegisterValue(Register.L, 0x7F),  # High bit clear
        ],
        expected=[
            RegisterValue(Register.L, 0x80),
        ],
        description="Test high bit pattern transfer",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD C,D - alternating pattern",
        opcode=0x4A,
        setup=[
            RegisterValue(Register.C, 0x55),  # 01010101
            RegisterValue(Register.D, 0xAA),  # 10101010
        ],
        expected=[
            RegisterValue(Register.C, 0xAA),
        ],
        description="Test alternating bit pattern transfer",
        cycles=1,
    ),
]


@pytest.fixture
def cpu():
    """Create fresh CPU instance for each test."""
    cpu = Z80()
    cpu.Reset()
    return cpu


@pytest.mark.parametrize("test_case", LD_REGISTER_CASES)
def test_ld_register_instructions(cpu, test_case):
    """Test 8-bit load register instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", ADD_ARITHMETIC_CASES)
def test_add_arithmetic_instructions(cpu, test_case):
    """Test 8-bit add arithmetic instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", SUB_ARITHMETIC_CASES)
def test_sub_arithmetic_instructions(cpu, test_case):
    """Test 8-bit sub arithmetic instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", INC_DEC_CASES)
def test_inc_dec_instructions(cpu, test_case):
    """Test 8-bit inc/dec instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", LOGICAL_OPERATIONS_CASES)
def test_logical_operations(cpu, test_case):
    """Test logical operations instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", CP_OPERATIONS_CASES)
def test_cp_operations(cpu, test_case):
    """Test compare operations instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", ADC_OPERATIONS_CASES)
def test_adc_operations(cpu, test_case):
    """Test ADC operations instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", SBC_OPERATIONS_CASES)
def test_sbc_operations(cpu, test_case):
    """Test SBC operations instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", MEMORY_LD_CASES)
def test_memory_ld_operations(cpu, test_case):
    """Test memory LD operations instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", BIT_OPERATIONS_CASES)
def test_bit_operations(cpu, test_case):
    """Test bit operations instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction (CB-prefixed opcodes need special handling)
    initial_pc = cpu._PC.value

    # Write the CB prefix and opcode to memory, then execute from PC
    cpu._mem.wb(initial_pc, 0xCB)
    cpu._mem.wb(initial_pc + 1, test_case.opcode & 0xFF)
    cpu._PC.value += 2  # Skip to after the CB opcode

    # Execute the CB opcode directly (it should execute what we just wrote)
    cb_method = getattr(cpu, f"OPCode_CB{test_case.opcode & 0xFF:02X}")
    if cb_method:
        cb_method()

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", ROTATION_SHIFT_CASES)
def test_rotation_shift_operations(cpu, test_case):
    """Test rotation/shift operation: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction (CB-prefixed opcodes need special handling)
    initial_pc = cpu._PC.value

    # Write the CB prefix and opcode to memory, then execute from PC
    cpu._mem.wb(initial_pc, 0xCB)
    cpu._mem.wb(initial_pc + 1, test_case.opcode & 0xFF)
    cpu._PC.value += 2  # Skip to after the CB opcode

    # Execute the CB opcode directly (it should execute what we just wrote)
    cb_method = getattr(cpu, f"OPCode_CB{test_case.opcode & 0xFF:02X}")
    if cb_method:
        cb_method()

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", LD_EDGE_CASES)
def test_ld_edge_cases(cpu, test_case):
    """Test LD register edge cases: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


if __name__ == "__main__":
    # Quick test runner for development
    pytest.main([__file__, "-v"])

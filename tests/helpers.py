"""
Shared test infrastructure for Z80 instruction tests.

This module provides unified test cases for all Z80 CPU instructions with:
- Type-safe register and flag access using enums
- Memory value operations with typed objects
- Expected state verification in single unified approach
- Quick feedback for initial instruction validation
"""

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
    STOP = "STOP"
    HALT = "HALT"


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
        Flag.STOP: lambda cpu: cpu._stop,
        Flag.HALT: lambda cpu: cpu._halt,
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
        Flag.STOP: lambda cpu, val: setattr(cpu, "_stop", val),
        Flag.HALT: lambda cpu, val: setattr(cpu, "_halt", val),
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
                new_flags = CPUStateValidator.FLAG_SETTERS[item.flag](cpu, item.value)
                cpu._AF.low = new_flags

    @staticmethod
    def verify_state(
        cpu: Z80, expected_list: List[Union[RegisterValue, MemoryValue, FlagValue]]
    ) -> tuple[bool, str]:
        """Verify CPU state including expected flag values. Returns (success, error_message)."""
        errors = []
        for item in expected_list:
            if isinstance(item, RegisterValue):
                actual = CPUStateValidator.REGISTER_GETTERS[item.register](cpu)
                if actual != item.value:
                    errors.append(
                        f"Register {item.register}: expected 0x{item.value:02X}, got 0x{actual:02X}"
                    )
            elif isinstance(item, MemoryValue):
                actual = cpu._mem.rb(item.address)
                if actual != item.value:
                    errors.append(
                        f"Memory 0x{item.address:04X}: expected 0x{item.value:02X}, got 0x{actual:02X}"
                    )
            elif isinstance(item, FlagValue):
                actual = CPUStateValidator.FLAG_GETTERS[item.flag](cpu)
                if actual != item.value:
                    errors.append(
                        f"Flag {item.flag}: expected {item.value}, got {actual}"
                    )
            else:
                raise TypeError(f"Unknown expected type: {type(item)}")

        return (len(errors) == 0, "; ".join(errors) if errors else "")

    @staticmethod
    def execute_instruction(cpu: Z80, opcode: int):
        """Execute single instruction and handle PC increment."""
        # Store initial PC for instruction fetch
        initial_pc = cpu._PC.value

        # Execute the instruction (it should handle its own PC increment)
        cpu._opmap[opcode]()

        # If PC didn't change during instruction execution, increment by 1
        # This handles single-byte instructions that don't increment PC themselves
        if cpu._PC.value == initial_pc:
            cpu._PC.value += 1

    @staticmethod
    def assert_state(cpu: Z80, test_case: InstructionTestCase):
        """Unified assertion for registers, memory, and flags."""
        # Verify expected state
        success, error_msg = CPUStateValidator.verify_state(cpu, test_case.expected)
        assert success, f"{test_case.name} failed: {error_msg}"

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

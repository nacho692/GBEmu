import pytest
from helpers import (
    Register, Flag,
    RegisterValue, MemoryValue, FlagValue,
    InstructionTestCase, CPUStateValidator,
)

# Miscellaneous Operations Test Cases (STOP, HALT, etc.)
MISCELLANEOUS_OPERATIONS_CASES = [
    InstructionTestCase(
        name="STOP - CPU stop with proper 0x00 suffix",
        opcode=0x10,
        setup=[
            RegisterValue(Register.PC, 0xC000),  # Set PC to a test location
            MemoryValue(0xC001, 0x00),  # STOP requires 0x00 as next byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xC002),  # PC should advance past both bytes
            FlagValue(Flag.STOP, True),  # STOP flag should be set
        ],
        description="STOP instruction halts CPU until button press",
        cycles=4,
    ),
]

# I/O and Interrupt Control Test Cases
IO_INTERRUPT_CASES = [
    # LDH (n),A (0xE0) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="LDH (n),A - store to I/O port",
        opcode=0xE0,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.A, 0x42),
            MemoryValue(0xC000, 0x10),  # Port address 0x10
        ],
        expected=[
            RegisterValue(Register.PC, 0xC001),
            MemoryValue(0xFF10, 0x42),  # A stored at 0xFF00 + 0x10
        ],
        description="Store A to I/O port at 0xFF00 + n",
        cycles=3,
    ),
    # LD (C),A (0xE2) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD (C),A - store to I/O port via C",
        opcode=0xE2,
        setup=[
            RegisterValue(Register.A, 0x55),
            RegisterValue(Register.C, 0x20),
        ],
        expected=[
            MemoryValue(0xFF20, 0x55),  # A stored at 0xFF00 + C
        ],
        description="Store A to I/O port at 0xFF00 + C",
        cycles=2,
    ),
    # LDH A,(n) (0xF0) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="LDH A,(n) - load from I/O port",
        opcode=0xF0,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.A, 0x00),  # Initial A value
            MemoryValue(0xC000, 0x15),  # Port address 0x15
            MemoryValue(0xFF15, 0x7A),  # Port data
        ],
        expected=[
            RegisterValue(Register.PC, 0xC001),
            RegisterValue(Register.A, 0x7A),  # A loaded from port
        ],
        description="Load A from I/O port at 0xFF00 + n",
        cycles=3,
    ),
    # LD A,(C) (0xF2) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD A,(C) - load from I/O port via C",
        opcode=0xF2,
        setup=[
            RegisterValue(Register.A, 0x00),  # Initial A value
            RegisterValue(Register.C, 0x25),
            MemoryValue(0xFF25, 0x33),  # Port data
        ],
        expected=[
            RegisterValue(Register.A, 0x33),  # A loaded from port
        ],
        description="Load A from I/O port at 0xFF00 + C",
        cycles=2,
    ),
    # DI (0xF3) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="DI - disable interrupts",
        opcode=0xF3,
        setup=[
            # Start with interrupts enabled
        ],
        expected=[
            # IME should be disabled (this would need to be verified in implementation)
        ],
        description="Disable interrupts",
        cycles=1,
    ),
]

# Additional missing opcode test cases
MISSING_OPCODE_CASES = [
    # LD A,(DE) (0x1A) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD A,(DE) - load from memory via DE",
        opcode=0x1A,
        setup=[
            RegisterValue(Register.DE, 0xC000),
            RegisterValue(Register.A, 0x00),  # Initial A value
            MemoryValue(0xC000, 0x42),
        ],
        expected=[
            RegisterValue(Register.A, 0x42),
        ],
        description="Load A from memory location pointed by DE",
        cycles=2,
    ),
    # LD (DE),A (0x12) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD (DE),A - store A to memory via DE",
        opcode=0x12,
        setup=[
            RegisterValue(Register.DE, 0xC001),
            RegisterValue(Register.A, 0x55),
            MemoryValue(0xC001, 0x00),
        ],
        expected=[
            MemoryValue(0xC001, 0x55),
        ],
        description="Store A to memory location pointed by DE",
        cycles=2,
    ),
    # LD A,(BC) (0x0A) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD A,(BC) - load from memory via BC",
        opcode=0x0A,
        setup=[
            RegisterValue(Register.BC, 0xC002),
            RegisterValue(Register.A, 0x00),  # Initial A value
            MemoryValue(0xC002, 0x33),
        ],
        expected=[
            RegisterValue(Register.A, 0x33),
        ],
        description="Load A from memory location pointed by BC",
        cycles=2,
    ),
    # LD (BC),A (0x02) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD (BC),A - store A to memory via BC",
        opcode=0x02,
        setup=[
            RegisterValue(Register.BC, 0xC003),
            RegisterValue(Register.A, 0x77),
            MemoryValue(0xC003, 0x00),
        ],
        expected=[
            MemoryValue(0xC003, 0x77),
        ],
        description="Store A to memory location pointed by BC",
        cycles=2,
    ),
    # INC (HL) (0x34) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="INC (HL) - increment memory value",
        opcode=0x34,
        setup=[
            RegisterValue(Register.HL, 0xC100),
            MemoryValue(0xC100, 0x10),
        ],
        expected=[
            MemoryValue(0xC100, 0x11),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="Increment memory value at HL",
        cycles=3,
    ),
    InstructionTestCase(
        name="INC (HL) - increment memory with overflow to zero",
        opcode=0x34,
        setup=[
            RegisterValue(Register.HL, 0xC101),
            MemoryValue(0xC101, 0xFF),
        ],
        expected=[
            MemoryValue(0xC101, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="Increment memory value with overflow",
        cycles=3,
    ),
    # DEC (HL) (0x35) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="DEC (HL) - decrement memory value",
        opcode=0x35,
        setup=[
            RegisterValue(Register.HL, 0xC102),
            MemoryValue(0xC102, 0x20),
        ],
        expected=[
            MemoryValue(0xC102, 0x1F),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="Decrement memory value at HL",
        cycles=3,
    ),
    InstructionTestCase(
        name="DEC (HL) - decrement memory to zero",
        opcode=0x35,
        setup=[
            RegisterValue(Register.HL, 0xC103),
            MemoryValue(0xC103, 0x01),
        ],
        expected=[
            MemoryValue(0xC103, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="Decrement memory value to zero",
        cycles=3,
    ),
    # LD A,(nn) (0xFA) - 16 cycles = 4 test cycles
    InstructionTestCase(
        name="LD A,(nn) - load from absolute address",
        opcode=0xFA,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.A, 0x00),
            MemoryValue(0xC000, 0x50),  # Low byte of address
            MemoryValue(0xC001, 0xC0),  # High byte (little-endian: 0xC050)
            MemoryValue(0xC050, 0x42),  # Value at target address
        ],
        expected=[
            RegisterValue(Register.A, 0x42),
            RegisterValue(Register.PC, 0xC002),  # PC advances by 2
        ],
        description="Load A from 16-bit absolute memory address",
        cycles=4,
    ),
    # LD (nn),A (0xEA) - 16 cycles = 4 test cycles
    InstructionTestCase(
        name="LD (nn),A - store to absolute address",
        opcode=0xEA,
        setup=[
            RegisterValue(Register.PC, 0xC010),
            RegisterValue(Register.A, 0x99),
            MemoryValue(0xC010, 0x50),  # Low byte of address
            MemoryValue(0xC011, 0xC0),  # High byte (little-endian: 0xC050)
            MemoryValue(0xC050, 0x00),  # Initial value at target
        ],
        expected=[
            MemoryValue(0xC050, 0x99),  # A stored to 0xC050
            RegisterValue(Register.PC, 0xC012),  # PC advances by 2
        ],
        description="Store A to 16-bit absolute memory address",
        cycles=4,
    ),
    # LD HL,SP+n (0xF8) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="LD HL,SP+n - positive offset",
        opcode=0xF8,
        setup=[
            RegisterValue(Register.PC, 0xC020),
            RegisterValue(Register.SP, 0x1000),
            MemoryValue(0xC020, 0x20),  # Offset
        ],
        expected=[
            RegisterValue(Register.HL, 0x1020),
            RegisterValue(Register.PC, 0xC021),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Load HL = SP + positive offset",
        cycles=3,
    ),
    InstructionTestCase(
        name="LD HL,SP+n - negative offset with flags",
        opcode=0xF8,
        setup=[
            RegisterValue(Register.PC, 0xC030),
            RegisterValue(Register.SP, 0x1000),
            MemoryValue(0xC030, 0xF0),  # -16 offset
        ],
        expected=[
            RegisterValue(Register.HL, 0x0FF0),
            RegisterValue(Register.PC, 0xC031),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),  # Half carry from borrowing
            FlagValue(Flag.CARRY, False),
        ],
        description="Load HL = SP + negative offset with half carry",
        cycles=3,
    ),
    # LD SP,HL (0xF9) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD SP,HL - copy HL to SP",
        opcode=0xF9,
        setup=[
            RegisterValue(Register.HL, 0xD123),
            RegisterValue(Register.SP, 0x0000),  # Initial SP value
        ],
        expected=[
            RegisterValue(Register.SP, 0xD123),
        ],
        description="Copy HL to stack pointer",
        cycles=2,
    ),
    # ADD SP,n (0xE8) - 16 cycles = 4 test cycles
    InstructionTestCase(
        name="ADD SP,n - positive offset",
        opcode=0xE8,
        setup=[
            RegisterValue(Register.PC, 0xC040),
            RegisterValue(Register.SP, 0xFFFE),
            MemoryValue(0xC040, 0x02),  # Offset
        ],
        expected=[
            RegisterValue(Register.SP, 0x0000),  # 0xFFFE + 0x02 = 0x10000, truncated
            RegisterValue(Register.PC, 0xC041),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, True),
        ],
        description="Add positive offset to SP with overflow",
        cycles=4,
    ),
    InstructionTestCase(
        name="ADD SP,n - negative offset",
        opcode=0xE8,
        setup=[
            RegisterValue(Register.PC, 0xC050),
            RegisterValue(Register.SP, 0x1000),
            MemoryValue(0xC050, 0xF8),  # -8 offset
        ],
        expected=[
            RegisterValue(Register.SP, 0x0FF8),  # 0x1000 + (-8) = 0x0FF8
            RegisterValue(Register.PC, 0xC051),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add negative offset to SP",
        cycles=4,
    ),
    # LD (nn),SP (0x08) - 20 cycles = 5 test cycles
    InstructionTestCase(
        name="LD (nn),SP - store SP to memory",
        opcode=0x08,
        setup=[
            RegisterValue(Register.PC, 0xC060),
            RegisterValue(Register.SP, 0xABCD),
            MemoryValue(0xC060, 0x00),  # Low byte of address
            MemoryValue(0xC061, 0xD0),  # High byte of address (0xD000)
            MemoryValue(0xD000, 0x00),  # Initial memory values
            MemoryValue(0xD001, 0x00),
        ],
        expected=[
            MemoryValue(0xD000, 0xCD),  # SP low byte stored
            MemoryValue(0xD001, 0xAB),  # SP high byte stored
            RegisterValue(Register.PC, 0xC062),
        ],
        description="Store SP to absolute memory address",
        cycles=5,
    ),
]

# HALT instruction test case
HALT_CASES = [
    # HALT (0x76) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="HALT - halt CPU",
        opcode=0x76,
        setup=[],
        expected=[
            FlagValue(Flag.HALT, True),
        ],
        description="Halt CPU until interrupt",
        cycles=1,
    ),
]

# Stack Operations - 8 opcodes
STACK_CASES = [
    # PUSH AF (0xF5) - 16 cycles = 4 test cycles
    InstructionTestCase(
        name="PUSH AF - push register pair to stack",
        opcode=0xF5,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.AF, 0x1234),  # A=0x12, F=0x34
            RegisterValue(Register.SP, 0xD000),
            MemoryValue(0xD000, 0x00),  # Stack initial
            MemoryValue(0xD001, 0x00),
        ],
        expected=[
            RegisterValue(Register.AF, 0x1234),  # AF unchanged
            RegisterValue(Register.SP, 0xCFFE),  # SP decremented by 2
            MemoryValue(0xCFFE, 0x34),  # F register (low byte) pushed first
            MemoryValue(0xCFFF, 0x12),  # A register (high byte) pushed second
        ],
        description="Push AF register pair to stack",
        cycles=4,
    ),
    # PUSH BC (0xC5) - 16 cycles = 4 test cycles
    InstructionTestCase(
        name="PUSH BC - push register pair to stack",
        opcode=0xC5,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.BC, 0x5678),  # B=0x56, C=0x78
            RegisterValue(Register.SP, 0xD010),
            MemoryValue(0xD010, 0x00),  # Stack initial
            MemoryValue(0xD011, 0x00),
        ],
        expected=[
            RegisterValue(Register.BC, 0x5678),  # BC unchanged
            RegisterValue(Register.SP, 0xD00E),  # SP decremented by 2
            MemoryValue(0xD00E, 0x78),  # C register (low byte) pushed first
            MemoryValue(0xD00F, 0x56),  # B register (high byte) pushed second
        ],
        description="Push BC register pair to stack",
        cycles=4,
    ),
    # PUSH DE (0xD5) - 16 cycles = 4 test cycles
    InstructionTestCase(
        name="PUSH DE - push register pair to stack",
        opcode=0xD5,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.DE, 0x9ABC),  # D=0x9A, E=0xBC
            RegisterValue(Register.SP, 0xD020),
            MemoryValue(0xD020, 0x00),  # Stack initial
            MemoryValue(0xD021, 0x00),
        ],
        expected=[
            RegisterValue(Register.DE, 0x9ABC),  # DE unchanged
            RegisterValue(Register.SP, 0xD01E),  # SP decremented by 2
            MemoryValue(0xD01E, 0xBC),  # E register (low byte) pushed first
            MemoryValue(0xD01F, 0x9A),  # D register (high byte) pushed second
        ],
        description="Push DE register pair to stack",
        cycles=4,
    ),
    # PUSH HL (0xE5) - 16 cycles = 4 test cycles
    InstructionTestCase(
        name="PUSH HL - push register pair to stack",
        opcode=0xE5,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.HL, 0xDEF0),  # H=0xDE, L=0xF0
            RegisterValue(Register.SP, 0xD030),
            MemoryValue(0xD030, 0x00),  # Stack initial
            MemoryValue(0xD031, 0x00),
        ],
        expected=[
            RegisterValue(Register.HL, 0xDEF0),  # HL unchanged
            RegisterValue(Register.SP, 0xD02E),  # SP decremented by 2
            MemoryValue(0xD02E, 0xF0),  # L register (low byte) pushed first
            MemoryValue(0xD02F, 0xDE),  # H register (high byte) pushed second
        ],
        description="Push HL register pair to stack",
        cycles=4,
    ),
    # POP AF (0xF1) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="POP AF - pop register pair from stack",
        opcode=0xF1,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.AF, 0x0000),  # AF initial value
            RegisterValue(Register.SP, 0xCFFE),
            MemoryValue(0xCFFE, 0x78),  # Stack data: F=0x78, A=0x56
            MemoryValue(0xCFFF, 0x56),
        ],
        expected=[
            RegisterValue(Register.AF, 0x5678),  # AF loaded from stack
            RegisterValue(Register.SP, 0xD000),  # SP incremented by 2
        ],
        description="Pop AF register pair from stack",
        cycles=3,
    ),
    # POP BC (0xC1) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="POP BC - pop register pair from stack",
        opcode=0xC1,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.BC, 0x0000),  # BC initial value
            RegisterValue(Register.SP, 0xCFFE),
            MemoryValue(0xCFFE, 0x34),  # Stack data: C=0x34, B=0x12
            MemoryValue(0xCFFF, 0x12),
        ],
        expected=[
            RegisterValue(Register.BC, 0x1234),  # BC loaded from stack
            RegisterValue(Register.SP, 0xD000),  # SP incremented by 2
        ],
        description="Pop BC register pair from stack",
        cycles=3,
    ),
    # POP DE (0xD1) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="POP DE - pop register pair from stack",
        opcode=0xD1,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.DE, 0x0000),  # DE initial value
            RegisterValue(Register.SP, 0xCFFE),
            MemoryValue(0xCFFE, 0xBC),  # Stack data: E=0xBC, D=0x9A
            MemoryValue(0xCFFF, 0x9A),
        ],
        expected=[
            RegisterValue(Register.DE, 0x9ABC),  # DE loaded from stack
            RegisterValue(Register.SP, 0xD000),  # SP incremented by 2
        ],
        description="Pop DE register pair from stack",
        cycles=3,
    ),
    # POP HL (0xE1) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="POP HL - pop register pair from stack",
        opcode=0xE1,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.HL, 0x0000),  # HL initial value
            RegisterValue(Register.SP, 0xCFFE),
            MemoryValue(0xCFFE, 0xF0),  # Stack data: L=0xF0, H=0xDE
            MemoryValue(0xCFFF, 0xDE),
        ],
        expected=[
            RegisterValue(Register.HL, 0xDEF0),  # HL loaded from stack
            RegisterValue(Register.SP, 0xD000),  # SP incremented by 2
        ],
        description="Pop HL register pair from stack",
        cycles=3,
    ),
]

# Missing Special/System Instructions
MISSING_SPECIAL_CASES = [
    InstructionTestCase(
        name="RLA - rotate left through carry",
        opcode=0x17,
        setup=[
            RegisterValue(Register.A, 0x80),  # 0b10000000
            FlagValue(Flag.CARRY, False),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # Bit 7 goes to carry, carry (0) goes to bit 0
            FlagValue(Flag.ZERO, False),  # RLA always resets Z on Game Boy
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Old bit 7
        ],
        description="Rotate A left through carry",
        cycles=1,
    ),
    InstructionTestCase(
        name="RLA - carry in to bit 0",
        opcode=0x17,
        setup=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x01),  # Carry goes to bit 0
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),  # Old bit 7 was 0
        ],
        description="Rotate A left through carry - carry in",
        cycles=1,
    ),
    InstructionTestCase(
        name="CPL - complement A",
        opcode=0x2F,
        setup=[
            RegisterValue(Register.A, 0x35),
        ],
        expected=[
            RegisterValue(Register.A, 0xCA),  # ~0x35 = 0xCA
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="Complement A (flip all bits)",
        cycles=1,
    ),
    InstructionTestCase(
        name="EI - enable interrupts",
        opcode=0xFB,
        setup=[],
        expected=[],
        description="Enable interrupts",
        cycles=1,
    ),
    InstructionTestCase(
        name="DAA - after addition BCD",
        opcode=0x27,
        setup=[
            RegisterValue(Register.A, 0x0A),  # Result of 5+5=10, needs BCD adjust
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        expected=[
            RegisterValue(Register.A, 0x10),  # BCD: 10
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="DAA after addition - adjust lower nibble",
        cycles=1,
    ),
    InstructionTestCase(
        name="DAA - after addition with half carry",
        opcode=0x27,
        setup=[
            RegisterValue(Register.A, 0x13),  # E.g., 0x19 + 0x0A = 0x23, with half carry
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, False),
        ],
        expected=[
            RegisterValue(Register.A, 0x19),  # 0x13 + 0x06 = 0x19
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="DAA after addition with half carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="DAA - zero result",
        opcode=0x27,
        setup=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="DAA - already zero",
        cycles=1,
    ),
]

# =============================================================================
# Final gap-filling tests for remaining uncovered lines
# =============================================================================

# --- Base rotation opcodes (0x07 RLCA, 0x0F RRCA, 0x17 RLA, 0x1F RRA) ---
# These are distinct from CB-prefixed rotations: they always clear Zero flag.
BASE_ROTATION_CASES = [
    InstructionTestCase(
        name="RLCA (0x07) - rotate left with carry",
        opcode=0x07,
        setup=[RegisterValue(Register.A, 0x85)],  # 10000101
        expected=[
            RegisterValue(Register.A, 0x0B),  # 00001011
            FlagValue(Flag.CARRY, True),  # bit 7 was set
            FlagValue(Flag.ZERO, False),  # always cleared
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="RLCA rotates A left through carry, always clears Zero",
        cycles=1,
    ),
    InstructionTestCase(
        name="RRCA (0x0F) - rotate right with carry",
        opcode=0x0F,
        setup=[RegisterValue(Register.A, 0x01)],  # 00000001
        expected=[
            RegisterValue(Register.A, 0x80),  # 10000000
            FlagValue(Flag.CARRY, True),  # bit 0 was set
            FlagValue(Flag.ZERO, False),  # always cleared
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="RRCA rotates A right through carry, always clears Zero",
        cycles=1,
    ),
    InstructionTestCase(
        name="RRA (0x1F) - rotate right through carry",
        opcode=0x1F,
        setup=[
            RegisterValue(Register.A, 0x01),  # 00000001
            FlagValue(Flag.CARRY, False),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # shifted right, carry_in=0
            FlagValue(Flag.CARRY, True),  # bit 0 was set
            FlagValue(Flag.ZERO, False),  # always cleared even though result is 0
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="RRA rotates A right through carry, always clears Zero",
        cycles=1,
    ),
]

# --- CCF (0x3F) and SCF (0x37) ---
CARRY_FLAG_CASES = [
    InstructionTestCase(
        name="CCF (0x3F) - complement carry (set to clear)",
        opcode=0x3F,
        setup=[FlagValue(Flag.CARRY, True)],
        expected=[
            FlagValue(Flag.CARRY, False),  # toggled
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="CCF toggles carry from set to clear",
        cycles=1,
    ),
    InstructionTestCase(
        name="CCF (0x3F) - complement carry (clear to set)",
        opcode=0x3F,
        setup=[FlagValue(Flag.CARRY, False)],
        expected=[
            FlagValue(Flag.CARRY, True),  # toggled
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="CCF toggles carry from clear to set",
        cycles=1,
    ),
    InstructionTestCase(
        name="SCF (0x37) - set carry flag",
        opcode=0x37,
        setup=[FlagValue(Flag.CARRY, False)],
        expected=[
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="SCF sets carry flag unconditionally",
        cycles=1,
    ),
    InstructionTestCase(
        name="SCF (0x37) - set carry flag (already set)",
        opcode=0x37,
        setup=[FlagValue(Flag.CARRY, True)],
        expected=[
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="SCF keeps carry set when already set",
        cycles=1,
    ),
]


@pytest.mark.parametrize(
    "test_case",
    MISCELLANEOUS_OPERATIONS_CASES,
    ids=[tc.name for tc in MISCELLANEOUS_OPERATIONS_CASES],
)
def test_miscellaneous_instructions(cpu, test_case):
    """Test miscellaneous instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", IO_INTERRUPT_CASES, ids=[tc.name for tc in IO_INTERRUPT_CASES]
)
def test_io_interrupt_instructions(cpu, test_case):
    """Test I/O and interrupt control instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", MISSING_OPCODE_CASES, ids=[tc.name for tc in MISSING_OPCODE_CASES]
)
def test_missing_opcodes(cpu, test_case):
    """Test missing opcode instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", HALT_CASES, ids=[tc.name for tc in HALT_CASES])
def test_halt_instructions(cpu, test_case):
    """Test halt instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", STACK_CASES, ids=[tc.name for tc in STACK_CASES])
def test_stack_operations(cpu, test_case):
    """Test stack operation instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    MISSING_SPECIAL_CASES,
    ids=[tc.name for tc in MISSING_SPECIAL_CASES],
)
def test_missing_special_instructions(cpu, test_case):
    """Test missing special instruction: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    BASE_ROTATION_CASES,
    ids=[tc.name for tc in BASE_ROTATION_CASES],
)
def test_base_rotation(cpu, test_case):
    """Test base rotation opcodes (not CB-prefixed): {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    CARRY_FLAG_CASES,
    ids=[tc.name for tc in CARRY_FLAG_CASES],
)
def test_carry_flag_ops(cpu, test_case):
    """Test carry flag operations: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


# --- STOP with invalid second byte (covers line 1610) ---
def test_stop_invalid_byte(cpu):
    """Test STOP (0x10) with non-zero second byte treats as NOP."""
    cpu._PC.value = 0xC000
    cpu._mem.wb(0xC000, 0x42)  # Invalid: second byte should be 0x00
    CPUStateValidator.execute_instruction(cpu, 0x10)
    assert cpu._m == 1, "STOP with invalid byte should take 1 cycle (NOP)"
    assert not cpu._stop, "CPU should NOT be in stop mode"



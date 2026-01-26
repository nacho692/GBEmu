import pytest
from helpers import (
    Register, Flag,
    RegisterValue, MemoryValue, FlagValue,
    InstructionTestCase, CPUStateValidator,
)

# 16-Bit Arithmetic Test Cases - ADD HL,XX operations
ARITHMETIC_16BIT_CASES = [
    # ADD HL,BC (0x09)
    InstructionTestCase(
        name="ADD HL,BC - normal case",
        opcode=0x09,
        setup=[
            RegisterValue(Register.HL, 0x1234),
            RegisterValue(Register.BC, 0x5678),
        ],
        expected=[
            RegisterValue(Register.HL, 0x68AC),  # 0x1234 + 0x5678 = 0x68AC
            FlagValue(Flag.ZERO, False),  # Flags not affected except N and H
            FlagValue(Flag.SUB, False),  # N flag cleared
            FlagValue(Flag.HALF_CARRY, False),  # No half carry from lower byte
            FlagValue(Flag.CARRY, False),  # No carry from upper byte
        ],
        description="Add BC to HL without carry",
        cycles=2,
    ),
    InstructionTestCase(
        name="ADD HL,BC - with carry",
        opcode=0x09,
        setup=[
            RegisterValue(Register.HL, 0xF000),
            RegisterValue(Register.BC, 0x2000),
        ],
        expected=[
            RegisterValue(
                Register.HL, 0x1000
            ),  # 0xF000 + 0x2000 = 0x11000 (truncated to 16 bits)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry from bit 15
        ],
        description="Add BC to HL with carry out",
        cycles=2,
    ),
    # ADD HL,DE (0x19)
    InstructionTestCase(
        name="ADD HL,DE - normal case",
        opcode=0x19,
        setup=[
            RegisterValue(Register.HL, 0x1111),
            RegisterValue(Register.DE, 0x2222),
        ],
        expected=[
            RegisterValue(Register.HL, 0x3333),  # 0x1111 + 0x2222 = 0x3333
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add DE to HL without carry",
        cycles=2,
    ),
    # ADD HL,HL (0x29)
    InstructionTestCase(
        name="ADD HL,HL - double value",
        opcode=0x29,
        setup=[
            RegisterValue(Register.HL, 0x4000),
        ],
        expected=[
            RegisterValue(Register.HL, 0x8000),  # 0x4000 + 0x4000 = 0x8000
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add HL to itself (double)",
        cycles=2,
    ),
    InstructionTestCase(
        name="ADD HL,HL - with carry",
        opcode=0x29,
        setup=[
            RegisterValue(Register.HL, 0x9000),
        ],
        expected=[
            RegisterValue(Register.HL, 0x2000),  # 0x9000 + 0x9000 = 0x12000 (truncated)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry from bit 15
        ],
        description="Add HL to itself with carry out",
        cycles=2,
    ),
    # ADD HL,SP (0x39)
    InstructionTestCase(
        name="ADD HL,SP - normal case",
        opcode=0x39,
        setup=[
            RegisterValue(Register.HL, 0x1234),
            RegisterValue(Register.SP, 0x0ABC),
        ],
        expected=[
            RegisterValue(Register.HL, 0x1CF0),  # 0x1234 + 0x0ABC = 0x1CF0 (corrected)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),  # No half carry from lower byte
            FlagValue(Flag.CARRY, False),
        ],
        description="Add SP to HL without carry",
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
    InstructionTestCase(
        name="CP E - A less than E",
        opcode=0xBB,
        setup=[
            RegisterValue(Register.A, 0x10),
            RegisterValue(Register.E, 0x20),
        ],
        expected=[
            RegisterValue(Register.A, 0x10),  # A unchanged
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Borrow needed
        ],
        description="Compare A with E - A less",
        cycles=1,
    ),
    InstructionTestCase(
        name="CP H - equal",
        opcode=0xBC,
        setup=[
            RegisterValue(Register.A, 0x42),
            RegisterValue(Register.H, 0x42),
        ],
        expected=[
            RegisterValue(Register.A, 0x42),  # A unchanged
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Compare A with H - equal",
        cycles=1,
    ),
    InstructionTestCase(
        name="CP L - A greater",
        opcode=0xBD,
        setup=[
            RegisterValue(Register.A, 0xFF),
            RegisterValue(Register.L, 0x01),
        ],
        expected=[
            RegisterValue(Register.A, 0xFF),  # A unchanged
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),  # 0xF - 0x1 = 0xE, no half borrow
            FlagValue(Flag.CARRY, False),
        ],
        description="Compare A with L - A greater",
        cycles=1,
    ),
    InstructionTestCase(
        name="CP (HL) - memory compare",
        opcode=0xBE,
        setup=[
            RegisterValue(Register.A, 0x50),
            RegisterValue(Register.HL, 0xC000),
            MemoryValue(0xC000, 0x50),
        ],
        expected=[
            RegisterValue(Register.A, 0x50),  # A unchanged
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Compare A with memory at HL - equal",
        cycles=2,
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
    InstructionTestCase(
        name="ADC A,E - with carry",
        opcode=0x8B,
        setup=[
            RegisterValue(Register.A, 0x10),
            RegisterValue(Register.E, 0x20),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x31),  # 0x10 + 0x20 + 1
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add E to A with carry",
        cycles=1,
    ),
    InstructionTestCase(
        name="ADC A,A - self add with carry",
        opcode=0x8F,
        setup=[
            RegisterValue(Register.A, 0x80),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x01),  # 0x80 + 0x80 + 1 = 0x101 & 0xFF = 0x01
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Overflow
        ],
        description="Add A to A with carry",
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
    InstructionTestCase(
        name="ADC A,H - no carry",
        opcode=0x8C,
        setup=[
            RegisterValue(Register.A, 0x42),
            RegisterValue(Register.H, 0x10),
            FlagValue(Flag.CARRY, False),
        ],
        expected=[
            RegisterValue(Register.A, 0x52),  # 0x42 + 0x10 + 0
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add H to A with carry - no carry",
        cycles=1,
    ),
    InstructionTestCase(
        name="ADC A,L - with carry",
        opcode=0x8D,
        setup=[
            RegisterValue(Register.A, 0x35),
            RegisterValue(Register.L, 0x08),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x3E),  # 0x35 + 0x08 + 1
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add L to A with carry - carry flag set",
        cycles=1,
    ),
    InstructionTestCase(
        name="ADC A,[HL] - add memory with carry",
        opcode=0x8E,
        setup=[
            RegisterValue(Register.A, 0x20),
            RegisterValue(Register.HL, 0xC000),
            MemoryValue(0xC000, 0x15),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x36),  # 0x20 + 0x15 + 1
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),  # No half carry from 0x0 + 0x5 + 1 = 0x6
            FlagValue(Flag.CARRY, False),
        ],
        description="Add memory at HL to A with carry",
        cycles=2,
    ),
]

# Extended ADD Operations Test Cases (missing H, L variants)
EXTENDED_ADD_CASES = [
    InstructionTestCase(
        name="ADD A,H - normal case",
        opcode=0x84,
        setup=[
            RegisterValue(Register.A, 0x30),
            RegisterValue(Register.H, 0x20),
        ],
        expected=[
            RegisterValue(Register.A, 0x50),  # 0x30 + 0x20
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add H to A - normal case",
        cycles=1,
    ),
    InstructionTestCase(
        name="ADD A,L - with half carry",
        opcode=0x85,
        setup=[
            RegisterValue(Register.A, 0x08),
            RegisterValue(Register.L, 0x08),
        ],
        expected=[
            RegisterValue(Register.A, 0x10),  # 0x08 + 0x08
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),  # Half carry from low nibble
            FlagValue(Flag.CARRY, False),
        ],
        description="Add L to A - with half carry",
        cycles=1,
    ),
]

# Extended SUB Operations Test Cases (missing H, L variants)
EXTENDED_SUB_CASES = [
    InstructionTestCase(
        name="SUB A,H - normal case",
        opcode=0x94,
        setup=[
            RegisterValue(Register.A, 0x50),
            RegisterValue(Register.H, 0x20),
        ],
        expected=[
            RegisterValue(Register.A, 0x30),  # 0x50 - 0x20
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Subtract H from A - normal case",
        cycles=1,
    ),
    InstructionTestCase(
        name="SUB A,L - zero result",
        opcode=0x95,
        setup=[
            RegisterValue(Register.A, 0x42),
            RegisterValue(Register.L, 0x42),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # 0x42 - 0x42
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Subtract L from A - zero result",
        cycles=1,
    ),
    InstructionTestCase(
        name="SUB E - normal case",
        opcode=0x93,
        setup=[
            RegisterValue(Register.A, 0x50),
            RegisterValue(Register.E, 0x30),
        ],
        expected=[
            RegisterValue(Register.A, 0x20),  # 0x50 - 0x30
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Subtract E from A",
        cycles=1,
    ),
]

# Extended SBC Operations Test Cases (missing H, L, [HL] variants)
EXTENDED_SBC_CASES = [
    InstructionTestCase(
        name="SBC A,H - no borrow",
        opcode=0x9C,
        setup=[
            RegisterValue(Register.A, 0x40),
            RegisterValue(Register.H, 0x10),
            FlagValue(Flag.CARRY, False),
        ],
        expected=[
            RegisterValue(Register.A, 0x30),  # 0x40 - 0x10 - 0
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Subtract H from A with borrow - no borrow",
        cycles=1,
    ),
    InstructionTestCase(
        name="SBC A,L - with borrow",
        opcode=0x9D,
        setup=[
            RegisterValue(Register.A, 0x40),
            RegisterValue(Register.L, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x2F),  # 0x40 - 0x10 - 1
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),  # Half carry from low nibble borrow
            FlagValue(Flag.CARRY, False),
        ],
        description="Subtract L from A with borrow - borrow flag set",
        cycles=1,
    ),
    InstructionTestCase(
        name="SBC A,[HL] - with borrow overflow",
        opcode=0x9E,
        setup=[
            RegisterValue(Register.A, 0x10),
            RegisterValue(Register.HL, 0xC000),
            MemoryValue(0xC000, 0x20),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0xEF),  # 0x10 - 0x20 - 1 = 0xEF
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, True),
        ],
        description="Subtract memory at HL from A with borrow - borrow needed",
        cycles=2,
    ),
    InstructionTestCase(
        name="SBC A,E - with borrow",
        opcode=0x9B,
        setup=[
            RegisterValue(Register.A, 0x50),
            RegisterValue(Register.E, 0x20),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x2F),  # 0x50 - 0x20 - 1 = 0x2F
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),  # Half carry from low nibble
            FlagValue(Flag.CARRY, False),
        ],
        description="Subtract E from A with borrow",
        cycles=1,
    ),
    InstructionTestCase(
        name="SBC A,A - with carry",
        opcode=0x9F,
        setup=[
            RegisterValue(Register.A, 0x42),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0xFF),  # 0x42 - 0x42 - 1 = -1 = 0xFF
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, True),
        ],
        description="Subtract A from A with carry",
        cycles=1,
    ),
]

# 16-Bit Increment/Decrement Operations Test Cases
INC_DEC_16BIT_CASES = [
    # INC BC (0x03) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="INC BC - normal increment",
        opcode=0x03,
        setup=[RegisterValue(Register.BC, 0x1234)],
        expected=[
            RegisterValue(Register.BC, 0x1235),
        ],
        description="Increment BC normally",
        cycles=2,
    ),
    InstructionTestCase(
        name="INC BC - overflow low byte",
        opcode=0x03,
        setup=[RegisterValue(Register.BC, 0x12FF)],
        expected=[
            RegisterValue(Register.BC, 0x1300),
        ],
        description="Increment BC with low byte overflow",
        cycles=2,
    ),
    InstructionTestCase(
        name="INC BC - overflow to zero",
        opcode=0x03,
        setup=[RegisterValue(Register.BC, 0xFFFF)],
        expected=[
            RegisterValue(Register.BC, 0x0000),
        ],
        description="Increment BC with overflow to zero",
        cycles=2,
    ),
    # DEC BC (0x0B) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="DEC BC - normal decrement",
        opcode=0x0B,
        setup=[RegisterValue(Register.BC, 0x1234)],
        expected=[
            RegisterValue(Register.BC, 0x1233),
        ],
        description="Decrement BC normally",
        cycles=2,
    ),
    InstructionTestCase(
        name="DEC BC - underflow low byte",
        opcode=0x0B,
        setup=[RegisterValue(Register.BC, 0x1200)],
        expected=[
            RegisterValue(Register.BC, 0x11FF),
        ],
        description="Decrement BC with low byte underflow",
        cycles=2,
    ),
    InstructionTestCase(
        name="DEC BC - underflow from zero",
        opcode=0x0B,
        setup=[RegisterValue(Register.BC, 0x0000)],
        expected=[
            RegisterValue(Register.BC, 0xFFFF),
        ],
        description="Decrement BC with underflow from zero",
        cycles=2,
    ),
    # INC DE (0x13) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="INC DE - normal increment",
        opcode=0x13,
        setup=[RegisterValue(Register.DE, 0x5678)],
        expected=[
            RegisterValue(Register.DE, 0x5679),
        ],
        description="Increment DE normally",
        cycles=2,
    ),
    InstructionTestCase(
        name="INC DE - overflow",
        opcode=0x13,
        setup=[RegisterValue(Register.DE, 0xFFFF)],
        expected=[
            RegisterValue(Register.DE, 0x0000),
        ],
        description="Increment DE with overflow",
        cycles=2,
    ),
    # DEC DE (0x1B) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="DEC DE - normal decrement",
        opcode=0x1B,
        setup=[RegisterValue(Register.DE, 0x5678)],
        expected=[
            RegisterValue(Register.DE, 0x5677),
        ],
        description="Decrement DE normally",
        cycles=2,
    ),
    InstructionTestCase(
        name="DEC DE - underflow",
        opcode=0x1B,
        setup=[RegisterValue(Register.DE, 0x0000)],
        expected=[
            RegisterValue(Register.DE, 0xFFFF),
        ],
        description="Decrement DE with underflow",
        cycles=2,
    ),
    # INC SP (0x33) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="INC SP - normal increment",
        opcode=0x33,
        setup=[RegisterValue(Register.SP, 0xFFFE)],
        expected=[
            RegisterValue(Register.SP, 0xFFFF),
        ],
        description="Increment SP normally",
        cycles=2,
    ),
    InstructionTestCase(
        name="INC SP - overflow",
        opcode=0x33,
        setup=[RegisterValue(Register.SP, 0xFFFF)],
        expected=[
            RegisterValue(Register.SP, 0x0000),
        ],
        description="Increment SP with overflow",
        cycles=2,
    ),
    # DEC SP (0x3B) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="DEC SP - normal decrement",
        opcode=0x3B,
        setup=[RegisterValue(Register.SP, 0x8000)],
        expected=[
            RegisterValue(Register.SP, 0x7FFF),
        ],
        description="Decrement SP normally",
        cycles=2,
    ),
    InstructionTestCase(
        name="DEC SP - underflow",
        opcode=0x3B,
        setup=[RegisterValue(Register.SP, 0x0000)],
        expected=[
            RegisterValue(Register.SP, 0xFFFF),
        ],
        description="Decrement SP with underflow",
        cycles=2,
    ),
]

# Missing 16-bit ALU Operations
MISSING_16BIT_ALU = [
    # INC HL (0x23) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="INC HL - normal increment",
        opcode=0x23,
        setup=[RegisterValue(Register.HL, 0x1234)],
        expected=[RegisterValue(Register.HL, 0x1235)],
        description="Increment HL normally",
        cycles=2,
    ),
    InstructionTestCase(
        name="INC HL - overflow low byte",
        opcode=0x23,
        setup=[RegisterValue(Register.HL, 0x12FF)],
        expected=[RegisterValue(Register.HL, 0x1300)],
        description="Increment HL with low byte overflow",
        cycles=2,
    ),
    InstructionTestCase(
        name="INC HL - overflow to zero",
        opcode=0x23,
        setup=[RegisterValue(Register.HL, 0xFFFF)],
        expected=[RegisterValue(Register.HL, 0x0000)],
        description="Increment HL with overflow to zero",
        cycles=2,
    ),
    # DEC HL (0x2B) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="DEC HL - normal decrement",
        opcode=0x2B,
        setup=[RegisterValue(Register.HL, 0x1234)],
        expected=[RegisterValue(Register.HL, 0x1233)],
        description="Decrement HL normally",
        cycles=2,
    ),
    InstructionTestCase(
        name="DEC HL - underflow low byte",
        opcode=0x2B,
        setup=[RegisterValue(Register.HL, 0x1200)],
        expected=[RegisterValue(Register.HL, 0x11FF)],
        description="Decrement HL with low byte underflow",
        cycles=2,
    ),
    InstructionTestCase(
        name="DEC HL - underflow from zero",
        opcode=0x2B,
        setup=[RegisterValue(Register.HL, 0x0000)],
        expected=[RegisterValue(Register.HL, 0xFFFF)],
        description="Decrement HL with underflow from zero",
        cycles=2,
    ),
]

# Additional 8-bit ALU Operations
ADDITIONAL_8BIT_ALU = [
    # DEC B (0x05) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="DEC B - normal decrement",
        opcode=0x05,
        setup=[RegisterValue(Register.B, 0x10)],
        expected=[
            RegisterValue(Register.B, 0x0F),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="Decrement B normally",
        cycles=1,
    ),
    InstructionTestCase(
        name="DEC B - to zero",
        opcode=0x05,
        setup=[RegisterValue(Register.B, 0x01)],
        expected=[
            RegisterValue(Register.B, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="Decrement B to zero",
        cycles=1,
    ),
    # DEC C (0x0D) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="DEC C - normal decrement",
        opcode=0x0D,
        setup=[RegisterValue(Register.C, 0x20)],
        expected=[
            RegisterValue(Register.C, 0x1F),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="Decrement C normally",
        cycles=1,
    ),
    # DEC D (0x15) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="DEC D - normal decrement",
        opcode=0x15,
        setup=[RegisterValue(Register.D, 0x30)],
        expected=[
            RegisterValue(Register.D, 0x2F),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="Decrement D normally",
        cycles=1,
    ),
    # DEC E (0x1D) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="DEC E - normal decrement",
        opcode=0x1D,
        setup=[RegisterValue(Register.E, 0x40)],
        expected=[
            RegisterValue(Register.E, 0x3F),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="Decrement E normally",
        cycles=1,
    ),
    # DEC H (0x25) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="DEC H - normal decrement",
        opcode=0x25,
        setup=[RegisterValue(Register.H, 0x50)],
        expected=[
            RegisterValue(Register.H, 0x4F),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="Decrement H normally",
        cycles=1,
    ),
    # DEC L (0x2D) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="DEC L - normal decrement",
        opcode=0x2D,
        setup=[RegisterValue(Register.L, 0x60)],
        expected=[
            RegisterValue(Register.L, 0x5F),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="Decrement L normally",
        cycles=1,
    ),
    # INC B (0x04) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="INC B - normal increment",
        opcode=0x04,
        setup=[RegisterValue(Register.B, 0x10)],
        expected=[
            RegisterValue(Register.B, 0x11),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="Increment B normally",
        cycles=1,
    ),
    # INC C (0x0C) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="INC C - normal increment",
        opcode=0x0C,
        setup=[RegisterValue(Register.C, 0x20)],
        expected=[
            RegisterValue(Register.C, 0x21),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="Increment C normally",
        cycles=1,
    ),
    # INC D (0x14) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="INC D - normal increment",
        opcode=0x14,
        setup=[RegisterValue(Register.D, 0x30)],
        expected=[
            RegisterValue(Register.D, 0x31),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="Increment D normally",
        cycles=1,
    ),
    # INC E (0x1C) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="INC E - normal increment",
        opcode=0x1C,
        setup=[RegisterValue(Register.E, 0x40)],
        expected=[
            RegisterValue(Register.E, 0x41),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="Increment E normally",
        cycles=1,
    ),
    # INC H (0x24) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="INC H - normal increment",
        opcode=0x24,
        setup=[RegisterValue(Register.H, 0x50)],
        expected=[
            RegisterValue(Register.H, 0x51),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="Increment H normally",
        cycles=1,
    ),
    # INC L (0x2C) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="INC L - normal increment",
        opcode=0x2C,
        setup=[RegisterValue(Register.L, 0x60)],
        expected=[
            RegisterValue(Register.L, 0x61),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="Increment L normally",
        cycles=1,
    ),
]

# Missing INC/DEC and 16-bit Arithmetic
MISSING_INC_DEC_CASES = [
    InstructionTestCase(
        name="DEC A - normal",
        opcode=0x3D,
        setup=[
            RegisterValue(Register.A, 0x10),
        ],
        expected=[
            RegisterValue(Register.A, 0x0F),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),  # Borrow from bit 4: 0x10 - 1
        ],
        description="Decrement A",
        cycles=1,
    ),
    InstructionTestCase(
        name="DEC A - to zero",
        opcode=0x3D,
        setup=[
            RegisterValue(Register.A, 0x01),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="Decrement A to zero",
        cycles=1,
    ),
    InstructionTestCase(
        name="DEC DE - normal",
        opcode=0x1B,
        setup=[
            RegisterValue(Register.DE, 0x1000),
        ],
        expected=[
            RegisterValue(Register.DE, 0x0FFF),
        ],
        description="Decrement DE",
        cycles=2,
    ),
    InstructionTestCase(
        name="DEC SP - normal",
        opcode=0x3B,
        setup=[
            RegisterValue(Register.SP, 0xFFFE),
        ],
        expected=[
            RegisterValue(Register.SP, 0xFFFD),
        ],
        description="Decrement SP",
        cycles=2,
    ),
    InstructionTestCase(
        name="ADD HL,HL - double HL",
        opcode=0x29,
        setup=[
            RegisterValue(Register.HL, 0x4000),
        ],
        expected=[
            RegisterValue(Register.HL, 0x8000),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add HL to HL (double)",
        cycles=2,
    ),
    InstructionTestCase(
        name="ADD HL,HL - overflow",
        opcode=0x29,
        setup=[
            RegisterValue(Register.HL, 0x8001),
        ],
        expected=[
            RegisterValue(Register.HL, 0x0002),  # 0x8001 + 0x8001 = 0x10002 & 0xFFFF
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),
        ],
        description="Add HL to HL - overflow with carry",
        cycles=2,
    ),
]

# Immediate ALU Operations
IMMEDIATE_ALU_CASES = [
    InstructionTestCase(
        name="ADD A,n - normal",
        opcode=0xC6,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.A, 0x10),
            MemoryValue(0xC000, 0x20),
        ],
        expected=[
            RegisterValue(Register.A, 0x30),
            RegisterValue(Register.PC, 0xC001),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add immediate to A",
        cycles=2,
    ),
    InstructionTestCase(
        name="ADD A,n - overflow",
        opcode=0xC6,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.A, 0xFF),
            MemoryValue(0xC000, 0x01),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),
            RegisterValue(Register.PC, 0xC001),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, True),
        ],
        description="Add immediate to A - overflow to zero",
        cycles=2,
    ),
    InstructionTestCase(
        name="ADC A,n - with carry",
        opcode=0xCE,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.A, 0x10),
            MemoryValue(0xC000, 0x20),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x31),  # 0x10 + 0x20 + 1
            RegisterValue(Register.PC, 0xC001),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add immediate with carry to A",
        cycles=2,
    ),
    InstructionTestCase(
        name="SUB n - normal",
        opcode=0xD6,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.A, 0x50),
            MemoryValue(0xC000, 0x30),
        ],
        expected=[
            RegisterValue(Register.A, 0x20),
            RegisterValue(Register.PC, 0xC001),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Subtract immediate from A",
        cycles=2,
    ),
    InstructionTestCase(
        name="SBC A,n - with borrow",
        opcode=0xDE,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.A, 0x50),
            MemoryValue(0xC000, 0x20),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x2F),  # 0x50 - 0x20 - 1
            RegisterValue(Register.PC, 0xC001),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, False),
        ],
        description="Subtract immediate with carry from A",
        cycles=2,
    ),
    InstructionTestCase(
        name="AND n - mask",
        opcode=0xE6,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.A, 0xFF),
            MemoryValue(0xC000, 0x0F),
        ],
        expected=[
            RegisterValue(Register.A, 0x0F),
            RegisterValue(Register.PC, 0xC001),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, False),
        ],
        description="AND immediate with A",
        cycles=2,
    ),
    InstructionTestCase(
        name="XOR n - toggle",
        opcode=0xEE,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.A, 0xFF),
            MemoryValue(0xC000, 0xFF),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),
            RegisterValue(Register.PC, 0xC001),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="XOR immediate with A - zero result",
        cycles=2,
    ),
    InstructionTestCase(
        name="OR n - combine",
        opcode=0xF6,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.A, 0xF0),
            MemoryValue(0xC000, 0x0F),
        ],
        expected=[
            RegisterValue(Register.A, 0xFF),
            RegisterValue(Register.PC, 0xC001),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="OR immediate with A",
        cycles=2,
    ),
    InstructionTestCase(
        name="CP n - equal",
        opcode=0xFE,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.A, 0x42),
            MemoryValue(0xC000, 0x42),
        ],
        expected=[
            RegisterValue(Register.A, 0x42),  # A unchanged
            RegisterValue(Register.PC, 0xC001),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Compare A with immediate - equal",
        cycles=2,
    ),
    InstructionTestCase(
        name="CP n - A less",
        opcode=0xFE,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.A, 0x10),
            MemoryValue(0xC000, 0x20),
        ],
        expected=[
            RegisterValue(Register.A, 0x10),
            RegisterValue(Register.PC, 0xC001),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),
        ],
        description="Compare A with immediate - A less",
        cycles=2,
    ),
]

# --- ADD SP,n negative offset (covers lines 1449, 1451) ---
ADD_SP_NEGATIVE_CASES = [
    InstructionTestCase(
        name="ADD SP,n - negative offset with carry",
        opcode=0xE8,
        setup=[
            RegisterValue(Register.PC, 0xC090),
            RegisterValue(Register.SP, 0x10FF),
            MemoryValue(0xC090, 0xFF),  # -1 as signed byte
        ],
        expected=[
            RegisterValue(Register.SP, 0x10FE),
            RegisterValue(Register.PC, 0xC091),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.CARRY, True),  # (0xFE <= 0xFF)
            FlagValue(Flag.HALF_CARRY, True),  # (0xE <= 0xF)
        ],
        description="ADD SP,-1 with carry and half carry from negative wrap",
        cycles=4,
    ),
]

# --- INC with carry flag pre-set (carry preservation branches) ---
INC_CARRY_PRESERVE_CASES = [
    InstructionTestCase(
        name="INC A (0x3C) - carry preserved",
        opcode=0x3C,
        setup=[
            RegisterValue(Register.A, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x11),
            FlagValue(Flag.CARRY, True),  # carry preserved
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
        ],
        description="INC A preserves carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="INC B (0x04) - carry preserved",
        opcode=0x04,
        setup=[
            RegisterValue(Register.B, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.B, 0x11),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
        ],
        description="INC B preserves carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="INC C (0x0C) - carry preserved",
        opcode=0x0C,
        setup=[
            RegisterValue(Register.C, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.C, 0x11),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
        ],
        description="INC C preserves carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="INC D (0x14) - carry preserved",
        opcode=0x14,
        setup=[
            RegisterValue(Register.D, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.D, 0x11),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
        ],
        description="INC D preserves carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="INC E (0x1C) - carry preserved",
        opcode=0x1C,
        setup=[
            RegisterValue(Register.E, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.E, 0x11),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
        ],
        description="INC E preserves carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="INC H (0x24) - carry preserved",
        opcode=0x24,
        setup=[
            RegisterValue(Register.H, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.H, 0x11),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
        ],
        description="INC H preserves carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="INC L (0x2C) - carry preserved",
        opcode=0x2C,
        setup=[
            RegisterValue(Register.L, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.L, 0x11),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
        ],
        description="INC L preserves carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="INC (HL) (0x34) - carry preserved",
        opcode=0x34,
        setup=[
            RegisterValue(Register.HL, 0xC080),
            MemoryValue(0xC080, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            MemoryValue(0xC080, 0x11),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
        ],
        description="INC (HL) preserves carry flag",
        cycles=3,
    ),
]

# --- DEC with carry flag pre-set (carry preservation branches) ---
DEC_CARRY_PRESERVE_CASES = [
    InstructionTestCase(
        name="DEC A (0x3D) - carry preserved",
        opcode=0x3D,
        setup=[
            RegisterValue(Register.A, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x0F),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="DEC A preserves carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="DEC B (0x05) - carry preserved",
        opcode=0x05,
        setup=[
            RegisterValue(Register.B, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.B, 0x0F),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="DEC B preserves carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="DEC C (0x0D) - carry preserved",
        opcode=0x0D,
        setup=[
            RegisterValue(Register.C, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.C, 0x0F),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="DEC C preserves carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="DEC D (0x15) - carry preserved",
        opcode=0x15,
        setup=[
            RegisterValue(Register.D, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.D, 0x0F),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="DEC D preserves carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="DEC E (0x1D) - carry preserved",
        opcode=0x1D,
        setup=[
            RegisterValue(Register.E, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.E, 0x0F),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="DEC E preserves carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="DEC H (0x25) - carry preserved",
        opcode=0x25,
        setup=[
            RegisterValue(Register.H, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.H, 0x0F),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="DEC H preserves carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="DEC L (0x2D) - carry preserved",
        opcode=0x2D,
        setup=[
            RegisterValue(Register.L, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.L, 0x0F),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="DEC L preserves carry flag",
        cycles=1,
    ),
    InstructionTestCase(
        name="DEC (HL) (0x35) - carry preserved",
        opcode=0x35,
        setup=[
            RegisterValue(Register.HL, 0xC080),
            MemoryValue(0xC080, 0x10),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            MemoryValue(0xC080, 0x0F),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="DEC (HL) preserves carry flag",
        cycles=3,
    ),
]

# --- DAA after subtraction (covers DAA else branch) ---
DAA_SUBTRACTION_CASES = [
    InstructionTestCase(
        name="DAA after SUB - half carry correction",
        opcode=0x27,
        setup=[
            RegisterValue(Register.A, 0xFA),  # Result after SUB that caused half carry
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, False),
        ],
        expected=[
            RegisterValue(Register.A, 0xF4),  # 0xFA - 0x06 = 0xF4
            FlagValue(Flag.SUB, True),  # preserved
            FlagValue(Flag.HALF_CARRY, False),  # cleared by DAA
            FlagValue(Flag.CARRY, False),
        ],
        description="DAA corrects after subtraction with half carry",
        cycles=1,
    ),
    InstructionTestCase(
        name="DAA after SUB - carry correction",
        opcode=0x27,
        setup=[
            RegisterValue(Register.A, 0x60),  # Result after SUB that caused carry
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # 0x60 - 0x60 = 0x00
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # carry preserved
            FlagValue(Flag.ZERO, True),
        ],
        description="DAA corrects after subtraction with carry",
        cycles=1,
    ),
    InstructionTestCase(
        name="DAA after SUB - both carry and half carry",
        opcode=0x27,
        setup=[
            RegisterValue(Register.A, 0x9A),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.A, 0x34),  # 0x9A - 0x06 - 0x60 = 0x34
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="DAA corrects after subtraction with both flags",
        cycles=1,
    ),
]

# --- DAA carry overflow (covers line 1564: toggle carry on bit 8) ---
DAA_CARRY_OVERFLOW_CASES = [
    InstructionTestCase(
        name="DAA addition - carry overflow from correction",
        opcode=0x27,
        setup=[
            RegisterValue(Register.A, 0x9A),  # > 0x99, needs +0x60 correction
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # 0x9A + 0x06 + 0x60 = 0x100 -> 0x00
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.CARRY, True),  # overflow from 0x100
        ],
        description="DAA triggers carry overflow during addition correction",
        cycles=1,
    ),
]


@pytest.mark.parametrize(
    "test_case", ARITHMETIC_16BIT_CASES, ids=[tc.name for tc in ARITHMETIC_16BIT_CASES]
)
def test_arithmetic_16bit_instructions(cpu, test_case):
    """Test 16-bit arithmetic instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", ADD_ARITHMETIC_CASES, ids=[tc.name for tc in ADD_ARITHMETIC_CASES]
)
def test_add_arithmetic_instructions(cpu, test_case):
    """Test 8-bit add arithmetic instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", SUB_ARITHMETIC_CASES, ids=[tc.name for tc in SUB_ARITHMETIC_CASES]
)
def test_sub_arithmetic_instructions(cpu, test_case):
    """Test 8-bit sub arithmetic instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", INC_DEC_CASES, ids=[tc.name for tc in INC_DEC_CASES]
)
def test_inc_dec_instructions(cpu, test_case):
    """Test 8-bit inc/dec instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", CP_OPERATIONS_CASES, ids=[tc.name for tc in CP_OPERATIONS_CASES]
)
def test_cp_operations(cpu, test_case):
    """Test compare operations instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", ADC_OPERATIONS_CASES, ids=[tc.name for tc in ADC_OPERATIONS_CASES]
)
def test_adc_operations(cpu, test_case):
    """Test ADC operations instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", SBC_OPERATIONS_CASES, ids=[tc.name for tc in SBC_OPERATIONS_CASES]
)
def test_sbc_operations(cpu, test_case):
    """Test SBC operations instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", EXTENDED_ADD_CASES, ids=[tc.name for tc in EXTENDED_ADD_CASES]
)
def test_extended_add_instructions(cpu, test_case):
    """Test extended ADD instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", EXTENDED_SUB_CASES, ids=[tc.name for tc in EXTENDED_SUB_CASES]
)
def test_extended_sub_instructions(cpu, test_case):
    """Test extended SUB instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", EXTENDED_SBC_CASES, ids=[tc.name for tc in EXTENDED_SBC_CASES]
)
def test_extended_sbc_instructions(cpu, test_case):
    """Test extended SBC instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", INC_DEC_16BIT_CASES, ids=[tc.name for tc in INC_DEC_16BIT_CASES]
)
def test_inc_dec_16bit_instructions(cpu, test_case):
    """Test 16-bit inc/dec instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", MISSING_16BIT_ALU, ids=[tc.name for tc in MISSING_16BIT_ALU]
)
def test_missing_16bit_alu(cpu, test_case):
    """Test missing 16-bit ALU instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", ADDITIONAL_8BIT_ALU, ids=[tc.name for tc in ADDITIONAL_8BIT_ALU]
)
def test_additional_8bit_alu(cpu, test_case):
    """Test additional 8-bit ALU instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    MISSING_INC_DEC_CASES,
    ids=[tc.name for tc in MISSING_INC_DEC_CASES],
)
def test_missing_inc_dec_instructions(cpu, test_case):
    """Test missing INC/DEC instruction: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    IMMEDIATE_ALU_CASES,
    ids=[tc.name for tc in IMMEDIATE_ALU_CASES],
)
def test_immediate_alu_instructions(cpu, test_case):
    """Test immediate ALU instruction: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    ADD_SP_NEGATIVE_CASES,
    ids=[tc.name for tc in ADD_SP_NEGATIVE_CASES],
)
def test_add_sp_negative(cpu, test_case):
    """Test ADD SP,n with negative offset: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    INC_CARRY_PRESERVE_CASES,
    ids=[tc.name for tc in INC_CARRY_PRESERVE_CASES],
)
def test_inc_carry_preserve(cpu, test_case):
    """Test INC instructions preserve carry flag: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    DEC_CARRY_PRESERVE_CASES,
    ids=[tc.name for tc in DEC_CARRY_PRESERVE_CASES],
)
def test_dec_carry_preserve(cpu, test_case):
    """Test DEC instructions preserve carry flag: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    DAA_SUBTRACTION_CASES,
    ids=[tc.name for tc in DAA_SUBTRACTION_CASES],
)
def test_daa_subtraction(cpu, test_case):
    """Test DAA instruction after subtraction: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    DAA_CARRY_OVERFLOW_CASES,
    ids=[tc.name for tc in DAA_CARRY_OVERFLOW_CASES],
)
def test_daa_carry_overflow(cpu, test_case):
    """Test DAA carry overflow: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"



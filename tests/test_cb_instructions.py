import pytest
from helpers import (
    Register, Flag,
    RegisterValue, MemoryValue, FlagValue,
    InstructionTestCase, CPUStateValidator,
)

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

# Comprehensive CB Rotations and Shifts Test Cases
CB_ROTATION_SHIFT_CASES = [
    # RLC variants (0x00-0x07)
    InstructionTestCase(
        name="CB RLC B - rotate left circular",
        opcode=0x00,
        setup=[
            RegisterValue(Register.B, 0x85),  # 0b10000101
        ],
        expected=[
            RegisterValue(Register.B, 0x0B),  # 0b00001011 (rotated)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry from bit 7
        ],
        description="Rotate B left circular",
        cycles=2,
    ),
    InstructionTestCase(
        name="CB RLC C - rotate to zero",
        opcode=0x01,
        setup=[
            RegisterValue(Register.C, 0x80),  # 0b10000000
        ],
        expected=[
            RegisterValue(Register.C, 0x01),  # 0b00000001 (rotated)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry from bit 7
        ],
        description="Rotate C left circular to zero",
        cycles=2,
    ),
    # RRC variants (0x08-0x0F)
    InstructionTestCase(
        name="CB RRC D - rotate right circular",
        opcode=0x0A,
        setup=[
            RegisterValue(Register.D, 0x85),  # 0b10000101
        ],
        expected=[
            RegisterValue(Register.D, 0xC2),  # 0b11000010 (rotated)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry from bit 0
        ],
        description="Rotate D right circular",
        cycles=2,
    ),
    # RL variants (0x10-0x17)
    InstructionTestCase(
        name="CB RL E - rotate left through carry",
        opcode=0x13,
        setup=[
            RegisterValue(Register.E, 0x40),  # 0b01000000
            FlagValue(Flag.CARRY, True),  # Incoming carry
        ],
        expected=[
            RegisterValue(Register.E, 0x81),  # 0b10000001 (rotated with carry)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),  # No carry out
        ],
        description="Rotate E left through carry",
        cycles=2,
    ),
    # RR variants (0x18-0x1F)
    InstructionTestCase(
        name="CB RR H - rotate right through carry",
        opcode=0x1C,
        setup=[
            RegisterValue(Register.H, 0x01),  # 0b00000001
            FlagValue(Flag.CARRY, True),  # Incoming carry
        ],
        expected=[
            RegisterValue(Register.H, 0x80),  # 0b10000000 (rotated with carry)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry from bit 0
        ],
        description="Rotate H right through carry",
        cycles=2,
    ),
    # SLA variants (0x20-0x27)
    InstructionTestCase(
        name="CB SLA L - shift left arithmetic",
        opcode=0x25,
        setup=[
            RegisterValue(Register.L, 0x40),  # 0b01000000
        ],
        expected=[
            RegisterValue(Register.L, 0x80),  # 0b10000000 (shifted)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),  # No carry out
        ],
        description="Shift L left arithmetic",
        cycles=2,
    ),
    # SRA variants (0x28-0x2F)
    InstructionTestCase(
        name="CB SRA [HL] - shift right arithmetic memory",
        opcode=0x2E,
        setup=[
            RegisterValue(Register.HL, 0xC000),
            MemoryValue(0xC000, 0x85),  # 0b10000101
        ],
        expected=[
            MemoryValue(0xC000, 0xC2),  # 0b11000010 (shifted preserving sign)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry from bit 0
        ],
        description="Shift memory at HL right arithmetic",
        cycles=4,
    ),
    # SRL variants (0x38-0x3F)
    InstructionTestCase(
        name="CB SRL A - shift right logical",
        opcode=0x3F,
        setup=[
            RegisterValue(Register.A, 0x81),  # 0b10000001
        ],
        expected=[
            RegisterValue(Register.A, 0x40),  # 0b01000000 (shifted)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry from bit 0
        ],
        description="Shift A right logical",
        cycles=2,
    ),
]

# CB Bit Operations Test Cases
CB_BIT_OPERATIONS_CASES = [
    # BIT variants (0x40-0x7F)
    InstructionTestCase(
        name="CB BIT 0,B - test bit 0 in B",
        opcode=0x40,
        setup=[
            RegisterValue(Register.B, 0x01),  # Bit 0 set
        ],
        expected=[
            RegisterValue(Register.B, 0x01),  # B unchanged
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),  # BIT sets half carry
            FlagValue(Flag.CARRY, False),
        ],
        description="Test bit 0 in B - bit set",
        cycles=2,
    ),
    InstructionTestCase(
        name="CB BIT 7,C - test bit 7 in C",
        opcode=0x79,  # Correct opcode for BIT 7,C
        setup=[
            RegisterValue(Register.C, 0x7F),  # Bit 7 clear
        ],
        expected=[
            RegisterValue(Register.C, 0x7F),  # C unchanged
            FlagValue(Flag.ZERO, True),  # Bit is clear
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),  # BIT sets half carry
            FlagValue(Flag.CARRY, False),
        ],
        description="Test bit 7 in C - bit clear",
        cycles=2,
    ),
    # RES variants (0x80-0xBF)
    InstructionTestCase(
        name="CB RES 3,D - reset bit 3 in D",
        opcode=0x9A,  # Correct opcode for RES 3,D
        setup=[
            RegisterValue(Register.D, 0xFF),  # All bits set
        ],
        expected=[
            RegisterValue(Register.D, 0xF7),  # 0b11110111 (bit 3 cleared)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Reset bit 3 in D",
        cycles=2,
    ),
    InstructionTestCase(
        name="CB RES 5,[HL] - reset bit in memory",
        opcode=0xAE,  # Correct opcode for RES 5,[HL]
        setup=[
            RegisterValue(Register.HL, 0xC100),
            MemoryValue(0xC100, 0xFF),  # All bits set
        ],
        expected=[
            MemoryValue(0xC100, 0xDF),  # 0b11011111 (bit 5 cleared)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Reset bit 5 in memory at HL",
        cycles=4,
    ),
    # SET variants (0xC0-0xFF)
    InstructionTestCase(
        name="CB SET 6,[HL] - set bit in memory",
        opcode=0xF6,
        setup=[
            RegisterValue(Register.HL, 0xC200),
            MemoryValue(0xC200, 0x00),  # All bits clear
        ],
        expected=[
            MemoryValue(0xC200, 0x40),  # 0b01000000 (bit 6 set)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Set bit 6 in memory at HL",
        cycles=4,
    ),
]

# Comprehensive CB-Prefix Extended Test Cases - Complete CB coverage
COMPREHENSIVE_CB_CASES = [
    # RRC Operations - rotate right circular
    InstructionTestCase(
        name="RRC A - rotate right circular",
        opcode=0x0F,  # CB prefix + 0x0F
        setup=[RegisterValue(Register.A, 0x85)],  # 0b10000101
        expected=[
            RegisterValue(
                Register.A, 0xC2
            ),  # 0b11000010 (rotated right, bit 0 -> carry)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out = original bit 0
        ],
        description="Rotate A right circular",
        cycles=2,
    ),
    # RL Operations - rotate left through carry
    InstructionTestCase(
        name="RL A - rotate left through carry",
        opcode=0x17,  # CB prefix + 0x17
        setup=[
            RegisterValue(Register.A, 0x85),
            FlagValue(Flag.CARRY, True),  # Carry in = 1
        ],
        expected=[
            RegisterValue(Register.A, 0x0B),  # 0b00001011 (rotate with carry)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out = original bit 7
        ],
        description="Rotate A left through carry",
        cycles=2,
    ),
    # RR Operations - rotate right through carry
    InstructionTestCase(
        name="RR A - rotate right through carry",
        opcode=0x1F,  # CB prefix + 0x1F
        setup=[
            RegisterValue(Register.A, 0x85),
            FlagValue(Flag.CARRY, True),  # Carry in = 1
        ],
        expected=[
            RegisterValue(Register.A, 0xC2),  # 0b11000010 (rotate with carry)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out = original bit 0
        ],
        description="Rotate A right through carry",
        cycles=2,
    ),
    # SLA Operations - shift left arithmetic
    InstructionTestCase(
        name="SLA A - shift left arithmetic",
        opcode=0x27,  # CB prefix + 0x27
        setup=[RegisterValue(Register.A, 0x85)],  # 0b10000101
        expected=[
            RegisterValue(Register.A, 0x0A),  # 0b00001010 (shift left, bit 7 to carry)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out = original bit 7
        ],
        description="Shift A left arithmetic",
        cycles=2,
    ),
    # SRA Operations - shift right arithmetic
    InstructionTestCase(
        name="SRA A - shift right arithmetic",
        opcode=0x2F,  # CB prefix + 0x2F
        setup=[RegisterValue(Register.A, 0x85)],  # 0b10000101
        expected=[
            RegisterValue(
                Register.A, 0xC2
            ),  # 0b11000010 (shift right preserving bit 7)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out = original bit 0
        ],
        description="Shift A right arithmetic",
        cycles=2,
    ),
    # SRL Operations - shift right logical
    InstructionTestCase(
        name="SRL A - shift right logical",
        opcode=0x3F,  # CB prefix + 0x3F
        setup=[RegisterValue(Register.A, 0x85)],  # 0b10000101
        expected=[
            RegisterValue(Register.A, 0x42),  # 0b01000010 (shift right, MSB = 0)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out = original bit 0
        ],
        description="Shift A right logical",
        cycles=2,
    ),
    # RES Operations - reset bits
    InstructionTestCase(
        name="RES 3,B - reset bit 3",
        opcode=0x98,  # CB prefix + 0x98
        setup=[RegisterValue(Register.B, 0xFF)],  # All bits set
        expected=[
            RegisterValue(Register.B, 0xF7),  # 0b11110111 (bit 3 cleared)
        ],
        description="Reset bit 3 in B",
        cycles=2,
    ),
    # More comprehensive BIT tests
    InstructionTestCase(
        name="BIT 5,D - test bit 5 in D",
        opcode=0x6A,  # CB prefix + 0x6A
        setup=[RegisterValue(Register.D, 0x20)],  # 0b00100000 (bit 5 set)
        expected=[
            RegisterValue(Register.D, 0x20),  # D unchanged
            FlagValue(Flag.ZERO, False),  # Bit is set
            FlagValue(Flag.SUB, False),  # BIT clears SUB
            FlagValue(Flag.HALF_CARRY, True),  # BIT sets half carry
        ],
        description="Test bit 5 in D - bit is set",
        cycles=2,
    ),
    # Memory-based BIT operations
    InstructionTestCase(
        name="BIT 2,[HL] - test bit in memory",
        opcode=0x56,  # CB prefix + 0x66
        setup=[
            RegisterValue(Register.HL, 0xC200),  # Use proper WRAM range
            MemoryValue(0xC200, 0x04),  # 0b00000100 (bit 2 set)
        ],
        expected=[
            MemoryValue(0xC200, 0x04),  # Memory unchanged
            FlagValue(Flag.ZERO, False),  # Bit is set
            FlagValue(Flag.SUB, False),  # BIT clears SUB
            FlagValue(Flag.HALF_CARRY, True),  # BIT sets half carry
        ],
        description="Test bit 2 at [HL] - bit is set",
        cycles=4,
    ),
    # SET Operations - set bits
    InstructionTestCase(
        name="SET 7,H - set highest bit",
        opcode=0xFC,  # CB prefix + 0xFC
        setup=[RegisterValue(Register.H, 0x00)],  # All bits cleared
        expected=[
            RegisterValue(Register.H, 0x80),  # 0b10000000 (bit 7 set)
        ],
        description="Set bit 7 in H",
        cycles=2,
    ),
    # Memory-based SET operations
    InstructionTestCase(
        name="SET 1,[HL] - set bit in memory",
        opcode=0xCE,  # CB prefix + 0xCE
        setup=[
            RegisterValue(Register.HL, 0xD200),
            MemoryValue(0xD200, 0x01),  # 0b00000001
        ],
        expected=[
            MemoryValue(0xD200, 0x03),  # 0b00000011 (bit 1 set)
        ],
        description="Set bit 1 at [HL]",
        cycles=4,
    ),
    # Memory-based rotate operations
    InstructionTestCase(
        name="RLC [HL] - rotate memory left circular",
        opcode=0x06,  # CB prefix + 0x06
        setup=[
            RegisterValue(Register.HL, 0xC200),
            MemoryValue(0xC200, 0x85),  # 0b10000101
        ],
        expected=[
            MemoryValue(0xC200, 0x0B),  # 0b00001011 (rotated left)
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),  # Carry out = original bit 7
        ],
        description="Rotate memory at [HL] left circular",
        cycles=4,
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

# =============================================================================
# CB Rotate & Shift Completeness (0xCB00-0xCB3F)
# =============================================================================

# Register map for CB opcodes: low 3 bits → register
_CB_REG_MAP = {
    0: (Register.B, "B"),
    1: (Register.C, "C"),
    2: (Register.D, "D"),
    3: (Register.E, "E"),
    4: (Register.H, "H"),
    5: (Register.L, "L"),
    # 6: (HL) memory - handled separately
    7: (Register.A, "A"),
}

# Define operations with: (base_opcode, name, input, expected_output, carry_out)
# Each tuple: (input_val, carry_in, expected_val, carry_out)
_CB_ROTATE_SHIFT_OPS = {
    "RLC": (0x00, 0x85, None, 0x0B, True),   # 10000101 → 00001011, C=1
    "RRC": (0x08, 0x85, None, 0xC2, True),   # 10000101 → 11000010, C=1
    "RL":  (0x10, 0x80, False, 0x00, True),   # 10000000 + carry=0 → 00000000, C=1
    "RR":  (0x18, 0x01, False, 0x00, True),   # 00000001 + carry=0 → 00000000, C=1
    "SLA": (0x20, 0x85, None, 0x0A, True),   # 10000101 → 00001010, C=1
    "SRA": (0x28, 0x85, None, 0xC2, True),   # 10000101 → 11000010, C=1 (MSB preserved)
    "SWAP":(0x30, 0xF1, None, 0x1F, False),  # 11110001 → 00011111, C=0
    "SRL": (0x38, 0x85, None, 0x42, True),   # 10000101 → 01000010, C=1
}

CB_ROTATE_SHIFT_COMPLETENESS_CASES = []

for op_name, (base, inp, carry_in, exp, carry_out) in _CB_ROTATE_SHIFT_OPS.items():
    for reg_idx, (reg_enum, reg_name) in _CB_REG_MAP.items():
        opcode = base + reg_idx
        setup = [RegisterValue(reg_enum, inp)]
        if carry_in is not None:
            setup.append(FlagValue(Flag.CARRY, carry_in))
        expected = [
            RegisterValue(reg_enum, exp),
            FlagValue(Flag.ZERO, exp == 0),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, carry_out),
        ]
        CB_ROTATE_SHIFT_COMPLETENESS_CASES.append(InstructionTestCase(
            name=f"CB {op_name} {reg_name}",
            opcode=opcode,
            setup=setup,
            expected=expected,
            description=f"{op_name} {reg_name}",
            cycles=2,
        ))
    # (HL) memory variant
    hl_opcode = base + 6
    setup = [
        RegisterValue(Register.HL, 0xC080),
        MemoryValue(0xC080, inp),
    ]
    if carry_in is not None:
        setup.append(FlagValue(Flag.CARRY, carry_in))
    expected = [
        MemoryValue(0xC080, exp),
        FlagValue(Flag.ZERO, exp == 0),
        FlagValue(Flag.SUB, False),
        FlagValue(Flag.HALF_CARRY, False),
        FlagValue(Flag.CARRY, carry_out),
    ]
    CB_ROTATE_SHIFT_COMPLETENESS_CASES.append(InstructionTestCase(
        name=f"CB {op_name} (HL)",
        opcode=hl_opcode,
        setup=setup,
        expected=expected,
        description=f"{op_name} (HL)",
        cycles=4,
    ))


@pytest.mark.parametrize(
    "test_case",
    CB_ROTATE_SHIFT_COMPLETENESS_CASES,
    ids=[tc.name for tc in CB_ROTATE_SHIFT_COMPLETENESS_CASES],
)
def test_cb_rotate_shift_completeness(cpu, test_case):
    """Test CB rotate/shift instruction: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    cb_method = getattr(cpu, f"OPCode_CB{test_case.opcode:02X}")
    cb_method()
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


# =============================================================================
# CB BIT Operations (0xCB40-0xCB7F)
# =============================================================================

CB_BIT_COMPLETENESS_CASES = []

for bit in range(8):
    for reg_idx, (reg_enum, reg_name) in _CB_REG_MAP.items():
        opcode = 0x40 + (bit * 8) + reg_idx
        # Test with bit SET → Zero=False
        CB_BIT_COMPLETENESS_CASES.append(InstructionTestCase(
            name=f"CB BIT {bit},{reg_name} - set",
            opcode=opcode,
            setup=[RegisterValue(reg_enum, 1 << bit)],
            expected=[
                RegisterValue(reg_enum, 1 << bit),  # Register unchanged
                FlagValue(Flag.ZERO, False),
                FlagValue(Flag.SUB, False),
                FlagValue(Flag.HALF_CARRY, True),
            ],
            description=f"BIT {bit},{reg_name} - bit is set",
            cycles=2,
        ))
        # Test with bit CLEAR → Zero=True
        CB_BIT_COMPLETENESS_CASES.append(InstructionTestCase(
            name=f"CB BIT {bit},{reg_name} - clear",
            opcode=opcode,
            setup=[RegisterValue(reg_enum, 0xFF & ~(1 << bit))],
            expected=[
                RegisterValue(reg_enum, 0xFF & ~(1 << bit)),  # Register unchanged
                FlagValue(Flag.ZERO, True),
                FlagValue(Flag.SUB, False),
                FlagValue(Flag.HALF_CARRY, True),
            ],
            description=f"BIT {bit},{reg_name} - bit is clear",
            cycles=2,
        ))
    # (HL) memory variants
    hl_opcode = 0x40 + (bit * 8) + 6
    CB_BIT_COMPLETENESS_CASES.append(InstructionTestCase(
        name=f"CB BIT {bit},(HL) - set",
        opcode=hl_opcode,
        setup=[
            RegisterValue(Register.HL, 0xC080),
            MemoryValue(0xC080, 1 << bit),
        ],
        expected=[
            MemoryValue(0xC080, 1 << bit),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description=f"BIT {bit},(HL) - bit is set",
        cycles=4,
    ))
    CB_BIT_COMPLETENESS_CASES.append(InstructionTestCase(
        name=f"CB BIT {bit},(HL) - clear",
        opcode=hl_opcode,
        setup=[
            RegisterValue(Register.HL, 0xC080),
            MemoryValue(0xC080, 0xFF & ~(1 << bit)),
        ],
        expected=[
            MemoryValue(0xC080, 0xFF & ~(1 << bit)),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description=f"BIT {bit},(HL) - bit is clear",
        cycles=4,
    ))


@pytest.mark.parametrize(
    "test_case",
    CB_BIT_COMPLETENESS_CASES,
    ids=[tc.name for tc in CB_BIT_COMPLETENESS_CASES],
)
def test_cb_bit_completeness(cpu, test_case):
    """Test CB BIT instruction: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    cb_method = getattr(cpu, f"OPCode_CB{test_case.opcode:02X}")
    cb_method()
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


# =============================================================================
# CB RES & SET Operations (0xCB80-0xCBFF)
# =============================================================================

CB_RES_COMPLETENESS_CASES = []

for bit in range(8):
    for reg_idx, (reg_enum, reg_name) in _CB_REG_MAP.items():
        opcode = 0x80 + (bit * 8) + reg_idx
        CB_RES_COMPLETENESS_CASES.append(InstructionTestCase(
            name=f"CB RES {bit},{reg_name}",
            opcode=opcode,
            setup=[RegisterValue(reg_enum, 0xFF)],
            expected=[RegisterValue(reg_enum, 0xFF & ~(1 << bit))],
            description=f"RES {bit},{reg_name}",
            cycles=2,
        ))
    # (HL) memory variant
    hl_opcode = 0x80 + (bit * 8) + 6
    CB_RES_COMPLETENESS_CASES.append(InstructionTestCase(
        name=f"CB RES {bit},(HL)",
        opcode=hl_opcode,
        setup=[
            RegisterValue(Register.HL, 0xC080),
            MemoryValue(0xC080, 0xFF),
        ],
        expected=[MemoryValue(0xC080, 0xFF & ~(1 << bit))],
        description=f"RES {bit},(HL)",
        cycles=4,
    ))

CB_SET_COMPLETENESS_CASES = []

for bit in range(8):
    for reg_idx, (reg_enum, reg_name) in _CB_REG_MAP.items():
        opcode = 0xC0 + (bit * 8) + reg_idx
        CB_SET_COMPLETENESS_CASES.append(InstructionTestCase(
            name=f"CB SET {bit},{reg_name}",
            opcode=opcode,
            setup=[RegisterValue(reg_enum, 0x00)],
            expected=[RegisterValue(reg_enum, 1 << bit)],
            description=f"SET {bit},{reg_name}",
            cycles=2,
        ))
    # (HL) memory variant
    hl_opcode = 0xC0 + (bit * 8) + 6
    CB_SET_COMPLETENESS_CASES.append(InstructionTestCase(
        name=f"CB SET {bit},(HL)",
        opcode=hl_opcode,
        setup=[
            RegisterValue(Register.HL, 0xC080),
            MemoryValue(0xC080, 0x00),
        ],
        expected=[MemoryValue(0xC080, 1 << bit)],
        description=f"SET {bit},(HL)",
        cycles=4,
    ))


@pytest.mark.parametrize(
    "test_case",
    CB_RES_COMPLETENESS_CASES,
    ids=[tc.name for tc in CB_RES_COMPLETENESS_CASES],
)
def test_cb_res_completeness(cpu, test_case):
    """Test CB RES instruction: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    cb_method = getattr(cpu, f"OPCode_CB{test_case.opcode:02X}")
    cb_method()
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    CB_SET_COMPLETENESS_CASES,
    ids=[tc.name for tc in CB_SET_COMPLETENESS_CASES],
)
def test_cb_set_completeness(cpu, test_case):
    """Test CB SET instruction: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    cb_method = getattr(cpu, f"OPCode_CB{test_case.opcode:02X}")
    cb_method()
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"



@pytest.mark.parametrize(
    "test_case", ROTATION_SHIFT_CASES, ids=[tc.name for tc in ROTATION_SHIFT_CASES]
)
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


@pytest.mark.parametrize(
    "test_case",
    CB_ROTATION_SHIFT_CASES,
    ids=[tc.name for tc in CB_ROTATION_SHIFT_CASES],
)
def test_cb_rotation_shift_instructions(cpu, test_case):
    """Test CB rotation/shift instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute CB-prefixed instruction
    cb_method = getattr(cpu, f"OPCode_CB{test_case.opcode & 0xFF:02X}")
    cb_method()

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    CB_BIT_OPERATIONS_CASES,
    ids=[tc.name for tc in CB_BIT_OPERATIONS_CASES],
)
def test_cb_bit_operations(cpu, test_case):
    """Test CB bit operation instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute CB-prefixed instruction
    cb_method = getattr(cpu, f"OPCode_CB{test_case.opcode & 0xFF:02X}")
    cb_method()

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", COMPREHENSIVE_CB_CASES, ids=[tc.name for tc in COMPREHENSIVE_CB_CASES]
)
def test_comprehensive_cb_instructions(cpu, test_case):
    """Test comprehensive CB-prefixed instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute CB-prefixed instruction normally like other CB tests
    # Set up CB prefix at current PC and execute CB handler directly
    cb_method = getattr(cpu, f"OPCode_CB{test_case.opcode & 0xFF:02X}")
    cb_method()

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", BIT_OPERATIONS_CASES, ids=[tc.name for tc in BIT_OPERATIONS_CASES]
)
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


@pytest.mark.parametrize(
    "test_case",
    CB_ROTATE_SHIFT_COMPLETENESS_CASES,
    ids=[tc.name for tc in CB_ROTATE_SHIFT_COMPLETENESS_CASES],
)
def test_cb_rotate_shift_completeness(cpu, test_case):
    """Test CB rotate/shift instruction: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    cb_method = getattr(cpu, f"OPCode_CB{test_case.opcode:02X}")
    cb_method()
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    CB_BIT_COMPLETENESS_CASES,
    ids=[tc.name for tc in CB_BIT_COMPLETENESS_CASES],
)
def test_cb_bit_completeness(cpu, test_case):
    """Test CB BIT instruction: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    cb_method = getattr(cpu, f"OPCode_CB{test_case.opcode:02X}")
    cb_method()
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    CB_RES_COMPLETENESS_CASES,
    ids=[tc.name for tc in CB_RES_COMPLETENESS_CASES],
)
def test_cb_res_completeness(cpu, test_case):
    """Test CB RES instruction: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    cb_method = getattr(cpu, f"OPCode_CB{test_case.opcode:02X}")
    cb_method()
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    CB_SET_COMPLETENESS_CASES,
    ids=[tc.name for tc in CB_SET_COMPLETENESS_CASES],
)
def test_cb_set_completeness(cpu, test_case):
    """Test CB SET instruction: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    cb_method = getattr(cpu, f"OPCode_CB{test_case.opcode:02X}")
    cb_method()
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"



# --- CB dispatcher (covers lines 1499-1501) ---
def test_cb_dispatcher(cpu):
    """Test the CB prefix dispatcher (0xCB) routes to CB sub-opcode."""
    cpu._PC.value = 0xC000
    cpu._mem.wb(0xC000, 0x37)  # CB opcode for SWAP A
    cpu._AF.high = 0xF0
    CPUStateValidator.execute_instruction(cpu, 0xCB)
    assert cpu._AF.high == 0x0F, "CB dispatcher should route to SWAP A"
    assert cpu._PC.value == 0xC001, "PC should advance past CB sub-opcode byte"



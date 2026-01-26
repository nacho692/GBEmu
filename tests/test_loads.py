import pytest
from helpers import (
    Register, Flag,
    RegisterValue, MemoryValue, FlagValue,
    InstructionTestCase, CPUStateValidator,
)

# Basic Operations Test Cases - NOP and 8-bit immediate loads
BASIC_LOAD_CASES = [
    # NOP (0x00) - No operation
    InstructionTestCase(
        name="NOP - no operation",
        opcode=0x00,
        setup=[],
        expected=[],
        description="No operation - should not change any state",
        cycles=1,
    ),
    # 8-bit immediate loads
    # LD B,n (0x06)
    InstructionTestCase(
        name="LD B,n - zero value",
        opcode=0x06,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            MemoryValue(0xC000, 0x00),
        ],
        expected=[
            RegisterValue(Register.B, 0x00),
            RegisterValue(Register.PC, 0xC001),
        ],
        description="Load immediate zero into B",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD B,n - max value",
        opcode=0x06,
        setup=[
            RegisterValue(Register.PC, 0xC010),
            MemoryValue(0xC010, 0xFF),
        ],
        expected=[
            RegisterValue(Register.B, 0xFF),
            RegisterValue(Register.PC, 0xC011),
        ],
        description="Load immediate max value into B",
        cycles=2,
    ),
    # LD C,n (0x0E)
    InstructionTestCase(
        name="LD C,n - typical value",
        opcode=0x0E,
        setup=[
            RegisterValue(Register.PC, 0xC020),
            MemoryValue(0xC020, 0x42),
        ],
        expected=[
            RegisterValue(Register.C, 0x42),
            RegisterValue(Register.PC, 0xC021),
        ],
        description="Load immediate value into C",
        cycles=2,
    ),
    # LD D,n (0x16)
    InstructionTestCase(
        name="LD D,n - typical value",
        opcode=0x16,
        setup=[
            RegisterValue(Register.PC, 0xC030),
            MemoryValue(0xC030, 0x11),
        ],
        expected=[
            RegisterValue(Register.D, 0x11),
            RegisterValue(Register.PC, 0xC031),
        ],
        description="Load immediate value into D",
        cycles=2,
    ),
    # LD E,n (0x1E)
    InstructionTestCase(
        name="LD E,n - typical value",
        opcode=0x1E,
        setup=[
            RegisterValue(Register.PC, 0xC040),
            MemoryValue(0xC040, 0x22),
        ],
        expected=[
            RegisterValue(Register.E, 0x22),
            RegisterValue(Register.PC, 0xC041),
        ],
        description="Load immediate value into E",
        cycles=2,
    ),
    # LD H,n (0x26)
    InstructionTestCase(
        name="LD H,n - typical value",
        opcode=0x26,
        setup=[
            RegisterValue(Register.PC, 0xC050),
            MemoryValue(0xC050, 0x33),
        ],
        expected=[
            RegisterValue(Register.H, 0x33),
            RegisterValue(Register.PC, 0xC051),
        ],
        description="Load immediate value into H",
        cycles=2,
    ),
    # LD L,n (0x2E)
    InstructionTestCase(
        name="LD L,n - typical value",
        opcode=0x2E,
        setup=[
            RegisterValue(Register.PC, 0xC060),
            MemoryValue(0xC060, 0x44),
        ],
        expected=[
            RegisterValue(Register.L, 0x44),
            RegisterValue(Register.PC, 0xC061),
        ],
        description="Load immediate value into L",
        cycles=2,
    ),
]

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
    InstructionTestCase(
        name="LD B,H",
        opcode=0x44,
        setup=[RegisterValue(Register.H, 0x56)],
        expected=[RegisterValue(Register.B, 0x56)],
        description="Copy H to B",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD B,L",
        opcode=0x45,
        setup=[RegisterValue(Register.L, 0x78)],
        expected=[RegisterValue(Register.B, 0x78)],
        description="Copy L to B",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD B,[HL]",
        opcode=0x46,
        setup=[
            RegisterValue(Register.HL, 0xC100),
            MemoryValue(0xC100, 0x9A),
        ],
        expected=[RegisterValue(Register.B, 0x9A)],
        description="Load from memory pointed by HL into B",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD B,A",
        opcode=0x47,
        setup=[RegisterValue(Register.A, 0xBC)],
        expected=[RegisterValue(Register.B, 0xBC)],
        description="Copy A to B",
        cycles=1,
    ),
    # Instructions loading into C (0x48-0x4F)
    InstructionTestCase(
        name="LD C,B",
        opcode=0x48,
        setup=[RegisterValue(Register.B, 0x11)],
        expected=[RegisterValue(Register.C, 0x11)],
        description="Copy B to C",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD C,C",
        opcode=0x49,
        setup=[RegisterValue(Register.C, 0x22)],
        expected=[RegisterValue(Register.C, 0x22)],
        description="Copy C to C (identity)",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD C,D",
        opcode=0x4A,
        setup=[RegisterValue(Register.D, 0x33)],
        expected=[RegisterValue(Register.C, 0x33)],
        description="Copy D to C",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD C,E",
        opcode=0x4B,
        setup=[RegisterValue(Register.E, 0x44)],
        expected=[RegisterValue(Register.C, 0x44)],
        description="Copy E to C",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD C,H",
        opcode=0x4C,
        setup=[RegisterValue(Register.H, 0x55)],
        expected=[RegisterValue(Register.C, 0x55)],
        description="Copy H to C",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD C,L",
        opcode=0x4D,
        setup=[RegisterValue(Register.L, 0x66)],
        expected=[RegisterValue(Register.C, 0x66)],
        description="Copy L to C",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD C,[HL]",
        opcode=0x4E,
        setup=[
            RegisterValue(Register.HL, 0xC200),
            MemoryValue(0xC200, 0x77),
        ],
        expected=[RegisterValue(Register.C, 0x77)],
        description="Load from memory pointed by HL into C",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD C,A",
        opcode=0x4F,
        setup=[RegisterValue(Register.A, 0x88)],
        expected=[RegisterValue(Register.C, 0x88)],
        description="Copy A to C",
        cycles=1,
    ),
    # Instructions loading into D (0x50-0x57)
    InstructionTestCase(
        name="LD D,B",
        opcode=0x50,
        setup=[RegisterValue(Register.B, 0x11)],
        expected=[RegisterValue(Register.D, 0x11)],
        description="Copy B to D",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD D,C",
        opcode=0x51,
        setup=[RegisterValue(Register.C, 0x22)],
        expected=[RegisterValue(Register.D, 0x22)],
        description="Copy C to D",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD D,D",
        opcode=0x52,
        setup=[RegisterValue(Register.D, 0x33)],
        expected=[RegisterValue(Register.D, 0x33)],
        description="Copy D to D (identity)",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD D,E",
        opcode=0x53,
        setup=[RegisterValue(Register.E, 0x44)],
        expected=[RegisterValue(Register.D, 0x44)],
        description="Copy E to D",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD D,H",
        opcode=0x54,
        setup=[RegisterValue(Register.H, 0x55)],
        expected=[RegisterValue(Register.D, 0x55)],
        description="Copy H to D",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD D,L",
        opcode=0x55,
        setup=[RegisterValue(Register.L, 0x66)],
        expected=[RegisterValue(Register.D, 0x66)],
        description="Copy L to D",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD D,[HL]",
        opcode=0x56,
        setup=[
            RegisterValue(Register.HL, 0xC300),
            MemoryValue(0xC300, 0x99),
        ],
        expected=[RegisterValue(Register.D, 0x99)],
        description="Load from memory pointed by HL into D",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD D,A",
        opcode=0x57,
        setup=[RegisterValue(Register.A, 0xAA)],
        expected=[RegisterValue(Register.D, 0xAA)],
        description="Copy A to D",
        cycles=1,
    ),
    # Instructions loading into E (0x58-0x5F)
    InstructionTestCase(
        name="LD E,B",
        opcode=0x58,
        setup=[RegisterValue(Register.B, 0x11)],
        expected=[RegisterValue(Register.E, 0x11)],
        description="Copy B to E",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD E,C",
        opcode=0x59,
        setup=[RegisterValue(Register.C, 0x22)],
        expected=[RegisterValue(Register.E, 0x22)],
        description="Copy C to E",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD E,D",
        opcode=0x5A,
        setup=[RegisterValue(Register.D, 0x33)],
        expected=[RegisterValue(Register.E, 0x33)],
        description="Copy D to E",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD E,E",
        opcode=0x5B,
        setup=[RegisterValue(Register.E, 0x44)],
        expected=[RegisterValue(Register.E, 0x44)],
        description="Copy E to E (identity)",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD E,H",
        opcode=0x5C,
        setup=[RegisterValue(Register.H, 0x55)],
        expected=[RegisterValue(Register.E, 0x55)],
        description="Copy H to E",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD E,L",
        opcode=0x5D,
        setup=[RegisterValue(Register.L, 0x66)],
        expected=[RegisterValue(Register.E, 0x66)],
        description="Copy L to E",
        cycles=1,
    ),
    InstructionTestCase(
        name="LD E,[HL]",
        opcode=0x5E,
        setup=[
            RegisterValue(Register.HL, 0xC400),
            MemoryValue(0xC400, 0xBB),
        ],
        expected=[RegisterValue(Register.E, 0xBB)],
        description="Load from memory pointed by HL into E",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD E,A",
        opcode=0x5F,
        setup=[RegisterValue(Register.A, 0xCC)],
        expected=[RegisterValue(Register.E, 0xCC)],
        description="Copy A to E",
        cycles=1,
    ),
    # Missing A load variants - LD A,H (0x7C) and LD A,[HL] (0x7E)
    InstructionTestCase(
        name="LD A,[HL]",
        opcode=0x7E,
        setup=[
            RegisterValue(Register.HL, 0xC500),
            MemoryValue(0xC500, 0xDD),
        ],
        expected=[RegisterValue(Register.A, 0xDD)],
        description="Load from memory pointed by HL into A",
        cycles=2,
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

# Extended Memory Operations Test Cases - Comprehensive memory addressing coverage
EXTENDED_MEMORY_CASES = [
    # LD (HL),r variants - all registers to memory
    InstructionTestCase(
        name="LD [HL],B - store B to memory",
        opcode=0x70,
        setup=[
            RegisterValue(Register.HL, 0xC100),
            RegisterValue(Register.B, 0x42),
            MemoryValue(0xC100, 0x00),
        ],
        expected=[
            MemoryValue(0xC100, 0x42),
        ],
        description="Store B to memory location pointed by HL",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD [HL],D - store D to memory",
        opcode=0x72,
        setup=[
            RegisterValue(Register.HL, 0xC101),
            RegisterValue(Register.D, 0x8F),
            MemoryValue(0xC101, 0xFF),
        ],
        expected=[
            MemoryValue(0xC101, 0x8F),
        ],
        description="Store D to memory location pointed by HL",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD [HL],H - store H to memory",
        opcode=0x74,
        setup=[
            RegisterValue(Register.HL, 0xC102),  # Set HL directly
            MemoryValue(0xC102, 0xAA),
        ],
        expected=[
            MemoryValue(0xC102, 0xC1),  # H should be 0xC1 (high byte of 0xC102)
        ],
        description="Store H to memory location pointed by HL",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD [HL],L - store L to memory",
        opcode=0x75,
        setup=[
            RegisterValue(Register.HL, 0xC103),  # Set HL directly
            MemoryValue(0xC103, 0x55),
        ],
        expected=[
            MemoryValue(0xC103, 0x03),  # L should be 0x03 (low byte of 0xC103)
        ],
        description="Store L to memory location pointed by HL",
        cycles=2,
    ),
    # LD r,(HL) variants - all registers from memory
    InstructionTestCase(
        name="LD D,[HL] - load D from memory",
        opcode=0x56,
        setup=[
            RegisterValue(Register.HL, 0xC104),
            RegisterValue(Register.D, 0x00),
            MemoryValue(0xC104, 0x77),
        ],
        expected=[
            RegisterValue(Register.D, 0x77),
        ],
        description="Load D from memory location pointed by HL",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD E,[HL] - load E from memory",
        opcode=0x5E,
        setup=[
            RegisterValue(Register.HL, 0xC105),
            RegisterValue(Register.E, 0xFF),
            MemoryValue(0xC105, 0x33),
        ],
        expected=[
            RegisterValue(Register.E, 0x33),
        ],
        description="Load E from memory location pointed by HL",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD H,[HL] - load H from memory",
        opcode=0x66,
        setup=[
            RegisterValue(Register.HL, 0xC106),
            MemoryValue(0xC106, 0x44),
        ],
        expected=[
            RegisterValue(Register.H, 0x44),
        ],
        description="Load H from memory location pointed by HL",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD L,[HL] - load L from memory",
        opcode=0x6E,
        setup=[
            RegisterValue(Register.HL, 0xC107),
            MemoryValue(0xC107, 0x11),
        ],
        expected=[
            RegisterValue(Register.L, 0x11),
        ],
        description="Load L from memory location pointed by HL",
        cycles=2,
    ),
    # Arithmetic operations with (HL)
    InstructionTestCase(
        name="ADD A,[HL] - add memory to A without carry",
        opcode=0x86,
        setup=[
            RegisterValue(Register.A, 0x20),
            RegisterValue(Register.HL, 0xC108),
            MemoryValue(0xC108, 0x15),
        ],
        expected=[
            RegisterValue(Register.A, 0x35),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add memory value to A",
        cycles=2,
    ),
    InstructionTestCase(
        name="ADD A,[HL] - add memory to A with half carry",
        opcode=0x86,
        setup=[
            RegisterValue(Register.A, 0x0F),
            RegisterValue(Register.HL, 0xC109),
            MemoryValue(0xC109, 0x01),
        ],
        expected=[
            RegisterValue(Register.A, 0x10),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, False),
        ],
        description="Add memory to A with half carry",
        cycles=2,
    ),
    InstructionTestCase(
        name="ADD A,[HL] - add memory to A with carry",
        opcode=0x86,
        setup=[
            RegisterValue(Register.A, 0xF0),
            RegisterValue(Register.HL, 0xC10A),
            MemoryValue(0xC10A, 0x20),
        ],
        expected=[
            RegisterValue(Register.A, 0x10),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, True),
        ],
        description="Add memory to A with carry",
        cycles=2,
    ),
    # Increment/Decrement operations with (HL)
    InstructionTestCase(
        name="INC [HL] - increment memory value",
        opcode=0x34,
        setup=[
            RegisterValue(Register.HL, 0xC110),
            MemoryValue(0xC110, 0x10),
        ],
        expected=[
            MemoryValue(0xC110, 0x11),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="Increment memory value at HL",
        cycles=3,
    ),
    InstructionTestCase(
        name="INC [HL] - increment memory with overflow to zero",
        opcode=0x34,
        setup=[
            RegisterValue(Register.HL, 0xC111),
            MemoryValue(0xC111, 0xFF),
        ],
        expected=[
            MemoryValue(0xC111, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="Increment memory value with overflow",
        cycles=3,
    ),
    InstructionTestCase(
        name="DEC [HL] - decrement memory value",
        opcode=0x35,
        setup=[
            RegisterValue(Register.HL, 0xC112),
            MemoryValue(0xC112, 0x20),
        ],
        expected=[
            MemoryValue(0xC112, 0x1F),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="Decrement memory value at HL",
        cycles=3,
    ),
    InstructionTestCase(
        name="DEC [HL] - decrement memory with borrow to zero",
        opcode=0x35,
        setup=[
            RegisterValue(Register.HL, 0xC113),
            MemoryValue(0xC113, 0x01),
        ],
        expected=[
            MemoryValue(0xC113, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
        ],
        description="Decrement memory value to zero",
        cycles=3,
    ),
    # SUB operations with (HL) - these should work
    InstructionTestCase(
        name="SUB A,[HL] - subtract memory from A without borrow",
        opcode=0x96,
        setup=[
            RegisterValue(Register.A, 0x30),
            RegisterValue(Register.HL, 0xC120),
            MemoryValue(0xC120, 0x10),
        ],
        expected=[
            RegisterValue(Register.A, 0x20),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Subtract memory value from A",
        cycles=2,
    ),
    InstructionTestCase(
        name="SUB A,[HL] - subtract memory from A with zero result",
        opcode=0x96,
        setup=[
            RegisterValue(Register.A, 0x55),
            RegisterValue(Register.HL, 0xC121),
            MemoryValue(0xC121, 0x55),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, True),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Subtract memory from A with zero result",
        cycles=2,
    ),
    # Logical operations with (HL) - these should work
    InstructionTestCase(
        name="AND A,[HL] - AND memory with A to zero",
        opcode=0xA6,
        setup=[
            RegisterValue(Register.A, 0xF0),
            RegisterValue(Register.HL, 0xC122),
            MemoryValue(0xC122, 0x0F),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, False),
        ],
        description="AND memory value with A - zero result",
        cycles=2,
    ),
    InstructionTestCase(
        name="OR A,[HL] - OR memory with A",
        opcode=0xB6,
        setup=[
            RegisterValue(Register.A, 0xF0),
            RegisterValue(Register.HL, 0xC123),
            MemoryValue(0xC123, 0x0F),
        ],
        expected=[
            RegisterValue(Register.A, 0xFF),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="OR memory value with A",
        cycles=2,
    ),
    InstructionTestCase(
        name="XOR A,[HL] - XOR memory with A to zero",
        opcode=0xAE,
        setup=[
            RegisterValue(Register.A, 0x55),
            RegisterValue(Register.HL, 0xC124),
            MemoryValue(0xC124, 0x55),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="XOR memory value with A - same pattern",
        cycles=2,
    ),
    # Additional memory load/store variants
    InstructionTestCase(
        name="LD A,[HL] - load A from memory with zero value",
        opcode=0x7E,
        setup=[
            RegisterValue(Register.HL, 0xC125),
            RegisterValue(Register.A, 0xFF),  # Initial value should be overwritten
            MemoryValue(0xC125, 0x00),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),
        ],
        description="Load A from memory location pointed by HL - zero value",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD [HL],A - store A zero to memory",
        opcode=0x77,
        setup=[
            RegisterValue(Register.HL, 0xC126),
            RegisterValue(Register.A, 0x00),
            MemoryValue(0xC126, 0xFF),
        ],
        expected=[
            MemoryValue(0xC126, 0x00),
        ],
        description="Store A to memory location pointed by HL - zero value",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD [HL],A - store A max value to memory",
        opcode=0x77,
        setup=[
            RegisterValue(Register.HL, 0xC127),
            RegisterValue(Register.A, 0xFF),
            MemoryValue(0xC127, 0x00),
        ],
        expected=[
            MemoryValue(0xC127, 0xFF),
        ],
        description="Store A to memory location pointed by HL - max value",
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


# 16-Bit Load Operations Test Cases (28 opcodes)
# Based on reference documentation with cycle counts divided by 4 for test values
LD_16BIT_IMMEDIATE_CASES = [
    # LD BC,nn (0x01) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="LD BC,nn - zero value",
        opcode=0x01,
        setup=[
            RegisterValue(Register.PC, 0xC000),  # Use RAM address
            MemoryValue(0xC000, 0x00),  # Low byte (at PC)
            MemoryValue(0xC001, 0x00),  # High byte
        ],
        expected=[
            RegisterValue(Register.BC, 0x0000),
            RegisterValue(Register.PC, 0xC002),  # PC should increment by 2
        ],
        description="Load immediate zero into BC",
        cycles=3,
    ),
    InstructionTestCase(
        name="LD BC,nn - max value",
        opcode=0x01,
        setup=[
            RegisterValue(Register.PC, 0xC010),  # Use RAM address
            MemoryValue(0xC010, 0xFF),  # Low byte
            MemoryValue(0xC011, 0xFF),  # High byte
        ],
        expected=[
            RegisterValue(Register.BC, 0xFFFF),
            RegisterValue(Register.PC, 0xC012),
        ],
        description="Load immediate max value into BC",
        cycles=3,
    ),
    InstructionTestCase(
        name="LD BC,nn - typical value",
        opcode=0x01,
        setup=[
            RegisterValue(Register.PC, 0xC020),  # Use RAM address
            MemoryValue(0xC020, 0x34),  # Low byte
            MemoryValue(0xC021, 0x12),  # High byte
        ],
        expected=[
            RegisterValue(Register.BC, 0x1234),
            RegisterValue(Register.PC, 0xC022),
        ],
        description="Load immediate typical value into BC",
        cycles=3,
    ),
    # LD DE,nn (0x11) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="LD DE,nn - boundary value 0x8000",
        opcode=0x11,
        setup=[
            RegisterValue(Register.PC, 0xC030),  # Use RAM address
            MemoryValue(0xC030, 0x00),  # Low byte
            MemoryValue(0xC031, 0x80),  # High byte
        ],
        expected=[
            RegisterValue(Register.DE, 0x8000),
            RegisterValue(Register.PC, 0xC032),
        ],
        description="Load boundary value into DE",
        cycles=3,
    ),
    InstructionTestCase(
        name="LD DE,nn - boundary value 0x7FFF",
        opcode=0x11,
        setup=[
            RegisterValue(Register.PC, 0xC040),  # Use RAM address
            MemoryValue(0xC040, 0xFF),  # Low byte
            MemoryValue(0xC041, 0x7F),  # High byte
        ],
        expected=[
            RegisterValue(Register.DE, 0x7FFF),
            RegisterValue(Register.PC, 0xC042),
        ],
        description="Load boundary value into DE",
        cycles=3,
    ),
    # LD HL,nn (0x21) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="LD HL,nn - zero value",
        opcode=0x21,
        setup=[
            RegisterValue(Register.PC, 0xC050),  # Use RAM address
            MemoryValue(0xC050, 0x00),
            MemoryValue(0xC051, 0x00),
        ],
        expected=[
            RegisterValue(Register.HL, 0x0000),
            RegisterValue(Register.PC, 0xC052),
        ],
        description="Load zero into HL",
        cycles=3,
    ),
    InstructionTestCase(
        name="LD HL,nn - max value",
        opcode=0x21,
        setup=[
            RegisterValue(Register.PC, 0xC060),  # Use RAM address
            MemoryValue(0xC060, 0xFF),
            MemoryValue(0xC061, 0xFF),
        ],
        expected=[
            RegisterValue(Register.HL, 0xFFFF),
            RegisterValue(Register.PC, 0xC062),
        ],
        description="Load max value into HL",
        cycles=3,
    ),
    # LD SP,nn (0x31) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="LD SP,nn - typical stack pointer",
        opcode=0x31,
        setup=[
            RegisterValue(Register.PC, 0xC070),  # Use RAM address
            MemoryValue(0xC070, 0xFF),
            MemoryValue(0xC071, 0xC0),
        ],
        expected=[
            RegisterValue(Register.SP, 0xC0FF),
            RegisterValue(Register.PC, 0xC072),
        ],
        description="Load typical stack pointer value",
        cycles=3,
    ),
]


# Special 16-Bit Load Operations
LD_16BIT_SPECIAL_CASES = [
    # LD [nn],SP (0x08) - 20 cycles = 5 test cycles
    InstructionTestCase(
        name="LD [nn],SP - store SP to memory",
        opcode=0x08,
        setup=[
            RegisterValue(Register.PC, 0xC080),  # Use RAM address
            RegisterValue(Register.SP, 0xFFFE),
            MemoryValue(
                0xC080, 0x00
            ),  # Low byte of address (at PC) - use 0xD000 for dest
            MemoryValue(0xC081, 0xD0),  # High byte of address
            MemoryValue(0xD000, 0x00),  # Initial memory value at destination
            MemoryValue(0xD001, 0x00),  # Initial memory value at destination
        ],
        expected=[
            MemoryValue(0xD000, 0xFE),  # SP low byte stored
            MemoryValue(0xD001, 0xFF),  # SP high byte stored
            RegisterValue(Register.PC, 0xC082),
        ],
        description="Store SP to memory location [nn]",
        cycles=5,
    ),
    # LD HL,SP+n (0xF8) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="LD HL,SP+n - positive offset",
        opcode=0xF8,
        setup=[
            RegisterValue(Register.PC, 0xC090),  # Use RAM address
            RegisterValue(Register.SP, 0x1000),
            MemoryValue(0xC090, 0x10),  # Offset n = 0x10 (at PC)
        ],
        expected=[
            RegisterValue(Register.HL, 0x1010),  # SP + 0x10
            RegisterValue(Register.PC, 0xC091),
            FlagValue(Flag.ZERO, False),  # Flags based on result
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="Load HL = SP + positive offset",
        cycles=3,
    ),
    InstructionTestCase(
        name="LD HL,SP+n - negative offset",
        opcode=0xF8,
        setup=[
            RegisterValue(Register.PC, 0xC0A0),  # Use RAM address
            RegisterValue(Register.SP, 0x1000),
            MemoryValue(0xC0A0, 0xF0),  # Offset n = -16 (0xF0 as signed byte, at PC)
        ],
        expected=[
            RegisterValue(Register.HL, 0x0FF0),  # SP + (-16)
            RegisterValue(Register.PC, 0xC0A1),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),  # Half carry occurs due to borrowing
            FlagValue(Flag.CARRY, False),
        ],
        description="Load HL = SP + negative offset",
        cycles=3,
    ),
    InstructionTestCase(
        name="LD HL,SP+n - with half carry",
        opcode=0xF8,
        setup=[
            RegisterValue(Register.PC, 0xC0B0),  # Use RAM address
            RegisterValue(Register.SP, 0x100F),
            MemoryValue(0xC0B0, 0x01),  # Offset causes half carry (at PC)
        ],
        expected=[
            RegisterValue(Register.HL, 0x1010),
            RegisterValue(Register.PC, 0xC0B1),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),  # Half carry occurs
            FlagValue(Flag.CARRY, False),
        ],
        description="Load HL = SP + n with half carry",
        cycles=3,
    ),
    InstructionTestCase(
        name="LD HL,SP+n - with carry",
        opcode=0xF8,
        setup=[
            RegisterValue(Register.PC, 0xC0C0),  # Use RAM address
            RegisterValue(Register.SP, 0xFFF0),
            MemoryValue(0xC0C0, 0x20),  # Offset causes carry (at PC)
        ],
        expected=[
            RegisterValue(Register.HL, 0x0010),  # Overflow wraps around
            RegisterValue(Register.PC, 0xC0C1),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),  # No half carry: 0x0 + 0x2 = 0x2
            FlagValue(Flag.CARRY, True),
        ],
        description="Load HL = SP + n with carry",
        cycles=3,
    ),
    # LD SP,HL (0xF9) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD SP,HL - copy HL to SP",
        opcode=0xF9,
        setup=[
            RegisterValue(Register.HL, 0xC000),
            RegisterValue(Register.SP, 0x0000),  # Initial SP
        ],
        expected=[
            RegisterValue(Register.SP, 0xC000),  # SP should equal HL
        ],
        description="Copy HL to stack pointer",
        cycles=2,
    ),
    InstructionTestCase(
        name="LD SP,HL - boundary value",
        opcode=0xF9,
        setup=[
            RegisterValue(Register.HL, 0xFFFF),
            RegisterValue(Register.SP, 0x0000),
        ],
        expected=[
            RegisterValue(Register.SP, 0xFFFF),
        ],
        description="Copy max HL value to SP",
        cycles=2,
    ),
]

# Comprehensive 8-bit Load Operations Test Cases
COMPREHENSIVE_8BIT_LOADS = [
    # LD A,n (0x3E) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD A,n - immediate value",
        opcode=0x3E,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            MemoryValue(0xC000, 0x55),
        ],
        expected=[
            RegisterValue(Register.A, 0x55),
            RegisterValue(Register.PC, 0xC001),
        ],
        description="Load immediate value into A",
        cycles=2,
    ),
    # LD H,B (0x60) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="LD H,B",
        opcode=0x60,
        setup=[RegisterValue(Register.B, 0x12)],
        expected=[RegisterValue(Register.H, 0x12)],
        description="Copy B to H",
        cycles=1,
    ),
    # LD H,C (0x61) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="LD H,C",
        opcode=0x61,
        setup=[RegisterValue(Register.C, 0x34)],
        expected=[RegisterValue(Register.H, 0x34)],
        description="Copy C to H",
        cycles=1,
    ),
    # LD H,D (0x62) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="LD H,D",
        opcode=0x62,
        setup=[RegisterValue(Register.D, 0x56)],
        expected=[RegisterValue(Register.H, 0x56)],
        description="Copy D to H",
        cycles=1,
    ),
    # LD H,E (0x63) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="LD H,E",
        opcode=0x63,
        setup=[RegisterValue(Register.E, 0x78)],
        expected=[RegisterValue(Register.H, 0x78)],
        description="Copy E to H",
        cycles=1,
    ),
    # LD H,H (0x64) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="LD H,H",
        opcode=0x64,
        setup=[RegisterValue(Register.H, 0x9A)],
        expected=[RegisterValue(Register.H, 0x9A)],
        description="Copy H to H (identity)",
        cycles=1,
    ),
    # LD H,L (0x65) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="LD H,L",
        opcode=0x65,
        setup=[RegisterValue(Register.L, 0xBC)],
        expected=[RegisterValue(Register.H, 0xBC)],
        description="Copy L to H",
        cycles=1,
    ),
    # LD H,(HL) (0x66) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD H,(HL)",
        opcode=0x66,
        setup=[
            RegisterValue(Register.H, 0xC1),  # Set H directly
            RegisterValue(Register.L, 0x00),  # Set L directly to form HL=0xC100
            MemoryValue(0xC100, 0x42),
        ],
        expected=[
            RegisterValue(Register.H, 0x42),
            RegisterValue(Register.L, 0x00),  # L should remain unchanged
        ],
        description="Load H from memory pointed by HL",
        cycles=2,
    ),
    # LD L,(HL) (0x6E) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD L,(HL)",
        opcode=0x6E,
        setup=[
            RegisterValue(Register.H, 0xC1),  # Set H directly
            RegisterValue(Register.L, 0x01),  # Set L directly to form HL=0xC101
            MemoryValue(0xC101, 0x77),
        ],
        expected=[
            RegisterValue(Register.H, 0xC1),  # H should remain unchanged
            RegisterValue(Register.L, 0x77),
        ],
        description="Load L from memory pointed by HL",
        cycles=2,
    ),
    # LD H,A (0x67) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="LD H,A",
        opcode=0x67,
        setup=[RegisterValue(Register.A, 0xDE)],
        expected=[RegisterValue(Register.H, 0xDE)],
        description="Copy A to H",
        cycles=1,
    ),
    # LD L,B (0x68) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="LD L,B",
        opcode=0x68,
        setup=[RegisterValue(Register.B, 0x11)],
        expected=[RegisterValue(Register.L, 0x11)],
        description="Copy B to L",
        cycles=1,
    ),
    # LD L,C (0x69) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="LD L,C",
        opcode=0x69,
        setup=[RegisterValue(Register.C, 0x22)],
        expected=[RegisterValue(Register.L, 0x22)],
        description="Copy C to L",
        cycles=1,
    ),
    # LD L,D (0x6A) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="LD L,D",
        opcode=0x6A,
        setup=[RegisterValue(Register.D, 0x33)],
        expected=[RegisterValue(Register.L, 0x33)],
        description="Copy D to L",
        cycles=1,
    ),
    # LD L,E (0x6B) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="LD L,E",
        opcode=0x6B,
        setup=[RegisterValue(Register.E, 0x44)],
        expected=[RegisterValue(Register.L, 0x44)],
        description="Copy E to L",
        cycles=1,
    ),
    # LD L,H (0x6C) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="LD L,H",
        opcode=0x6C,
        setup=[RegisterValue(Register.H, 0x55)],
        expected=[RegisterValue(Register.L, 0x55)],
        description="Copy H to L",
        cycles=1,
    ),
    # LD L,L (0x6D) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="LD L,L",
        opcode=0x6D,
        setup=[RegisterValue(Register.L, 0x66)],
        expected=[RegisterValue(Register.L, 0x66)],
        description="Copy L to L (identity)",
        cycles=1,
    ),
    # LD L,A (0x6F) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="LD L,A",
        opcode=0x6F,
        setup=[RegisterValue(Register.A, 0x88)],
        expected=[RegisterValue(Register.L, 0x88)],
        description="Copy A to L",
        cycles=1,
    ),
]

# Missing Memory Operations
MISSING_MEMORY_OPS = [
    # LD A,(HLI) (0x2A) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD A,(HLI) - load from memory and increment HL",
        opcode=0x2A,
        setup=[
            RegisterValue(Register.HL, 0xC000),
            RegisterValue(Register.A, 0x00),  # Initial A value
            MemoryValue(0xC000, 0x42),
        ],
        expected=[
            RegisterValue(Register.A, 0x42),  # A loaded from memory
            RegisterValue(Register.HL, 0xC001),  # HL incremented
        ],
        description="Load A from (HL) and increment HL",
        cycles=2,
    ),
    # LD (HLI),A (0x22) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD (HLI),A - store to memory and increment HL",
        opcode=0x22,
        setup=[
            RegisterValue(Register.HL, 0xC100),
            RegisterValue(Register.A, 0x55),
            MemoryValue(0xC100, 0x00),
        ],
        expected=[
            MemoryValue(0xC100, 0x55),  # A stored to memory
            RegisterValue(Register.HL, 0xC101),  # HL incremented
        ],
        description="Store A to (HL) and increment HL",
        cycles=2,
    ),
    # LD A,(HLD) (0x3A) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD A,(HLD) - load from memory and decrement HL",
        opcode=0x3A,
        setup=[
            RegisterValue(Register.HL, 0xC001),
            RegisterValue(Register.A, 0x00),  # Initial A value
            MemoryValue(0xC001, 0x33),
        ],
        expected=[
            RegisterValue(Register.A, 0x33),  # A loaded from memory
            RegisterValue(Register.HL, 0xC000),  # HL decremented
        ],
        description="Load A from (HL) and decrement HL",
        cycles=2,
    ),
    # LD (HLD),A (0x32) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="LD (HLD),A - store to memory and decrement HL",
        opcode=0x32,
        setup=[
            RegisterValue(Register.HL, 0xC101),
            RegisterValue(Register.A, 0x77),
            MemoryValue(0xC101, 0x00),
        ],
        expected=[
            MemoryValue(0xC101, 0x77),  # A stored to memory
            RegisterValue(Register.HL, 0xC100),  # HL decremented
        ],
        description="Store A to (HL) and decrement HL",
        cycles=2,
    ),
]

# Missing LD (HL),n (0x36) operation
LD_HL_IMMEDIATE = [
    InstructionTestCase(
        name="LD (HL),n - store immediate to memory",
        opcode=0x36,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.HL, 0xC100),
            MemoryValue(0xC000, 0x88),  # Immediate value at PC
            MemoryValue(0xC100, 0x00),  # Initial memory value
        ],
        expected=[
            MemoryValue(0xC100, 0x88),  # Memory gets immediate value
            RegisterValue(Register.PC, 0xC001),  # PC incremented
        ],
        description="Store immediate value to memory at HL",
        cycles=3,
    ),
]

# Missing Load Operations
MISSING_LOAD_CASES = [
    InstructionTestCase(
        name="LD DE,nn - load immediate 16-bit",
        opcode=0x11,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            MemoryValue(0xC000, 0x34),  # Low byte
            MemoryValue(0xC001, 0x12),  # High byte (little-endian: 0x1234)
        ],
        expected=[
            RegisterValue(Register.DE, 0x1234),
            RegisterValue(Register.PC, 0xC002),
        ],
        description="Load 16-bit immediate into DE",
        cycles=3,
    ),
    InstructionTestCase(
        name="LD (HL),E - store E to memory",
        opcode=0x73,
        setup=[
            RegisterValue(Register.E, 0x42),
            RegisterValue(Register.HL, 0xC000),
            MemoryValue(0xC000, 0x00),
        ],
        expected=[
            MemoryValue(0xC000, 0x42),
        ],
        description="Store E at address HL",
        cycles=2,
    ),
]

# --- LD HL,SP+n negative offset with carry (covers line 823) ---
LD_HL_SP_NEGATIVE_CARRY_CASES = [
    InstructionTestCase(
        name="LD HL,SP+n - negative offset with carry",
        opcode=0xF8,
        setup=[
            RegisterValue(Register.PC, 0xC090),
            RegisterValue(Register.SP, 0x10FF),
            MemoryValue(0xC090, 0xFF),  # -1 as signed byte
        ],
        expected=[
            RegisterValue(Register.HL, 0x10FE),
            RegisterValue(Register.PC, 0xC091),
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.CARRY, True),
            FlagValue(Flag.HALF_CARRY, True),
        ],
        description="LD HL,SP+(-1) with carry from negative wrap",
        cycles=3,
    ),
]


@pytest.mark.parametrize(
    "test_case", BASIC_LOAD_CASES, ids=[tc.name for tc in BASIC_LOAD_CASES]
)
def test_basic_load_instructions(cpu, test_case):
    """Test basic load instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", LD_REGISTER_CASES, ids=[tc.name for tc in LD_REGISTER_CASES]
)
def test_ld_register_instructions(cpu, test_case):
    """Test 8-bit load register instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", MEMORY_LD_CASES, ids=[tc.name for tc in MEMORY_LD_CASES]
)
def test_memory_ld_operations(cpu, test_case):
    """Test memory LD operations instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", EXTENDED_MEMORY_CASES, ids=[tc.name for tc in EXTENDED_MEMORY_CASES]
)
def test_extended_memory_instructions(cpu, test_case):
    """Test extended memory instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", LD_EDGE_CASES, ids=[tc.name for tc in LD_EDGE_CASES]
)
def test_ld_edge_cases(cpu, test_case):
    """Test LD register edge cases: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    LD_16BIT_IMMEDIATE_CASES,
    ids=[tc.name for tc in LD_16BIT_IMMEDIATE_CASES],
)
def test_ld_16bit_immediate_instructions(cpu, test_case):
    """Test 16-bit immediate load instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", LD_16BIT_SPECIAL_CASES, ids=[tc.name for tc in LD_16BIT_SPECIAL_CASES]
)
def test_ld_16bit_special_instructions(cpu, test_case):
    """Test 16-bit special load instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    COMPREHENSIVE_8BIT_LOADS,
    ids=[tc.name for tc in COMPREHENSIVE_8BIT_LOADS],
)
def test_comprehensive_8bit_loads(cpu, test_case):
    """Test comprehensive 8-bit load instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", MISSING_MEMORY_OPS, ids=[tc.name for tc in MISSING_MEMORY_OPS]
)
def test_missing_memory_instructions(cpu, test_case):
    """Test missing memory instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", LD_HL_IMMEDIATE, ids=[tc.name for tc in LD_HL_IMMEDIATE]
)
def test_ld_hl_immediate_instructions(cpu, test_case):
    """Test LD (HL),n instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    MISSING_LOAD_CASES,
    ids=[tc.name for tc in MISSING_LOAD_CASES],
)
def test_missing_load_instructions(cpu, test_case):
    """Test missing load instruction: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    LD_HL_SP_NEGATIVE_CARRY_CASES,
    ids=[tc.name for tc in LD_HL_SP_NEGATIVE_CARRY_CASES],
)
def test_ld_hl_sp_negative_carry(cpu, test_case):
    """Test LD HL,SP+n negative offset with carry: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"



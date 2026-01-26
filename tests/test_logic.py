import pytest
from helpers import (
    Register, Flag,
    RegisterValue, MemoryValue, FlagValue,
    InstructionTestCase, CPUStateValidator,
)

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

# Extended AND Operations Test Cases (missing H, L variants)
EXTENDED_AND_CASES = [
    InstructionTestCase(
        name="AND A,H - normal case",
        opcode=0xA4,
        setup=[
            RegisterValue(Register.A, 0xF0),
            RegisterValue(Register.H, 0x0F),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # 0xF0 & 0x0F
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),  # AND always sets half carry
            FlagValue(Flag.CARRY, False),
        ],
        description="AND H with A - zero result",
        cycles=1,
    ),
    InstructionTestCase(
        name="AND A,L - non-zero result",
        opcode=0xA5,
        setup=[
            RegisterValue(Register.A, 0x55),
            RegisterValue(Register.L, 0xAA),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # 0x55 & 0xAA
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, False),
        ],
        description="AND L with A - zero result",
        cycles=1,
    ),
    InstructionTestCase(
        name="AND D - mask bits",
        opcode=0xA2,
        setup=[
            RegisterValue(Register.A, 0xFF),
            RegisterValue(Register.D, 0x0F),
        ],
        expected=[
            RegisterValue(Register.A, 0x0F),  # 0xFF & 0x0F
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, False),
        ],
        description="AND D with A - mask high nibble",
        cycles=1,
    ),
    InstructionTestCase(
        name="AND E - zero result",
        opcode=0xA3,
        setup=[
            RegisterValue(Register.A, 0xF0),
            RegisterValue(Register.E, 0x0F),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # 0xF0 & 0x0F
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, True),
            FlagValue(Flag.CARRY, False),
        ],
        description="AND E with A - zero result",
        cycles=1,
    ),
]

# Extended XOR Operations Test Cases (missing H, L variants)
EXTENDED_XOR_CASES = [
    InstructionTestCase(
        name="XOR A,H - normal case",
        opcode=0xAC,
        setup=[
            RegisterValue(Register.A, 0xF0),
            RegisterValue(Register.H, 0x0F),
        ],
        expected=[
            RegisterValue(Register.A, 0xFF),  # 0xF0 ^ 0x0F
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="XOR H with A - all bits set",
        cycles=1,
    ),
    InstructionTestCase(
        name="XOR A,L - zero result",
        opcode=0xAD,
        setup=[
            RegisterValue(Register.A, 0x55),
            RegisterValue(Register.L, 0x55),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # 0x55 ^ 0x55
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="XOR L with A - zero result",
        cycles=1,
    ),
    InstructionTestCase(
        name="XOR D - toggle bits",
        opcode=0xAA,
        setup=[
            RegisterValue(Register.A, 0xFF),
            RegisterValue(Register.D, 0x0F),
        ],
        expected=[
            RegisterValue(Register.A, 0xF0),  # 0xFF ^ 0x0F
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="XOR D with A",
        cycles=1,
    ),
    InstructionTestCase(
        name="XOR E - self cancel",
        opcode=0xAB,
        setup=[
            RegisterValue(Register.A, 0x55),
            RegisterValue(Register.E, 0x55),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # 0x55 ^ 0x55
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="XOR E with A - zero result",
        cycles=1,
    ),
]

# Extended OR Operations Test Cases (missing H, L variants)
EXTENDED_OR_CASES = [
    InstructionTestCase(
        name="OR A,H - normal case",
        opcode=0xB4,
        setup=[
            RegisterValue(Register.A, 0x80),
            RegisterValue(Register.H, 0x01),
        ],
        expected=[
            RegisterValue(Register.A, 0x81),  # 0x80 | 0x01
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="OR H with A - set bit 0",
        cycles=1,
    ),
    InstructionTestCase(
        name="OR A,L - all bits set",
        opcode=0xB5,
        setup=[
            RegisterValue(Register.A, 0x80),
            RegisterValue(Register.L, 0x7F),
        ],
        expected=[
            RegisterValue(Register.A, 0xFF),  # 0x80 | 0x7F
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="OR L with A - all bits set",
        cycles=1,
    ),
    InstructionTestCase(
        name="OR D - combine bits",
        opcode=0xB2,
        setup=[
            RegisterValue(Register.A, 0xF0),
            RegisterValue(Register.D, 0x0F),
        ],
        expected=[
            RegisterValue(Register.A, 0xFF),  # 0xF0 | 0x0F
            FlagValue(Flag.ZERO, False),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="OR D with A - combine nibbles",
        cycles=1,
    ),
    InstructionTestCase(
        name="OR E - zero result",
        opcode=0xB3,
        setup=[
            RegisterValue(Register.A, 0x00),
            RegisterValue(Register.E, 0x00),
        ],
        expected=[
            RegisterValue(Register.A, 0x00),  # 0x00 | 0x00
            FlagValue(Flag.ZERO, True),
            FlagValue(Flag.SUB, False),
            FlagValue(Flag.HALF_CARRY, False),
            FlagValue(Flag.CARRY, False),
        ],
        description="OR E with A - zero result",
        cycles=1,
    ),
]


@pytest.mark.parametrize(
    "test_case",
    LOGICAL_OPERATIONS_CASES,
    ids=[tc.name for tc in LOGICAL_OPERATIONS_CASES],
)
def test_logical_operations(cpu, test_case):
    """Test logical operations instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", EXTENDED_AND_CASES, ids=[tc.name for tc in EXTENDED_AND_CASES]
)
def test_extended_and_instructions(cpu, test_case):
    """Test extended AND instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", EXTENDED_XOR_CASES, ids=[tc.name for tc in EXTENDED_XOR_CASES]
)
def test_extended_xor_instructions(cpu, test_case):
    """Test extended XOR instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", EXTENDED_OR_CASES, ids=[tc.name for tc in EXTENDED_OR_CASES]
)
def test_extended_or_instructions(cpu, test_case):
    """Test extended OR instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"



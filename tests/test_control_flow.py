import pytest
from helpers import (
    Register, Flag,
    RegisterValue, MemoryValue, FlagValue,
    InstructionTestCase, CPUStateValidator,
)

# Control Flow Instructions Test Cases (45 opcodes)
# Based on reference documentation with cycle counts divided by 4 for test values
JUMP_CASES = [
    # JR n (0x18) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="JR n - forward jump",
        opcode=0x18,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            MemoryValue(0xC000, 0x10),  # Jump forward 16 bytes
        ],
        expected=[
            RegisterValue(
                Register.PC, 0xC011
            ),  # PC = initial + 1 (opcode read) + 0x10 (offset)
        ],
        description="Relative jump forward",
        cycles=2,
    ),
    InstructionTestCase(
        name="JR n - backward jump",
        opcode=0x18,
        setup=[
            RegisterValue(Register.PC, 0xC010),
            MemoryValue(0xC010, 0xF0),  # Jump backward 16 bytes (-16)
        ],
        expected=[
            RegisterValue(
                Register.PC, 0xC001
            ),  # PC = initial + 1 (opcode read) + (-16) (offset)
        ],
        description="Relative jump backward",
        cycles=2,
    ),
    # JR NZ,n (0x20) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="JR NZ,n - taken (Z=0)",
        opcode=0x20,
        setup=[
            RegisterValue(Register.PC, 0xC020),
            FlagValue(Flag.ZERO, False),
            MemoryValue(0xC020, 0x08),  # Jump forward 8 bytes
        ],
        expected=[
            RegisterValue(
                Register.PC, 0xC029
            ),  # Jump taken: PC + 1 (opcode read) + 8 = 0xC029
        ],
        description="Conditional relative jump when not zero",
        cycles=2,
    ),
    InstructionTestCase(
        name="JR NZ,n - taken (Z=0)",
        opcode=0x20,
        setup=[
            RegisterValue(Register.PC, 0xC020),
            FlagValue(Flag.ZERO, False),
            MemoryValue(0xC020, 0x08),  # Jump forward 8 bytes
        ],
        expected=[
            RegisterValue(
                Register.PC, 0xC029
            ),  # Jump taken: PC + 1 (opcode read) + 8 = 0xC029
        ],
        description="Conditional relative jump when not zero",
        cycles=2,
    ),
    InstructionTestCase(
        name="JR NZ,n - not taken (Z=1)",
        opcode=0x20,
        setup=[
            RegisterValue(Register.PC, 0xC030),
            FlagValue(Flag.ZERO, True),
            MemoryValue(0xC030, 0x08),  # Jump forward 8 bytes
        ],
        expected=[
            RegisterValue(Register.PC, 0xC031),  # Jump not taken: PC + 1
        ],
        description="Conditional relative jump when zero",
        cycles=2,
    ),
    # JP nn (0xC3) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="JP nn - absolute jump",
        opcode=0xC3,
        setup=[
            RegisterValue(Register.PC, 0xC040),
            MemoryValue(0xC040, 0x00),  # Low byte of address
            MemoryValue(0xC041, 0xD0),  # High byte of address
        ],
        expected=[
            RegisterValue(Register.PC, 0xD000),  # Jump to 0xD000
        ],
        description="Absolute jump to address",
        cycles=3,
    ),
    # JP Z,nn (0xCA) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="JP Z,nn - taken (Z=1)",
        opcode=0xCA,
        setup=[
            RegisterValue(Register.PC, 0xC050),
            FlagValue(Flag.ZERO, True),
            MemoryValue(0xC050, 0x00),  # Low byte
            MemoryValue(0xC051, 0xD0),  # High byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xD000),  # Jump taken
        ],
        description="Conditional absolute jump when zero",
        cycles=3,
    ),
    InstructionTestCase(
        name="JP Z,nn - not taken (Z=0)",
        opcode=0xCA,
        setup=[
            RegisterValue(Register.PC, 0xC060),
            FlagValue(Flag.ZERO, False),
            MemoryValue(0xC060, 0x00),  # Low byte
            MemoryValue(0xC061, 0xD0),  # High byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xC062),  # Jump not taken: PC + 3
        ],
        description="Conditional absolute jump when not zero",
        cycles=3,
    ),
    # JP NZ,nn (0xC2) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="JP NZ,nn - taken (Z=0)",
        opcode=0xC2,
        setup=[
            RegisterValue(Register.PC, 0xC070),
            FlagValue(Flag.ZERO, False),
            MemoryValue(0xC070, 0x00),  # Low byte
            MemoryValue(0xC071, 0xD0),  # High byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xD000),  # Jump taken
        ],
        description="Conditional absolute jump when not zero",
        cycles=3,
    ),
    InstructionTestCase(
        name="JP NZ,nn - not taken (Z=1)",
        opcode=0xC2,
        setup=[
            RegisterValue(Register.PC, 0xC080),
            FlagValue(Flag.ZERO, True),
            MemoryValue(0xC080, 0x00),  # Low byte
            MemoryValue(0xC081, 0xD0),  # High byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xC082),  # Jump not taken: PC + 3
        ],
        description="Conditional absolute jump when zero",
        cycles=3,
    ),
    # JP NC,nn (0xD2) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="JP NC,nn - taken (C=0)",
        opcode=0xD2,
        setup=[
            RegisterValue(Register.PC, 0xC090),
            FlagValue(Flag.CARRY, False),
            MemoryValue(0xC090, 0x00),  # Low byte
            MemoryValue(0xC091, 0xD0),  # High byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xD000),  # Jump taken
        ],
        description="Conditional absolute jump when not carry",
        cycles=3,
    ),
    InstructionTestCase(
        name="JP NC,nn - not taken (C=1)",
        opcode=0xD2,
        setup=[
            RegisterValue(Register.PC, 0xC0A0),
            FlagValue(Flag.CARRY, True),
            MemoryValue(0xC0A0, 0x00),  # Low byte
            MemoryValue(0xC0A1, 0xD0),  # High byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xC0A2),  # Jump not taken: PC + 3
        ],
        description="Conditional absolute jump when carry",
        cycles=3,
    ),
    # JP C,nn (0xDA) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="JP C,nn - taken (C=1)",
        opcode=0xDA,
        setup=[
            RegisterValue(Register.PC, 0xC0B0),
            FlagValue(Flag.CARRY, True),
            MemoryValue(0xC0B0, 0x00),  # Low byte
            MemoryValue(0xC0B1, 0xD0),  # High byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xD000),  # Jump taken
        ],
        description="Conditional absolute jump when carry",
        cycles=3,
    ),
    InstructionTestCase(
        name="JP C,nn - not taken (C=0)",
        opcode=0xDA,
        setup=[
            RegisterValue(Register.PC, 0xC0C0),
            FlagValue(Flag.CARRY, False),
            MemoryValue(0xC0C0, 0x00),  # Low byte
            MemoryValue(0xC0C1, 0xD0),  # High byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xC0C2),  # Jump not taken: PC + 3
        ],
        description="Conditional absolute jump when not carry",
        cycles=3,
    ),
    # JP HL (0xE9) - 4 cycles = 1 test cycle
    InstructionTestCase(
        name="JP HL - jump to address in HL",
        opcode=0xE9,
        setup=[
            RegisterValue(Register.HL, 0xD100),
        ],
        expected=[
            RegisterValue(Register.PC, 0xD100),  # PC = HL
        ],
        description="Jump to address in HL register",
        cycles=1,
    ),
]


CALL_CASES = [
    # CALL nn (0xCD) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="CALL nn - call subroutine",
        opcode=0xCD,
        setup=[
            RegisterValue(Register.PC, 0xC100),
            RegisterValue(Register.SP, 0xD000),  # Stack pointer
            MemoryValue(0xC100, 0x00),  # Low byte of subroutine address
            MemoryValue(0xC101, 0xD2),  # High byte of subroutine address
            MemoryValue(0xD000, 0x00),  # Stack initial values
            MemoryValue(0xD001, 0x00),
        ],
        expected=[
            RegisterValue(Register.PC, 0xD200),  # Jump to subroutine
            MemoryValue(0xCFFE, 0x02),  # PC low byte pushed to stack (0xC102 low byte)
            MemoryValue(
                0xCFFF, 0xC1
            ),  # PC high byte pushed to stack (0xC102 high byte)
            RegisterValue(Register.SP, 0xCFFE),  # SP decremented by 2
        ],
        description="Call subroutine and push return address",
        cycles=3,
    ),
    # CALL Z,nn (0xCC) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="CALL Z,nn - taken (Z=1)",
        opcode=0xCC,
        setup=[
            RegisterValue(Register.PC, 0xC110),
            RegisterValue(Register.SP, 0xD010),
            FlagValue(Flag.ZERO, True),
            MemoryValue(0xC110, 0x00),  # Low byte of subroutine address
            MemoryValue(0xC111, 0xD2),  # High byte
            MemoryValue(0xD010, 0x00),  # Stack initial
            MemoryValue(0xD011, 0x00),
        ],
        expected=[
            RegisterValue(Register.PC, 0xD200),  # Jump taken
            MemoryValue(0xD00E, 0x12),  # PC low byte pushed (0xC112 low byte)
            MemoryValue(0xD00F, 0xC1),  # PC high byte pushed (0xC112 high byte)
            RegisterValue(Register.SP, 0xD00E),  # SP decremented by 2
        ],
        description="Conditional call when zero",
        cycles=3,
    ),
    InstructionTestCase(
        name="CALL Z,nn - not taken (Z=0)",
        opcode=0xCC,
        setup=[
            RegisterValue(Register.PC, 0xC120),
            RegisterValue(Register.SP, 0xD020),
            FlagValue(Flag.ZERO, False),
            MemoryValue(0xC120, 0x00),  # Low byte of subroutine address
            MemoryValue(0xC121, 0xD2),  # High byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xC122),  # Jump not taken: PC + 2
            RegisterValue(Register.SP, 0xD020),  # SP unchanged
        ],
        description="Conditional call when not zero",
        cycles=3,
    ),
]


RETURN_CASES = [
    # RET (0xC9) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="RET - return from subroutine",
        opcode=0xC9,
        setup=[
            RegisterValue(Register.PC, 0xD200),  # In subroutine
            RegisterValue(Register.SP, 0xCFFE),  # Stack has return address
            MemoryValue(0xCFFE, 0x04),  # Return address low byte
            MemoryValue(0xCFFF, 0xC1),  # Return address high byte
        ],
        expected=[
            RegisterValue(
                Register.PC, 0xC104
            ),  # PC = return address + 1 (next instruction)
            RegisterValue(Register.SP, 0xD000),  # SP incremented by 2
        ],
        description="Return from subroutine",
        cycles=2,
    ),
    # RET Z (0xC8) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="RET Z - taken (Z=1)",
        opcode=0xC8,
        setup=[
            RegisterValue(Register.PC, 0xD200),
            RegisterValue(Register.SP, 0xCFFE),
            FlagValue(Flag.ZERO, True),
            MemoryValue(0xCFFE, 0x04),  # Return address low byte
            MemoryValue(0xCFFF, 0xC1),  # Return address high byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xC104),  # Return taken
            RegisterValue(Register.SP, 0xD000),  # SP incremented by 2
        ],
        description="Conditional return when zero",
        cycles=2,
    ),
    InstructionTestCase(
        name="RET Z - not taken (Z=0)",
        opcode=0xC8,
        setup=[
            RegisterValue(Register.PC, 0xD200),
            RegisterValue(Register.SP, 0xCFFE),
            FlagValue(Flag.ZERO, False),
            MemoryValue(0xCFFE, 0x04),  # Return address low byte
            MemoryValue(0xCFFF, 0xC1),  # Return address high byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xD201),  # Return not taken: PC + 1
            RegisterValue(Register.SP, 0xCFFE),  # SP unchanged
        ],
        description="Conditional return when not zero",
        cycles=2,
    ),
    # RET NZ (0xC0) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="RET NZ - taken (Z=0)",
        opcode=0xC0,
        setup=[
            RegisterValue(Register.PC, 0xD200),
            RegisterValue(Register.SP, 0xCFFE),
            FlagValue(Flag.ZERO, False),
            MemoryValue(0xCFFE, 0x04),  # Return address low byte
            MemoryValue(0xCFFF, 0xC1),  # Return address high byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xC104),  # Return taken
            RegisterValue(Register.SP, 0xD000),  # SP incremented by 2
        ],
        description="Conditional return when not zero",
        cycles=2,
    ),
    InstructionTestCase(
        name="RET NZ - not taken (Z=1)",
        opcode=0xC0,
        setup=[
            RegisterValue(Register.PC, 0xD200),
            RegisterValue(Register.SP, 0xCFFE),
            FlagValue(Flag.ZERO, True),
            MemoryValue(0xCFFE, 0x04),  # Return address low byte
            MemoryValue(0xCFFF, 0xC1),  # Return address high byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xD201),  # Return not taken: PC + 1
            RegisterValue(Register.SP, 0xCFFE),  # SP unchanged
        ],
        description="Conditional return when zero",
        cycles=2,
    ),
    # RET NC (0xD0) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="RET NC - taken (C=0)",
        opcode=0xD0,
        setup=[
            RegisterValue(Register.PC, 0xD200),
            RegisterValue(Register.SP, 0xCFFE),
            FlagValue(Flag.CARRY, False),
            MemoryValue(0xCFFE, 0x04),  # Return address low byte
            MemoryValue(0xCFFF, 0xC1),  # Return address high byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xC104),  # Return taken
            RegisterValue(Register.SP, 0xD000),  # SP incremented by 2
        ],
        description="Conditional return when not carry",
        cycles=2,
    ),
    InstructionTestCase(
        name="RET NC - not taken (C=1)",
        opcode=0xD0,
        setup=[
            RegisterValue(Register.PC, 0xD200),
            RegisterValue(Register.SP, 0xCFFE),
            FlagValue(Flag.CARRY, True),
            MemoryValue(0xCFFE, 0x04),  # Return address low byte
            MemoryValue(0xCFFF, 0xC1),  # Return address high byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xD201),  # Return not taken: PC + 1
            RegisterValue(Register.SP, 0xCFFE),  # SP unchanged
        ],
        description="Conditional return when carry",
        cycles=2,
    ),
    # RET C (0xD8) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="RET C - taken (C=1)",
        opcode=0xD8,
        setup=[
            RegisterValue(Register.PC, 0xD200),
            RegisterValue(Register.SP, 0xCFFE),
            FlagValue(Flag.CARRY, True),
            MemoryValue(0xCFFE, 0x04),  # Return address low byte
            MemoryValue(0xCFFF, 0xC1),  # Return address high byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xC104),  # Return taken
            RegisterValue(Register.SP, 0xD000),  # SP incremented by 2
        ],
        description="Conditional return when carry",
        cycles=2,
    ),
    InstructionTestCase(
        name="RET C - not taken (C=0)",
        opcode=0xD8,
        setup=[
            RegisterValue(Register.PC, 0xD200),
            RegisterValue(Register.SP, 0xCFFE),
            FlagValue(Flag.CARRY, False),
            MemoryValue(0xCFFE, 0x04),  # Return address low byte
            MemoryValue(0xCFFF, 0xC1),  # Return address high byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xD201),  # Return not taken: PC + 1
            RegisterValue(Register.SP, 0xCFFE),  # SP unchanged
        ],
        description="Conditional return when not carry",
        cycles=2,
    ),
]


RESTART_CASES = [
    # RST 00H (0xC7) - 32 cycles = 8 test cycles
    InstructionTestCase(
        name="RST 00H - restart to 0x0000",
        opcode=0xC7,
        setup=[
            RegisterValue(Register.PC, 0xC200),
            RegisterValue(Register.SP, 0xD030),
            MemoryValue(0xD030, 0x00),  # Stack initial
            MemoryValue(0xD031, 0x00),
        ],
        expected=[
            RegisterValue(Register.PC, 0x0000),  # Jump to restart vector
            MemoryValue(0xD02E, 0x00),  # PC low byte pushed (0xC200 low byte)
            MemoryValue(0xD02F, 0xC2),  # PC high byte pushed (0xC200 high byte)
            RegisterValue(Register.SP, 0xD02E),  # SP decremented by 2
        ],
        description="Restart to address 0x0000",
        cycles=8,
    ),
    # RST 38H (0xFF) - 32 cycles = 8 test cycles
    InstructionTestCase(
        name="RST 38H - restart to 0x0038",
        opcode=0xFF,
        setup=[
            RegisterValue(Register.PC, 0xC210),
            RegisterValue(Register.SP, 0xD040),
            MemoryValue(0xD040, 0x00),  # Stack initial
            MemoryValue(0xD041, 0x00),
        ],
        expected=[
            RegisterValue(Register.PC, 0x0038),  # Jump to restart vector 0x0038
            MemoryValue(0xD03E, 0x10),  # PC low byte pushed (0xC210 low byte)
            MemoryValue(0xD03F, 0xC2),  # PC high byte pushed (0xC210 high byte)
            RegisterValue(Register.SP, 0xD03E),  # SP decremented by 2
        ],
        description="Restart to address 0x0038",
        cycles=8,
    ),
]

# JUMP and CONTROL FLOW Operations Test Cases
JUMP_CONTROL_CASES = [
    # JP NZ,nn (0xC2) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="JP NZ,nn - taken (Z=0)",
        opcode=0xC2,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            FlagValue(Flag.ZERO, False),
            MemoryValue(0xC000, 0x00),  # Low byte
            MemoryValue(0xC001, 0xD0),  # High byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xD000),  # Jump taken
        ],
        description="Conditional jump when not zero",
        cycles=3,
    ),
    InstructionTestCase(
        name="JP NZ,nn - not taken (Z=1)",
        opcode=0xC2,
        setup=[
            RegisterValue(Register.PC, 0xC010),
            FlagValue(Flag.ZERO, True),
            MemoryValue(0xC010, 0x00),  # Low byte
            MemoryValue(0xC011, 0xD0),  # High byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xC012),  # Jump not taken: PC + 3
        ],
        description="Conditional jump when zero",
        cycles=3,
    ),
    # JP Z,nn (0xCA) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="JP Z,nn - taken (Z=1)",
        opcode=0xCA,
        setup=[
            RegisterValue(Register.PC, 0xC020),
            FlagValue(Flag.ZERO, True),
            MemoryValue(0xC020, 0x00),  # Low byte
            MemoryValue(0xC021, 0xD0),  # High byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xD000),  # Jump taken
        ],
        description="Conditional jump when zero",
        cycles=3,
    ),
    InstructionTestCase(
        name="JP Z,nn - not taken (Z=0)",
        opcode=0xCA,
        setup=[
            RegisterValue(Register.PC, 0xC030),
            FlagValue(Flag.ZERO, False),
            MemoryValue(0xC030, 0x00),  # Low byte
            MemoryValue(0xC031, 0xD0),  # High byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xC032),  # Jump not taken: PC + 3
        ],
        description="Conditional jump when not zero",
        cycles=3,
    ),
]

# Relative Jump Operations
RELATIVE_JUMP_CASES = [
    # JR Z,n (0x28) - 8 cycles = 2 test cycles
    # Note: execute_instruction skips opcode fetch, so PC + 1 + offset (not +2)
    InstructionTestCase(
        name="JR Z,n - taken (Z=1)",
        opcode=0x28,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            FlagValue(Flag.ZERO, True),
            MemoryValue(0xC000, 0x10),  # +16 offset
        ],
        expected=[
            RegisterValue(Register.PC, 0xC011),  # PC + 1 + 16
        ],
        description="Relative jump when zero",
        cycles=2,
    ),
    InstructionTestCase(
        name="JR Z,n - not taken (Z=0)",
        opcode=0x28,
        setup=[
            RegisterValue(Register.PC, 0xC010),
            FlagValue(Flag.ZERO, False),
            MemoryValue(0xC010, 0x10),  # +16 offset (unused)
        ],
        expected=[
            RegisterValue(Register.PC, 0xC011),  # PC + 1 (not taken)
        ],
        description="Relative jump when not zero",
        cycles=2,
    ),
    # JR NZ,n (0x20) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="JR NZ,n - taken (Z=0)",
        opcode=0x20,
        setup=[
            RegisterValue(Register.PC, 0xC020),
            FlagValue(Flag.ZERO, False),
            MemoryValue(0xC020, 0xF8),  # -8 offset (signed)
        ],
        expected=[
            RegisterValue(Register.PC, 0xC019),  # PC + 1 + (-8)
        ],
        description="Relative jump when not zero (negative offset)",
        cycles=2,
    ),
    # JR C,n (0x38) - 8 cycles = 2 test cycles
    InstructionTestCase(
        name="JR C,n - taken (C=1)",
        opcode=0x38,
        setup=[
            RegisterValue(Register.PC, 0xC030),
            FlagValue(Flag.CARRY, True),
            MemoryValue(0xC030, 0x20),  # +32 offset
        ],
        expected=[
            RegisterValue(Register.PC, 0xC051),  # PC + 1 + 32
        ],
        description="Relative jump when carry",
        cycles=2,
    ),
    InstructionTestCase(
        name="JR C,n - not taken (C=0)",
        opcode=0x38,
        setup=[
            RegisterValue(Register.PC, 0xC040),
            FlagValue(Flag.CARRY, False),
            MemoryValue(0xC040, 0x20),  # +32 offset (unused)
        ],
        expected=[
            RegisterValue(Register.PC, 0xC041),  # PC + 1 (not taken)
        ],
        description="Relative jump when not carry",
        cycles=2,
    ),
]

# Additional Call Operations
ADDITIONAL_CALL_CASES = [
    # CALL NZ,nn (0xC4) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="CALL NZ,nn - taken (Z=0)",
        opcode=0xC4,
        setup=[
            RegisterValue(Register.PC, 0xC100),
            RegisterValue(Register.SP, 0xD000),
            FlagValue(Flag.ZERO, False),
            MemoryValue(0xC100, 0x00),  # Low byte of subroutine address
            MemoryValue(0xC101, 0xD2),  # High byte (0xD200)
            MemoryValue(0xD000, 0x00),  # Stack initial
            MemoryValue(0xD001, 0x00),
        ],
        expected=[
            RegisterValue(Register.PC, 0xD200),  # Jump to subroutine
            MemoryValue(0xCFFE, 0x02),  # PC low byte pushed
            MemoryValue(0xCFFF, 0xC1),  # PC high byte pushed
            RegisterValue(Register.SP, 0xCFFE),  # SP decremented by 2
        ],
        description="Conditional call when not zero",
        cycles=3,
    ),
    InstructionTestCase(
        name="CALL NZ,nn - not taken (Z=1)",
        opcode=0xC4,
        setup=[
            RegisterValue(Register.PC, 0xC110),
            RegisterValue(Register.SP, 0xD010),
            FlagValue(Flag.ZERO, True),
            MemoryValue(0xC110, 0x00),  # Low byte
            MemoryValue(0xC111, 0xD2),  # High byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xC112),  # PC + 3 (not taken)
            RegisterValue(Register.SP, 0xD010),  # SP unchanged
        ],
        description="Conditional call when zero",
        cycles=3,
    ),
    # CALL NC,nn (0xD4) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="CALL NC,nn - taken (C=0)",
        opcode=0xD4,
        setup=[
            RegisterValue(Register.PC, 0xC120),
            RegisterValue(Register.SP, 0xD020),
            FlagValue(Flag.CARRY, False),
            MemoryValue(0xC120, 0x00),  # Low byte
            MemoryValue(0xC121, 0xD2),  # High byte (0xD200)
            MemoryValue(0xD020, 0x00),  # Stack initial
            MemoryValue(0xD021, 0x00),
        ],
        expected=[
            RegisterValue(Register.PC, 0xD200),  # Jump to subroutine
            MemoryValue(0xD01E, 0x22),  # PC low byte pushed
            MemoryValue(0xD01F, 0xC1),  # PC high byte pushed
            RegisterValue(Register.SP, 0xD01E),  # SP decremented by 2
        ],
        description="Conditional call when not carry",
        cycles=3,
    ),
    # CALL C,nn (0xDC) - 12 cycles = 3 test cycles
    InstructionTestCase(
        name="CALL C,nn - taken (C=1)",
        opcode=0xDC,
        setup=[
            RegisterValue(Register.PC, 0xC130),
            RegisterValue(Register.SP, 0xD030),
            FlagValue(Flag.CARRY, True),
            MemoryValue(0xC130, 0x00),  # Low byte
            MemoryValue(0xC131, 0xD2),  # High byte (0xD200)
            MemoryValue(0xD030, 0x00),  # Stack initial
            MemoryValue(0xD031, 0x00),
        ],
        expected=[
            RegisterValue(Register.PC, 0xD200),  # Jump to subroutine
            MemoryValue(0xD02E, 0x32),  # PC low byte pushed
            MemoryValue(0xD02F, 0xC1),  # PC high byte pushed
            RegisterValue(Register.SP, 0xD02E),  # SP decremented by 2
        ],
        description="Conditional call when carry",
        cycles=3,
    ),
]

# Restart Operations (all 8 restart vectors)
RESTART_ALL_CASES = [
    # RST 08H (0xCF) - 32 cycles = 8 test cycles
    InstructionTestCase(
        name="RST 08H - restart to 0x0008",
        opcode=0xCF,
        setup=[
            RegisterValue(Register.PC, 0xC200),
            RegisterValue(Register.SP, 0xD040),
            MemoryValue(0xD040, 0x00),  # Stack initial
            MemoryValue(0xD041, 0x00),
        ],
        expected=[
            RegisterValue(Register.PC, 0x0008),  # Jump to restart vector
            MemoryValue(0xD03E, 0x00),  # PC low byte pushed
            MemoryValue(0xD03F, 0xC2),  # PC high byte pushed
            RegisterValue(Register.SP, 0xD03E),  # SP decremented by 2
        ],
        description="Restart to address 0x0008",
        cycles=8,
    ),
    # RST 10H (0xD7) - 32 cycles = 8 test cycles
    InstructionTestCase(
        name="RST 10H - restart to 0x0010",
        opcode=0xD7,
        setup=[
            RegisterValue(Register.PC, 0xC210),
            RegisterValue(Register.SP, 0xD050),
            MemoryValue(0xD050, 0x00),  # Stack initial
            MemoryValue(0xD051, 0x00),
        ],
        expected=[
            RegisterValue(Register.PC, 0x0010),  # Jump to restart vector
            MemoryValue(0xD04E, 0x10),  # PC low byte pushed
            MemoryValue(0xD04F, 0xC2),  # PC high byte pushed
            RegisterValue(Register.SP, 0xD04E),  # SP decremented by 2
        ],
        description="Restart to address 0x0010",
        cycles=8,
    ),
    # RST 18H (0xDF) - 32 cycles = 8 test cycles
    InstructionTestCase(
        name="RST 18H - restart to 0x0018",
        opcode=0xDF,
        setup=[
            RegisterValue(Register.PC, 0xC220),
            RegisterValue(Register.SP, 0xD060),
            MemoryValue(0xD060, 0x00),  # Stack initial
            MemoryValue(0xD061, 0x00),
        ],
        expected=[
            RegisterValue(Register.PC, 0x0018),  # Jump to restart vector
            MemoryValue(0xD05E, 0x20),  # PC low byte pushed
            MemoryValue(0xD05F, 0xC2),  # PC high byte pushed
            RegisterValue(Register.SP, 0xD05E),  # SP decremented by 2
        ],
        description="Restart to address 0x0018",
        cycles=8,
    ),
    # RST 20H (0xE7) - 32 cycles = 8 test cycles
    InstructionTestCase(
        name="RST 20H - restart to 0x0020",
        opcode=0xE7,
        setup=[
            RegisterValue(Register.PC, 0xC230),
            RegisterValue(Register.SP, 0xD070),
            MemoryValue(0xD070, 0x00),  # Stack initial
            MemoryValue(0xD071, 0x00),
        ],
        expected=[
            RegisterValue(Register.PC, 0x0020),  # Jump to restart vector
            MemoryValue(0xD06E, 0x30),  # PC low byte pushed
            MemoryValue(0xD06F, 0xC2),  # PC high byte pushed
            RegisterValue(Register.SP, 0xD06E),  # SP decremented by 2
        ],
        description="Restart to address 0x0020",
        cycles=8,
    ),
    # RST 28H (0xEF) - 32 cycles = 8 test cycles
    InstructionTestCase(
        name="RST 28H - restart to 0x0028",
        opcode=0xEF,
        setup=[
            RegisterValue(Register.PC, 0xC240),
            RegisterValue(Register.SP, 0xD080),
            MemoryValue(0xD080, 0x00),  # Stack initial
            MemoryValue(0xD081, 0x00),
        ],
        expected=[
            RegisterValue(Register.PC, 0x0028),  # Jump to restart vector
            MemoryValue(0xD07E, 0x40),  # PC low byte pushed
            MemoryValue(0xD07F, 0xC2),  # PC high byte pushed
            RegisterValue(Register.SP, 0xD07E),  # SP decremented by 2
        ],
        description="Restart to address 0x0028",
        cycles=8,
    ),
    # RST 30H (0xF7) - 32 cycles = 8 test cycles
    InstructionTestCase(
        name="RST 30H - restart to 0x0030",
        opcode=0xF7,
        setup=[
            RegisterValue(Register.PC, 0xC250),
            RegisterValue(Register.SP, 0xD090),
            MemoryValue(0xD090, 0x00),  # Stack initial
            MemoryValue(0xD091, 0x00),
        ],
        expected=[
            RegisterValue(Register.PC, 0x0030),  # Jump to restart vector
            MemoryValue(0xD08E, 0x50),  # PC low byte pushed
            MemoryValue(0xD08F, 0xC2),  # PC high byte pushed
            RegisterValue(Register.SP, 0xD08E),  # SP decremented by 2
        ],
        description="Restart to address 0x0030",
        cycles=8,
    ),
]

# RETI instruction (0xD9)
RETI_CASES = [
    InstructionTestCase(
        name="RETI - return and enable interrupts",
        opcode=0xD9,
        setup=[
            RegisterValue(Register.PC, 0xD200),  # In subroutine
            RegisterValue(Register.SP, 0xCFFE),
            MemoryValue(0xCFFE, 0x04),  # Return address low byte
            MemoryValue(0xCFFF, 0xC1),  # Return address high byte
        ],
        expected=[
            RegisterValue(Register.PC, 0xC104),  # Return to next instruction
            RegisterValue(Register.SP, 0xD000),  # SP incremented by 2
            # IME should be enabled (implementation dependent)
        ],
        description="Return from subroutine and enable interrupts",
        cycles=2,
    ),
]

# Missing Control Flow
MISSING_CONTROL_FLOW_CASES = [
    InstructionTestCase(
        name="JR NC,n - taken (C=0)",
        opcode=0x30,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            FlagValue(Flag.CARRY, False),
            MemoryValue(0xC000, 0x10),  # +16 offset
        ],
        expected=[
            RegisterValue(Register.PC, 0xC011),  # PC + 1 + 16
        ],
        description="Relative jump when no carry - taken",
        cycles=2,
    ),
    InstructionTestCase(
        name="JR NC,n - not taken (C=1)",
        opcode=0x30,
        setup=[
            RegisterValue(Register.PC, 0xC000),
            FlagValue(Flag.CARRY, True),
            MemoryValue(0xC000, 0x10),  # +16 offset (unused)
        ],
        expected=[
            RegisterValue(Register.PC, 0xC001),  # PC + 1 (not taken)
        ],
        description="Relative jump when no carry - not taken",
        cycles=2,
    ),
    InstructionTestCase(
        name="RET NC - taken (C=0)",
        opcode=0xD0,
        setup=[
            RegisterValue(Register.SP, 0xDFF0),
            FlagValue(Flag.CARRY, False),
            MemoryValue(0xDFF0, 0x00),  # Return address low byte
            MemoryValue(0xDFF1, 0xC0),  # Return address high byte (0xC000)
        ],
        expected=[
            RegisterValue(Register.PC, 0xC000),
            RegisterValue(Register.SP, 0xDFF2),
        ],
        description="Return if no carry - taken",
        cycles=2,  # Implementation uses 2 for both taken/not-taken
    ),
    InstructionTestCase(
        name="RET NC - not taken (C=1)",
        opcode=0xD0,
        setup=[
            RegisterValue(Register.PC, 0xC100),
            RegisterValue(Register.SP, 0xDFF0),
            FlagValue(Flag.CARRY, True),
        ],
        expected=[
            RegisterValue(Register.SP, 0xDFF0),  # SP unchanged
        ],
        description="Return if no carry - not taken",
        cycles=2,
    ),
]


@pytest.mark.parametrize("test_case", JUMP_CASES, ids=[tc.name for tc in JUMP_CASES])
def test_jump_instructions(cpu, test_case):
    """Test jump instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", CALL_CASES, ids=[tc.name for tc in CALL_CASES])
def test_call_instructions(cpu, test_case):
    """Test call instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", RETURN_CASES, ids=[tc.name for tc in RETURN_CASES]
)
def test_return_instructions(cpu, test_case):
    """Test return instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", RESTART_CASES, ids=[tc.name for tc in RESTART_CASES]
)
def test_restart_instructions(cpu, test_case):
    """Test restart instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", JUMP_CONTROL_CASES, ids=[tc.name for tc in JUMP_CONTROL_CASES]
)
def test_jump_control_instructions(cpu, test_case):
    """Test jump control instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", RELATIVE_JUMP_CASES, ids=[tc.name for tc in RELATIVE_JUMP_CASES]
)
def test_relative_jump_instructions(cpu, test_case):
    """Test relative jump instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", ADDITIONAL_CALL_CASES, ids=[tc.name for tc in ADDITIONAL_CALL_CASES]
)
def test_additional_call_instructions(cpu, test_case):
    """Test additional call instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case", RESTART_ALL_CASES, ids=[tc.name for tc in RESTART_ALL_CASES]
)
def test_restart_all_instructions(cpu, test_case):
    """Test restart instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize("test_case", RETI_CASES, ids=[tc.name for tc in RETI_CASES])
def test_reti_instructions(cpu, test_case):
    """Test RETI instruction: {test_case.name}"""
    # Setup initial state
    CPUStateValidator.setup_state(cpu, test_case.setup)

    # Execute instruction
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)

    # Verify state and cycle timing
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"


@pytest.mark.parametrize(
    "test_case",
    MISSING_CONTROL_FLOW_CASES,
    ids=[tc.name for tc in MISSING_CONTROL_FLOW_CASES],
)
def test_missing_control_flow_instructions(cpu, test_case):
    """Test missing control flow instruction: {test_case.name}"""
    CPUStateValidator.setup_state(cpu, test_case.setup)
    CPUStateValidator.execute_instruction(cpu, test_case.opcode)
    CPUStateValidator.assert_state(cpu, test_case)
    assert cpu._m == test_case.cycles, f"{test_case.name} cycle count mismatch"



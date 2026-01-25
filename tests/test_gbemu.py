import pytest

from src.gbemu import GPU, MMU, R8, R16, Z80, GBEmu


def test_gbemu_initialization():
    """Test that GBEmu can be initialized without errors."""
    emulator = GBEmu()
    assert emulator._mmu is not None
    assert emulator._cpu is not None
    assert emulator._gpu is not None


def test_z80_registers():
    """Test Z80 register initialization."""
    cpu = Z80()
    assert cpu._PC.value == 0
    assert cpu._SP.value == 0
    assert cpu._AF.value == 0
    assert cpu._BC.value == 0
    assert cpu._DE.value == 0
    assert cpu._HL.value == 0


def test_register_classes():
    """Test register classes work correctly."""
    r8 = R8()
    r8.value = 255
    assert r8.value == 255

    r16 = R16()
    r16.value = 0x1234
    assert r16.high == 0x12
    assert r16.low == 0x34
    assert r16.value == 0x1234


def test_mmu_initialization():
    """Test MMU initialization."""
    mmu = MMU()
    assert mmu.biosf == True
    assert len(mmu._bios) > 0

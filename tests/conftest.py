import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from gbemu.Z80 import Z80


@pytest.fixture
def cpu():
    """Create fresh CPU instance for each test."""
    cpu = Z80()
    cpu.Reset()
    return cpu

class MMU(object):
    @property
    def biosf(self):
        return self._biosf

    @biosf.setter
    def biosf(self, value):
        self._biosf = value

    def __init__(self):
        # Flag, True iif BIOS is mapped in
        # Bios is unmapped with the first instruction above 0x00FF
        self._biosf = True

        # Memory regions
        # 0x0000 - 0x00FF
        self._bios = [
            0x31,
            0xFE,
            0xFF,
            0xAF,
            0x21,
            0xFF,
            0x9F,
            0x32,
            0xCB,
            0x7C,
            0x20,
            0xFB,
            0x21,
            0x26,
            0xFF,
            0x0E,
            0x11,
            0x3E,
            0x80,
            0x32,
            0xE2,
            0x0C,
            0x3E,
            0xF3,
            0xE2,
            0x32,
            0x3E,
            0x77,
            0x77,
            0x3E,
            0xFC,
            0xE0,
            0x47,
            0x11,
            0x04,
            0x01,
            0x21,
            0x10,
            0x80,
            0x1A,
            0xCD,
            0x95,
            0x00,
            0xCD,
            0x96,
            0x00,
            0x13,
            0x7B,
            0xFE,
            0x34,
            0x20,
            0xF3,
            0x11,
            0xD8,
            0x00,
            0x06,
            0x08,
            0x1A,
            0x13,
            0x22,
            0x23,
            0x05,
            0x20,
            0xF9,
            0x3E,
            0x19,
            0xEA,
            0x10,
            0x99,
            0x21,
            0x2F,
            0x99,
            0x0E,
            0x0C,
            0x3D,
            0x28,
            0x08,
            0x32,
            0x0D,
            0x20,
            0xF9,
            0x2E,
            0x0F,
            0x18,
            0xF3,
            0x67,
            0x3E,
            0x64,
            0x57,
            0xE0,
            0x42,
            0x3E,
            0x91,
            0xE0,
            0x40,
            0x04,
            0x1E,
            0x02,
            0x0E,
            0x0C,
            0xF0,
            0x44,
            0xFE,
            0x90,
            0x20,
            0xFA,
            0x0D,
            0x20,
            0xF7,
            0x1D,
            0x20,
            0xF2,
            0x0E,
            0x13,
            0x24,
            0x7C,
            0x1E,
            0x83,
            0xFE,
            0x62,
            0x28,
            0x06,
            0x1E,
            0xC1,
            0xFE,
            0x64,
            0x20,
            0x06,
            0x7B,
            0xE2,
            0x0C,
            0x3E,
            0x87,
            0xF2,
            0xF0,
            0x42,
            0x90,
            0xE0,
            0x42,
            0x15,
            0x20,
            0xD2,
            0x05,
            0x20,
            0x4F,
            0x16,
            0x20,
            0x18,
            0xCB,
            0x4F,
            0x06,
            0x04,
            0xC5,
            0xCB,
            0x11,
            0x17,
            0xC1,
            0xCB,
            0x11,
            0x17,
            0x05,
            0x20,
            0xF5,
            0x22,
            0x23,
            0x22,
            0x23,
            0xC9,
            0xCE,
            0xED,
            0x66,
            0x66,
            0xCC,
            0x0D,
            0x00,
            0x0B,
            0x03,
            0x73,
            0x00,
            0x83,
            0x00,
            0x0C,
            0x00,
            0x0D,
            0x00,
            0x08,
            0x11,
            0x1F,
            0x88,
            0x89,
            0x00,
            0x0E,
            0xDC,
            0xCC,
            0x6E,
            0xE6,
            0xDD,
            0xDD,
            0xD9,
            0x99,
            0xBB,
            0xBB,
            0x67,
            0x63,
            0x6E,
            0x0E,
            0xEC,
            0xCC,
            0xDD,
            0xDC,
            0x99,
            0x9F,
            0xBB,
            0xB9,
            0x33,
            0x3E,
            0x3C,
            0x42,
            0xB9,
            0xA5,
            0xB9,
            0xA5,
            0x42,
            0x4C,
            0x21,
            0x04,
            0x01,
            0x11,
            0xA8,
            0x00,
            0x1A,
            0x13,
            0xBE,
            0x20,
            0xFE,
            0x23,
            0x7D,
            0xFE,
            0x34,
            0x20,
            0xF5,
            0x06,
            0x19,
            0x78,
            0x86,
            0x23,
            0x05,
            0x20,
            0xFB,
            0x86,
            0x20,
            0xFE,
            0x3E,
            0x01,
            0xE0,
            0x50,
        ]
        # 0x0000 - 0x3FFF 16k
        # ROM Bank 0
        self._romb0 = [0] * 0x4000

        # 0x3FFF - 0x7FFF 16k
        # ROM Bank 1-N
        self._rombn = [0] * 0x4000

        # 0x8000 - 0x9FFF 8k
        # Video RAM (gpu)

        # 0xA000 - 0xBFFF 8k
        # External RAM
        self._eram = [0] * 0x2000

        # 0xC000 - 0xCFFF 4k
        # Work RAM Bank 0
        self._wramb0 = [0] * 0x1000

        # 0xD000 - 0xDFFF 4k
        # Work RAM Bank 1-N
        self._wrambn = [0] * 0x1000

        # 0xE000 - 0xFDFF
        # Mirror 0xC000 - 0xDDFF

        # 0xFE00 - 0xFE9F
        # OAM
        self._oam = [0] * 0xA0

        # 0xFEA0 - 0xFEFF
        # Not usable

        # 0xFF00 - 0xFF7F
        # I/O Registers
        self._io = [0] * 0x80

        # 0xFF80 - 0xFFFE
        # HRAM
        self._hram = [0] * 0x7F

        # 0xFFFF
        self._ienable = 0x00

    def setGPU(self, gpu):
        self._gpu = gpu

    def setROM0(self, rom):
        self._romb0 = rom

    def setROMB(self, rom):
        self._rombn = rom

    def setVRAM(self, vram):
        self._vram = vram

    def setOAM(self, oam):
        self._oam = oam

    def setWRAMB(self, wram):
        self._wrambn = wram

    def loadROM(self, rom):
        self.setROM0(rom[0:16383])
        self.setROMB(rom[16384:32767])

    # Read 8bits
    def rb(self, addr):
        # BIOS / ROM0
        if addr & 0xF000 <= 0x3FFF:
            if self._biosf and addr <= 0x0FF:
                return self._bios[addr]
            return self._romb0[addr]
        # ROMN
        if addr <= 0x7FFF:
            return self._rombn[addr ^ 0x4000]

        # VRAM
        if addr <= 0x9FFF:
            return self._gpu.VRAM[addr ^ 0x8000]

        # ERAM
        if addr <= 0xBFFF:
            return self._eram[addr ^ 0xA000]

        # WRAM
        if addr <= 0xCFFF:
            return self._wramb0[addr ^ 0xC000]

        # WRAMN
        if addr <= 0xDFFF:
            return self._wrambn[addr ^ 0xD000]

        # MIRROR
        if addr <= 0xFDFF:
            return self.rb(addr ^ 0x2000)

        # OAM
        if addr <= 0xFE9F:
            return self._oam[addr ^ 0xFE00]

        # IO
        if addr <= 0xFF7F:
            if 0xFF40 <= addr <= 0xFF7F:
                return self._gpu.rb(addr)
            return self._io[addr ^ 0xFF00]

        # HRAM
        if addr <= 0xFFFE:
            return self._hram[addr ^ 0xFF80]

        # ienable
        if addr == 0xFFFF:
            return self._ienable

    # Read 16bits
    def rw(self, addr):
        l = self.rb(addr)
        h = self.rb((addr + 1) & 0xFFFF)
        return (h << 8) | l

    # Write 8bits
    def wb(self, addr, data):
        # VRAM
        if 0x8000 <= addr <= 0x9FFF:
            self._gpu.VRAM[addr ^ 0x8000] = data
            if addr <= 0x97FF:
                self._gpu.updateTile(addr ^ 0x8000)

            return

        # ERAM
        if 0xA000 <= addr <= 0xBFFF:
            self._eram[addr ^ 0xA000] = data
            return

        # WRAM
        if 0xC000 <= addr <= 0xCFFF:
            self._wramb0[addr ^ 0xC000] = data
            return

        # WRAMN
        if 0xD000 <= addr <= 0xDFFF:
            self._wrambn[addr ^ 0xD000] = data
            return

        # MIRROR
        if 0xE000 <= addr <= 0xFDFF:
            self.wb(addr ^ 0x2000, data)
            return

        # OAM
        if 0xFE00 <= addr <= 0xFE9F:
            return self._oam[addr ^ 0xFE00]

        # IO
        if 0xFF00 <= addr <= 0xFF7F:
            self._io[addr ^ 0xFF00] = data
            if 0xFF40 <= addr <= 0xFF47:
                self._gpu.wb(addr, data)

        # HRAM
        if 0xFF80 <= addr <= 0xFFFE:
            self._hram[addr ^ 0xFF80] = data
            return

        # ienable
        if addr == 0xFFFF:
            self._ienable = data
            return

    # write 16bits
    def ww(self, addr, data):
        self.wb(addr, data & 0xFF)
        self.wb((addr + 1) & 0xFFFF, data >> 8)

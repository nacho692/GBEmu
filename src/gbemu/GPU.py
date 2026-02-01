import pygame


class Color(object):
    """Maps 2-bit Game Boy palette indices to RGB tuples."""

    @staticmethod
    def getColor(val):
        """Return an RGB tuple for a 2-bit palette shade (0=white, 3=black)."""
        if val == 0:
            return (255, 255, 255)
        if val == 1:
            return (192, 192, 192)
        if val == 2:
            return (96, 96, 96)
        if val == 3:
            return (0, 0, 0)
        return (255, 0, 255)


class GPU(object):
    """Game Boy PPU (Pixel Processing Unit).

    Emulates the DMG display hardware: a 160x144 LCD driven by a scanline
    state machine that cycles through OAM search, pixel transfer, H-Blank,
    and V-Blank. Tile and background map data live in 8 KB of VRAM; rendering
    is performed scanline-by-scanline onto a pygame surface.
    """

    @property
    def VRAM(self):
        return self._vram

    @property
    def OAM(self):
        return self._oam

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((160, 144))
        self.reset()

    def reset(self):
        """Reset all GPU state to power-on defaults."""
        self._mode = 2
        self._modeclock = 0
        self._line = 0
        self._bgmap = 0
        self._bgtile = 0
        self._scy = 0
        self._scx = 0
        self._bgdisplay = 0
        self._lcd = 0
        self._vram = [0] * 0x2000
        self._oam = [0] * 0xA0
        self._screen.fill((255, 255, 255))
        self._tileset = [[[0] * 8 for _ in range(8)] for _ in range(384)]
        self._pal = [3, 2, 1, 0]
        pygame.display.update()

    def __renderscan(self):
        """Render the current scanline to the pygame surface.

        Reads tile indices from the background map in VRAM, looks up pixel
        data in the pre-decoded tileset, applies the background palette, and
        writes 160 pixels to the surface at the current scanline.

        Tile data addressing depends on LCDC bit 4 (_bgtile):
          - 1: unsigned mode, tiles at 0x8000 (tileset indices 0-255)
          - 0: signed mode, tiles at 0x8800 (indices 0-127 offset by +256)
        """
        if self._bgmap:
            mapbase = 0x1C00
        else:
            mapbase = 0x1800

        mapbase += (((self._line + self._scy) & 0xFF) >> 3) << 5
        lineoff = self._scx >> 3
        y = (self._line + self._scy) & 0xFF
        x = self._scx & 0x7
        tile = self._vram[mapbase + lineoff]
        if self._bgtile == 0 and tile < 128:
            tile += 256

        for p in range(0, 160):
            color = Color.getColor(self._pal[self._tileset[tile][y & 7][x]])
            self._screen.set_at((p, self._line), color)
            x += 1
            if x == 8:
                x = 0
                lineoff = (lineoff + 1) & 0x1F
                tile = self._vram[mapbase + lineoff]
                if self._bgtile == 0 and tile < 128:
                    tile += 256

    def updateTile(self, addr):
        """Decode a tile row from VRAM into the pre-decoded tileset cache.

        Each Game Boy tile is 16 bytes (2 bytes per row, 8 rows). The two
        bytes encode 8 pixels in 2BPP format: bit N of byte 0 is the low bit
        and bit N of byte 1 is the high bit of pixel N's palette index.

        Args:
            addr: VRAM-relative address (0x0000-0x17FF) of the written byte.
        """
        tile = addr >> 4
        if addr & 0x1:
            addr -= 1

        y = (addr >> 1) & 0x7
        val1 = [(self._vram[addr] >> bit) & 1 for bit in range(8 - 1, -1, -1)]
        val2 = [(self._vram[addr + 1] >> bit) & 1 for bit in range(8 - 1, -1, -1)]
        for x in range(0, 8):
            self._tileset[tile][y][x] = val1[x] + val2[x] * 2

    def rb(self, addr):
        """Read a GPU I/O register (0xFF40-0xFF47).

        Registers:
            0xFF40 - LCDC: LCD control (bg enable, tile map/data select, LCD on)
            0xFF42 - SCY:  background scroll Y
            0xFF43 - SCX:  background scroll X
            0xFF44 - LY:   current scanline (read-only)
            0xFF47 - BGP:  background palette
        """
        if addr == 0xFF40:
            return (
                self._bgdisplay * 0x01
                | self._bgmap * 0x08
                | self._bgtile * 0x10
                | self._lcd * 0x80
            )
        if addr == 0xFF42:
            return self._scy
        if addr == 0xFF43:
            return self._scx
        if addr == 0xFF44:
            return self._line

        if addr == 0xFF47:
            res = 0
            for x in range(0, 4):
                res |= self._pal[3 - x] << x * 2
            return res

    def wb(self, addr, val):
        """Write a GPU I/O register (0xFF40-0xFF47).

        See rb() for the register map. Writing to 0xFF44 (LY) is a no-op;
        the scanline counter is driven by the GPU's internal state machine.
        """
        # LCD Control
        if addr == 0xFF40:
            self._bgdisplay = val & 0x01
            self._bgmap = (val & 0x08) >> 3
            self._bgtile = (val & 0x10) >> 4
            self._lcd = (val & 0x80) >> 7
            return

        # Scroll Y
        if addr == 0xFF42:
            self._scy = val
            return
        # Scroll X
        if addr == 0xFF43:
            self._scx = val
            return

        # Current Line (writing into this register resets it)
        if addr == 0xFF44:
            return

        # Background Palette
        if addr == 0xFF47:
            pal = [(val >> bit) & 1 for bit in range(8 - 1, -1, -1)]
            for i in range(0, 8, 2):
                self._pal[i // 2] = (pal[i] << 1) | pal[i + 1]
            self._pal.reverse()

            return

    def step(self, m):
        """Advance the GPU state machine by the given number of machine cycles.

        The GPU cycles through four modes per visible scanline:
          Mode 2 (OAM search)     -  80 T-cycles
          Mode 3 (pixel transfer) - 172 T-cycles  (renders the scanline)
          Mode 0 (H-Blank)        - 204 T-cycles
        After 144 visible lines, it enters:
          Mode 1 (V-Blank)        - 456 T-cycles x 10 lines

        Args:
            m: Machine cycles elapsed since the last call (1 M-cycle = 4 T-cycles).
        """
        if not self._lcd:
            return
        self._modeclock += m * 4
        if self._mode == 2:
            if self._modeclock >= 80:
                self._mode = 3
                self._modeclock = 0
            return
        if self._mode == 3:
            if self._modeclock >= 172:
                self._mode = 0
                self._modeclock = 0
                self.__renderscan()

            return

        if self._mode == 0:
            if self._modeclock >= 204:
                self._modeclock = 0
                self._line += 1

                if self._line == 144:
                    self._mode = 1
                    pygame.display.update()
                else:
                    self._mode = 2
            return

        if self._mode == 1:
            if self._modeclock >= 456:
                self._modeclock = 0
                self._line += 1
                if self._line > 153:
                    self._mode = 2
                    self._line = 0
            return

import pygame

class Color(object):
    @staticmethod
    def getColor(val):
        if val == 0:
            return (255, 255, 255)
        if val == 1:
            return (192, 192, 192)
        if val == 2:
            return (96, 96, 96)
        if val == 3:
            return (0, 0, 0, 0)
        return (255, 0, 255)


class GPU(object):
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
        self._mode = 0
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
        self._tileset = [[[0, 0, 0, 0, 0, 0, 0, 0]] * 8] * 384
        self._pal = [3, 2, 1, 0]
        pygame.display.update()

    def __renderscan(self):
        self._screen.fill((255, 255, 255))
        if self._bgmap:
            mapoffset = 0x1C00
        else:
            mapoffset = 0x1800

        mapoffset += ((self._line + self._scy) & 0xFF >> 3) << 5
        mapoffset += self._scx >> 3
        y = (self._line + self._scy) & 0xFF
        x = self._scx & 0x7
        # print self._vram[mapoffset:mapoffset+0xF]
        # print self._vram[self._bgmap:0x20*0x20]
        tile = self._vram[mapoffset]
        if self._bgtile == 1 and tile < 128:
            tile += 256

        for p in range(0, 160):
            color = Color.getColor(self._pal[self._tileset[tile][y & 7][x]])
            self._screen.set_at((p, y), color)
            x += 1
            if x == 8:
                x = 0
                mapoffset += 1
                tile = self._vram[mapoffset]
                if self._bgtile == 1 and tile < 128:
                    tile += 256
        pygame.display.update()

    def updateTile(self, addr):
        tile = addr >> 4  # addr / 8
        if addr & 0x1:
            addr -= 1

        y = addr & 0x7
        val1 = [(self._vram[addr] >> bit) & 1 for bit in range(8 - 1, -1, -1)]
        val2 = [(self._vram[addr + 1] >> bit) & 1 for bit in range(8 - 1, -1, -1)]
        for x in range(0, 8):
            self._tileset[tile][y][x] = val1[x] + val2[x] * 2

    def rb(self, addr):
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
        # LCD Control
        if addr == 0xFF40:
            self._bgdisplay = val & 0x01
            self._bgmap = (val & 0x08) >> 3
            self._bgtile = (val & 0x10) >> 4
            self._lcd = (val & 0x80) >> 7
            return

        # Scroll X
        if addr == 0xFF42:
            self._scx = val
            return
        # Scroll Y
        if addr == 0xFF43:
            self._scy = val
            return

        # Current Line (writing into this register resets it
        if addr == 0xFF44:
            # self._line = 0
            # self._modeclock = 0
            # self._mode = 0
            return

        # Background Palette
        if addr == 0xFF47:
            pal = [(val >> bit) & 1 for bit in range(8 - 1, -1, -1)]
            for i in range(0, 8, 2):
                self._pal[i // 2] = (pal[i] << 1) | pal[i + 1]
            self._pal.reverse()

            return

    def step(self, m):
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

                if self._line == 143:
                    self._mode = 1
                else:
                    self._mode = 2
            return

        if self._mode == 1:
            if self._modeclock >= 456:
                self._modeclock = 0
                self._line += 1
                if self._line > 153:
                    self._mode = 0
                    self._line = 0
            return

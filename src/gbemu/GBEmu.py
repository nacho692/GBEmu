import sys

import pygame

from . import GPU, MMU, Z80


class GBEmu:
    def __init__(self):
        self._mmu = MMU.MMU()
        self._cpu = Z80.Z80()
        self._gpu = GPU.GPU()

        self._mmu.setGPU(self._gpu)
        self._mmu.setOAM(self._gpu.OAM)

        self._cpu.MMU = self._mmu

    def loadROM(self, path):
        with open(path, "rb") as f:
            rom = list(f.read())
        self._mmu.loadROM(rom)

    def start(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self._cpu.cycle()
            self._gpu.step(self._cpu._m)

import Z80
import MMU
import GPU

class GBEmu:
    def __init__(self):
        self._mmu = MMU.MMU()
        self._cpu = Z80.Z80()
        self._gpu = GPU.GPU()

        self._mmu.setGPU(self._gpu)
        self._mmu.setOAM(self._gpu.OAM)

        self._cpu.MMU = self._mmu
        
    def loadROM(self,name):
        file_ob = open(name,"rb")
        try:
            byte = file_ob.read(1)
            rom = []
            while not byte == "":
                rom.append(ord(byte))
                byte = file_ob.read(1)
        finally:
            file_ob.close()

        self._mmu.loadROM(rom)

    def start(self):
        i = 0
        while(True):    
            self._cpu.cycle()
            self._gpu.step(self._cpu._m)
            i += 1


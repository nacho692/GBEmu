import collections
import MMU
import registers

class Flags:
    ZERO = 0x80
    SUB = 0x40
    HALF_CARRY = 0x20
    CARRY = 0x10


class Z80(object):
    @property
    def MMU(self):
        return self._mem

    @MMU.setter
    def MMU(self,mem):
        self._mem = mem


    def __init__(self):
        self._HL = registers.R16()
        self._AF = registers.R16()
        self._BC = registers.R16()
        self._DE = registers.R16()

        self._PC = registers.R16()
        self._SP = registers.R16()
        self._ime = True
        self._m = 0

        self._clock = 0

        self._halt = False
        self._stop = False

        #Memory Unit
        self._mem = MMU.MMU()

        #OPCodes Map
        self._opmap = []
        for i in range(0x00,0x100):
            val = (hex(i)[2:].zfill(2)).upper()
            self._opmap.append(getattr(self, "OPCode_" + val,self.OPCode_00))

        self._opcbmap = []
        for i in range(0x00,0x100):
            val = (hex(i)[2:].zfill(2)).upper()
            self._opcbmap.append(getattr(self, "OPCode_CB" + val, self.OPCode_00))
            
    def Status(self):
        print "PC: " + hex(self._PC.value)
        print "SP: " + hex(self._SP.value)
        print "AF: " + hex(self._AF.value)
        print "BC: " + hex(self._BC.value)
        print "DE: " + hex(self._DE.value)
        print "HL: " + hex(self._HL.value)


    def Reset(self):
        self._HL = registers.R16()
        self._AF = registers.R16()
        self._BC = registers.R16()
        self._DE = registers.R16()

        self._PC = registers.R16()
        self._SP = registers.R16()

        self._ime = True
        self._m = 0

        self._clock = 0

        self._halt = False
        self._stop = False
    
    def cycle(self):
        if self._PC.value > 0x00FF:
            self._mem.biosf = False

        ir = self._mem.rb(self._PC.value)
        #if not ir == 0:
            #print "PC " + hex(self._PC.value)
            #print "IR " + hex(ir)
        self._PC.value += 1
        self._opmap[ir]()
        self._clock += self._m

        #self.Status()
        #print " "
#        if self._PC.value == 0x95:
#            self.Status()
#            print " "
#            input()

    def __ToggleFlag(self, flag):
        self._AF.low ^= flag
    
    def __ResetFlag(self, flag):
        self._AF.low &= (~flag & 0xFF)

    def __SetFlag(self, flag):
        self._AF.low |= flag

    def __IsFlagSet(self, flag):
        return (self._AF.low & flag) == flag

    def printFlags(self):
        print '{0:08b}'.format(self._AF.low)

    #Instructions
    def __OFFSET8(self,value):
        return ((value & 0x7F) - (value & 0x80))

    def __RL(self, value):
        out = (value & 0x80) == 0x80
        
        self._AF.low = 0
        value <<= 1
        
        if self.__IsFlagSet(Flags.CARRY):
            value |= 0x1
        if out:
            self.__SetFlag(Flags.CARRY)

        if value == 0:
            self.__SetFlag(Flags.ZERO)
        return value

    def __RLC(self,value):
        out = (value & 0x8) == 0x8

        self._AF.low = 0
        value <<= 1

        if out:
            self.__SetFlag(Flags.CARRY)
            value |= 0x10
        
        if value == 0:
            self.__SetFlag(Flags.ZERO)

        return value

    def __RR(self, value):
        out = (value & 0x1) == 0x1
         
        self._AF.low = 0
        value >>= 1
        
        if self.__IsFlagSet(Flags.CARRY):
            value |= 0x80
        if out:
            self.__SetFlag(Flags.CARRY)

        if value == 0:
            self.__SetFlag(Flags.ZERO)
        return value

    def __RRC(self,value):
        out = (value & 0x1) == 0x1

        self._AF.low = 0
        value >>= 1

        if out:
            self.__SetFlag(Flags.CARRY)
            value |= 0x80
        
        if value == 0:
            self.__SetFlag(Flags.ZERO)

        return value
    def __PUSH(self, data):
        self._SP.value -= 2
        self._mem.ww(self._SP.value, data)

    def __POP(self):
        data = self._mem.rw(self._SP.value)
        self._SP.value += 2
        return data

    def __ADD8(self,v1,v2):
        result = v1 + v2 
        self._AF.low = 0

        if(result & 0xFF) == 0:
            self.__ToggleFlag(Flags.ZERO)
        if(result > 0xFF):
            self.__ToggleFlag(Flags.CARRY)
        if (v1 & 0xF) + (v2 & 0xF) > 0xF:
            self.__ToggleFlag(Flags.HALF_CARRY)

        return result & 0xFF

    def __SUB8(self,v1,v2):
        result = v1 - v2
        carrybits = v1 ^ v2 ^ result
        self._AF.low = 0
        self.__SetFlag(Flags.SUB)

        if(result & 0xFF) == 0:
            self.__SetFlag(Flags.ZERO)
        if not(carrybits & 0x100 == 0):
            self.__SetFlag(Flags.CARRY)
        if not(carrybits & 0x10 == 0):
            self.__SetFlag(Flags.HALF_CARRY)
        
        return result & 0xFF

    def __ADD16(self,v1,v2):
        result = v1 + v2
        self._AF.low = 0
        if(result & 0xFFFF  == 0):
            self.__ToggleFlag(Flags.ZERO)
        if(result > 0xFFFF):
            self.__ToggleFlag(Flags.CARRY)
        if((v1 ^ v2 ^ (result & 0xFFFF)) & 0x1000):
            self.__ToggleFlag(Flags.HALF_CARRY)

        return result & 0xFFFF

    def __AND(self,v1,v2):
        result = v1 & v2
        self._AF.low = 0
        if result == 0:
            self.__SetFlag(Flags.ZERO)
        self.__SetFlag(Flags.HALF_CARRY)
        return result

    def __OR(self,v1,v2):
        result = v1 | v2
        self._AF.low = 0
        if result == 0:
            self.__SetFlag(Flags.ZERO)
        return result
    
    def __XOR(self,v1,v2):
        result = v1 ^ v2
        self._AF.low = 0
        if result == 0:
            self.__SetFlag(Flags.ZERO)
        
        return result

    def __SWAP8(self,val):
        h = val >> 4
        l = val & 0xF
        res = (l << 4) | h
        self._AF.low = 0
        if res == 0:
            self.__SetFlag(Flags.ZERO)
        return res

    def __SLA(self,value):
        self._AF.low = 0
        if(value > 0x7F):
            self.__SetFlag(Flags.CARRY)
        value <<= 1
        if(value == 0):
            self.__SetFlag(Flags.ZERO)
        return value

    def __SRA(self,value):
        self._AF.low = 0
        if(value & 0x1):
            self.__SetFlag(Flags.CARRY)
        value |= (value >> 7) << 8
        value >>=1
        if(value == 0):
            self.__SetFlag(Flags.ZERO)

        return value

    def __SRL(self,value):
        self._AF.low = 0
        if(value & 0x1):
            self.__SetFlag(Flags.CARRY)
        value >>=1

        if(value == 0):
            self.__SetFlag(Flags.ZERO)

        return value

    def __BIT(self,value,b):
        compare = 2**b
        self.__ResetFlag(Flags.SUB)
        self.__SetFlag(Flags.HALF_CARRY)
        self.__SetFlag(Flags.ZERO)
        if(value & compare) == compare:
           self.__ResetFlag(Flags.ZERO)

    def __SET(self,value,b):
        setb = 2**b
        value |= setb
        return value

    def __RES(self,value,b):
        setb = (~(2**b)) & 0xFF
        value &= setb
        return value

        
    #OPCodes
    def OPCode_00(self):
        #NOP
        self._m = 1

    #8-Bits Loads
    def OPCode_06(self):
        #LD B,n
        self._BC.high = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._m = 2
 
    def OPCode_0E(self):
        #LD C,n
        self._BC.low = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._m = 2
    
    def OPCode_16(self):
        #LD D,n
        self._DE.high = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._m = 2

    def OPCode_1E(self):
        #LD E,n
        self._DE.low = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._m = 2

    def OPCode_26(self):
        #LD H,n
        self._HL.high = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._m = 2

    def OPCode_2E(self):
        #LD L,n
        self._HL.low = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._m = 2
    

    def OPCode_7F(self):
        #LD A,A
        self._m = 1

    def OPCode_78(self):
        #LD A,B
        self._AF.high = self._BC.high
        self._m = 1
    
    def OPCode_79(self):
        #LD A,C
        self._AF.high = self._BC.low
        self._m = 1

    def OPCode_7A(self):
        #LD A,D
        self._AF.high = self._DE.high
        self._m = 1

    def OPCode_7B(self):
        #LD A,E
        self._AF.high = self._DE.low
        self._m = 1

    def OPCode_7C(self):
        #LD A,H
        self._AF.high = self._HL.high
        self._m = 1

    def OPCode_7D(self):
        #LD A,L
        self._AF.high = self._HL.low
        self._m = 1

    def OPCode_7E(self):
        #LD A,[HL]
        self._AF.high = self._mem.rb(self._HL.value)
        self._m = 2


    def OPCode_40(self):
        #LD B,B
        self._m = 1

    def OPCode_41(self):
        #LD B,C
        self._BC.high = self._BC.low
        self._m = 1

    def OPCode_42(self):
        #LD B,D
        self._BC.high = self._DE.high
        self._m = 1
    
    def OPCode_43(self):
        #LD B,E
        self._BC.high = self._DE.low
        self._m = 1
    
    def OPCode_44(self):
        #LD B,H
        self._BC.high = self._HL.high
        self._m = 1

    def OPCode_45(self):
        #LD B,L
        self._BC.high = self._HL.low
        self._m = 1
    
    def OPCode_46(self):
        #LD B,[HL]
        self._BC.high = self._mem.rb(self._HL.value)
        self._m = 2
     
    def OPCode_48(self):
        #LD C,B
        self._BC.low = self._BC.high
        self._m = 1   
      
    def OPCode_49(self):
        #LD C,C
        self._m = 1

    def OPCode_4A(self):
        #LD C,D
        self._BC.low = self._DE.high
        self._m = 1      

    def OPCode_4B(self):
        #LD C,E
        self._BC.low = self._DE.low
        self._m = 1

    def OPCode_4C(self):
        #LD C,H
        self._BC.low = self._HL.high
        self._m = 1

    def OPCode_4D(self):
        #LD C,L
        self._BC.low = self._HL.high
        self._m = 1

    def OPCode_4E(self):
        #LD C,[HL]
        self._BC.low = self._mem.rb(self._HL.value)
        self._m = 2

    def OPCode_50(self):
        #LD D,B
        self._DE.high = self._BC.high
        self._m = 1

    def OPCode_51(self):
        #LD D,C
        self._DE.high = self._BC.low
        self._m = 1

    def OPCode_52(self):
        #LD D,D
        self._m = 1

    def OPCode_53(self):
        #LD D,E
        self._DE.high = self._DE.low
        self._m = 1

    def OPCode_54(self):
        #LD D,H
        self._DE.high = self._HL.high
        self._m = 1

    def OPCode_55(self):
        #LD D,L
        self._DE.high = self._HL.low
        self._m = 1

    def OPCode_56(self):
        #LD D,[HL]
        self._DE.high = self._mem.rb(self._HL.value)
        self._m = 2

    def OPCode_58(self):
        #LD E,B
        self._DE.low = self._BC.high
        self._m = 1

    def OPCode_59(self):
        #LD E,C
        self._DE.low = self._BC.low
        self._m = 1

    def OPCode_5A(self):
        #LD E,D
        self._DE.low = self._DE.high
        self._m = 1

    def OPCode_5B(self):
        #LD E,E
        self._m = 1

    def OPCode_5C(self):
        #LD E,H
        self._DE.low = self._HL.high
        self._m = 1

    def OPCode_5D(self):
        #LD E,L
        self._DE.low = self._HL.low
        self._m = 1

    def OPCode_5E(self):
        #LD E,[HL]
        self._DE.low = self._mem.rb(self._HL.value)
        self._m = 2

    def OPCode_60(self):
        #LD H,B
        self._HL.high = self._BC.high
        self._m = 1

    def OPCode_61(self):
        #LD H,C
        self._HL.high = self._BC.low
        self._m = 1


    def OPCode_62(self):
        #LD H,D
        self._HL.high = self._DE.high
        self._m = 1


    def OPCode_63(self):
        #LD H,E
        self._HL.high = self._DE.low
        self._m = 1

    def OPCode_64(self):
        #LD H,H
        self._m = 1

    def OPCode_65(self):
        #LD H,L
        self._HL.high = self._HL.low
        self._m = 1

    def OPCode_66(self):
        #LD H,[HL]
        self._HL.high = self._mem.rb(self._HL.value)
        self._m = 2

    def OPCode_68(self):
        #LD L,B
        self._HL.low = self._BC.high
        self._m = 1

    def OPCode_69(self):
        #LD L,C
        self._HL.low = self._BC.low
        self._m = 1

    def OPCode_6A(self):
        #LD L,D
        self._HL.low = self._DE.high
        self._m = 1

    def OPCode_6B(self):
        #LD L,E
        self._HL.low = self._DE.low
        self._m = 1


    def OPCode_6C(self):
        #LD L,H
        self._HL.low = self._HL.high
        self._m = 1


    def OPCode_6D(self):
        #LD L,L
        self._m = 1

    def OPCode_6E(self):
        #LD L,[HL]
        self._HL.low = self._mem.rb(self._HL.value)
        self._m = 2

    def OPCode_70(self):
        #LD [HL],B
        self._mem.wb(self._HL.value,self._BC.high)
        self._m = 2

    def OPCode_71(self):
        #LD [HL],C
        self._mem.wb(self._HL.value,self._BC.low)
        self._m = 2
    
    def OPCode_72(self):
        #LD [HL],D
        self._mem.wb(self._HL.value,self._DE.high)
        self._m = 2
        
    def OPCode_73(self):
        #LD [HL],E
        self._mem.wb(self._HL.value,self._DE.low)
        self._m = 2

    def OPCode_74(self):
        #LD [HL],H
        self._mem.wb(self._HL.value,self._HL.high)
        self._m = 2

    def OPCode_75(self):
        #LD [HL],L
        self._mem.wb(self._HL.value,self._HL.low)
        self._m = 2

    def OPCode_36(self):
        #LD [HL],n
        value = self._mem.rb(self._PC.value)
        self._mem.wb(self._HL.value,value)
        self._PC.value += 1
        self._m = 3

    def OPCode_0A(self):
        #LD A,[BC]
        value = self._mem.rb(self._BC.value)
        self._AF.high = value
        self._m = 2

    def OPCode_1A(self):
        #LD A,[DE]
        value = self._mem.rb(self._DE.value)
        self._AF.high = value
        self._m = 2

    def OPCode_7E(self):
        #LD A,[HL]
        value = self._mem.rb(self._HL.value)
        self._AF.high = value
        self._m = 2

    def OPCode_FA(self):
        #LD A,[nn]
        addr = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._AF.high = self._mem.rb(addr)
        self._m = 4

    def OPCode_3E(self):
        #LD A,n
        value = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._AF.high = value
        self._m = 2

    def OPCode_47(self):
        #LD B,A
        self._BC.high = self._AF.high
        self._m = 1

    def OPCode_4F(self):
        #LD C,A
        self._BC.low = self._AF.high
        self._m = 1

    def OPCode_57(self):
        #LD D,A
        self._DE.high = self._AF.high
        self._m = 1

    def OPCode_5F(self):
        #LD E,A
        self._DE.low = self._AF.high
        self._m = 1

    def OPCode_67(self):
        #LD H,A
        self._HL.high = self._AF.high
        self._m = 1

    def OPCode_6F(self):
        #LD L,A
        self._HL.low = self._AF.high
        self._m = 1

    def OPCode_02(self):
        #LD [BC],A
        self._mem.wb(self._BC.value,self._AF.high)
        self._m = 2

    def OPCode_12(self):
        #LD [DE],A
        self._mem.wb(self._DE.value,self._AF.high)
        self._m = 2

    def OPCode_77(self):
        #LD [HL],A
        self._mem.wb(self._HL.value,self._AF.high)
        self._m = 2

    def OPCode_EA(self):
        #LD [nn],A
        addr = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._mem.wb(addr,self._AF.high)
        self._m = 4
    
    def OPCode_F2(self):
        #LD A,[C] (LD A,[0xFF00 + C]
        addr = 0xFF00 + self._BC.low
        self._AF.high = self._mem.rb(addr)
        self._m = 2

    def OPCode_E2(self):
        #LD [0xFF00 + C],A
        addr = 0xFF00 + self._BC.low
        self._mem.wb(addr,self._AF.high)
        self._m = 2

    def OPCode_3A(self):
        #LDD A,[HL]
        self._AF.high = self._mem.rb(self._HL.value)
        self._HL.value -= 1
        self._m = 2

    def OPCode_32(self):
        #LDD [HL],A
        self._mem.wb(self._HL.value,self._AF.high)
        self._HL.value -= 1
        self._m = 2

    def OPCode_2A(self):
        #LDI A,[HL]
        self._AF.high = self._mem.rb(self._HL.value)
        self._HL.value += 1
        self._m = 2

    def OPCode_22(self):
        #LDI [HL],A
        self._mem.wb(self._HL.value,self._AF.high)
        self._HL.value += 1
        self._m = 2


    def OPCode_E0(self):
        #LD [0xFFF0+n],A
        value = self._mem.rb(self._PC.value)
        self._PC.value += 1
        addr = 0xFF00 + value
        self._mem.wb(addr,self._AF.high)
        self._m = 3

    def OPCode_F0(self):
        #LD A,[0xFF00+n]
        value = self._mem.rb(self._PC.value)
        self._PC.value += 1

        addr = 0xFF00 + value
        self._AF.high = self._mem.rb(addr)
        self._m = 3

    #16-Bits Loads
    def OPCode_01(self):
        #LD BC,NN
        value = self._mem.rw(self._PC.value)
        self._PC.value += 2 
        self._BC.value = value
        self._m = 3
 
    def OPCode_11(self):
        #LD DE,NN
        value = self._mem.rw(self._PC.value)
        self._PC.value += 2 
        self._DE.value = value
        self._m = 3
 
    def OPCode_21(self):
        #LD HL,NN
        value = self._mem.rw(self._PC.value)
        self._PC.value += 2
        self._HL.value = value
        self._m = 3
    
    def OPCode_31(self):
        #LD SP,NN
        value = self._mem.rw(self._PC.value)
        self._PC.value += 2
        self._SP.value = value
        self._m = 3

    def OPCode_F9(self):
        #LD SP,HL
        self._SP.value = self._HL.value
        self._m = 2

    def OPCode_F8(self):
        #LD HL,SP+n
        value = self._mem.rb(self._PC.value)
        self._PC.value += 1
        value = self.__OFFSET8(value)
        result = self._SP.value + value
        
        self._AF.low = 0
        if value >= 0:
            if (self._SP.value & 0xFF) + value > 0xFF:
                self.__SetFlag(Flags.CARRY)
            if (self._SP.value & 0xF) + (value & 0xF) > 0xF:
                self.__SetFlag(Flags.HALF_CARRY)
        else:
            if (result & 0xFF) <= (self._SP.value & 0xFF):
                self.__SetFlag(Flags.CARRY)
            if (result & 0xF) <= (self._SP.value & 0xF):
                self.__SetFlag(Flags.HALF_CARRY)

        self.__ResetFlag(Flags.ZERO)
        
        self._HL.value = result
        self._m = 3


    def OPCode_08(self):
        #LD [nn],SP
        addr = self._mem.rw(self._PC.value)
        self._PC.value += 2
        self._mem.ww(addr, self._SP.value)
        self._m = 5


    def OPCode_F5(self):
        #PUSH AF
        self.__PUSH(self._AF.value)
        self._m = 4

    def OPCode_C5(self):
        #PUSH BC
        self.__PUSH(self._BC.value)
        self._m = 4

    def OPCode_D5(self):
        #PUSH DE
        self.__PUSH(self._DE.value)
        self._m = 4

    def OPCode_E5(self):
        #PUSH HL
        self.__PUSH(self._HL.value)
        self._m = 4

    def OPCode_F1(self):
        #POP AF
        self._AF.value = self.__POP()
        self._m = 3

    def OPCode_C1(self):
        #POP BC
        self._BC.value = self.__POP()
        self._m = 3

    def OPCode_D1(self):
        #POP DE
        self._DE.value = self.__POP()
        self._m = 3

    def OPCode_E1(self):
        #POP HL
        self._HL.value = self.__POP()
        self._m = 3


    #8-Bit ALU
    def OPCode_87(self):
        #ADD A,A
        self._AF.high = self.__ADD8(self._AF.high,self._AF.high)
        self._m = 1

    def OPCode_80(self):
        #ADD A,B
        self._AF.high = self.__ADD8(self._AF.high,self._BC.high)
        self._m = 1

    def OPCode_81(self):
        #ADD A,C
        self._AF.high = self.__ADD8(self._AF.high,self._BC.low)
        self._m = 1

    def OPCode_82(self):
        #ADD A,D
        self._AF.high = self.__ADD8(self._AF.high,self._DE.high)
        self._m = 1

    def OPCode_83(self):
        #ADD A,E
        self._AF.high = self.__ADD8(self._AF.high,self._DE.low)
        self._m = 1

    def OPCode_84(self):
        #ADD A,H
        self._AF.high = self.__ADD8(self._AF.high,self._HL.high)
        self._m = 1

    def OPCode_85(self):
        #ADD A,L
        self._AF.high = self.__ADD8(self._AF.high,self._HL.low)
        self._m = 1

    def OPCode_86(self):
        #ADD A,[HL]
        value = self._mem.rb(self._HL.value)
        self._AF.high = self.__ADD8(self._AF.high,value)
        self_m = 2

    def OPCode_C6(self):
        #ADD A,n
        value = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._AF.high = self.__ADD8(self._AF.high,value)
        self._m = 2

    def OPCode_8F(self):
        #ADC A,A
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__ADD8(self._AF.high,(self._AF.high + carry))
        self._m = 1

    def OPCode_88(self):
        #ADC A,B
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__ADD8(self._AF.high,(self._BC.high + carry))
        self._m = 1

    def OPCode_89(self):
        #ADC A,C
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__ADD8(self._AF.high,(self._BC.low + carry))
        self._m = 1
    
    def OPCode_8A(self):
        #ADC A,D
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__ADD8(self._AF.high,(self._DE.high + carry))
        self._m = 1
    
    def OPCode_8B(self):
        #ADC A,E
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__ADD8(self._AF.high,(self._DE.low + carry))
        self._m = 1
        
    def OPCode_8C(self):
        #ADC A,H
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__ADD8(self._AF.high,(self._HL.high + carry))
        self._m = 1

    def OPCode_8D(self):
        #ADC A,L
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__ADD8(self._AF.high,(self._HL.low + carry))
        self._m = 1

    def OPCode_8E(self):
        #ADC A,[HL]
        carry = self.__IsFlagSet(Flags.CARRY)
        value = self._mem.rb(self._HL.value)
        self._AF.high = self.__ADD8(self._AF.high,(value + carry))
        self._m = 2

    def OPCode_CE(self):
        #ADC A,n
        carry = self.__IsFlagSet(Flags.CARRY)
        value = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._AF.high = self.__ADD8(self._AF.high,(value+carry))
        self._m = 2

    def OPCode_97(self):
        #SUB A,A
        self._AF.high = self.__SUB8(self._AF.high,self._AF.high)
        self._m = 1

    def OPCode_90(self):
        #SUB A,B
        self._AF.high = self.__SUB8(self._AF.high,self._BC.high)
        self._m = 1

    def OPCode_91(self):
        #SUB A,C
        self._AF.high = self.__SUB8(self._AF.high,self._BC.low)
        self._m = 1

    def OPCode_92(self):
        #SUB A,D
        self._AF.high = self.__SUB8(self._AF.high,self._DE.high)
        self._m = 1

    def OPCode_93(self):
        #SUB A,E
        self._AF.high = self.__SUB8(self._AF.high,self._DE.low)
        self._m = 1

    def OPCode_94(self):
        #SUB A,H 
        self._AF.high = self.__SUB8(self._AF.high,self._HL.high)
        self._m = 1

    def OPCode_95(self):
        #SUB A,L 
        self._AF.high = self.__SUB8(self._AF.high,self._HL.low)
        self._m = 1

    def OPCode_96(self):
        #SUB A,[HL]
        value = self._mem.rb(self._HL.value)
        self._AF.high = self.__SUB8(self._AF.high,value)
        self._m = 2

    def OPCode_D6(self):
        #SUB A,n
        value = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._AF.high = self.__SUB8(self._AF.high,value)
        self._m = 2

    def OPCode_9F(self):
        #SBC A,A
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__SUB8(self._AF.high,(self._AF.high + carry))
        self._m = 1

    def OPCode_98(self):
        #SBC A,B
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__SUB8(self._AF.high,self._BC.high + carry)
        self._m = 1

    def OPCode_99(self):
        #SBC A,C
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__SUB8(self._AF.high,self._BC.low + carry)
        self._m = 1

    def OPCode_9A(self):
        #SBC A,D
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__SUB8(self._AF.high,self._DE.high + carry)
        self._m = 1

    def OPCode_9B(self):
        #SBC A,E
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__SUB8(self._AF.high,self._DE.low + carry)
        self._m = 1

    def OPCode_9C(self):
        #SBC A,H
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__SUB8(self._AF.high,self._HL.high + carry)
        self._m = 1

    def OPCode_9D(self):
        #SBC A,L
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__SUB8(self._AF.high,self._HL.low + carry)
        self._m = 1

    def OPCode_9E(self):
        #SBC A,[HL]
        value = self._mem.rb(self._HL.value)
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__SUB8(self._AF.high,value + carry)
        self._m = 2

    def OPCode_DE(self):
        #SBC A,n
        value = self._mem.rb(self._PC.value)
        self._PC.value += 1
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__SUB8(self._AF.high,value + carry)
        self._m = 2


    def OPCode_A7(self):
        #AND A,A
        self._AF.high = self.__AND(self._AF.high,self._AF.high)
        self._m = 1

    def OPCode_A0(self):
        #AND A,B
        self._AF.high = self.__AND(self._AF.high,self._BC.high)
        self._m = 1

    def OPCode_A1(self):
        #AND A,C
        self._AF.high = self.__AND(self._AF.high,self._BC.low)
        self._m = 1

    def OPCode_A2(self):
        #AND A,D
        self._AF.high = self.__AND(self._AF.high,self._DE.high)
        self._m = 1

    def OPCode_A3(self):
        #AND A,E
        self._AF.high = self.__AND(self._AF.high,self._DE.low)
        self._m = 1

    def OPCode_A4(self):
        #AND A,H
        self._AF.high = self.__AND(self._AF.high,self._HL.high)
        self._m = 1

    def OPCode_A5(self):
        #AND A,L
        self._AF.high = self.__AND(self._AF.high,self._HL.low)
        self._m = 1

    def OPCode_A6(self):
        #AND A,[HL]
        value = self._mem.rb(self._HL.value)
        self._AF.high = self.__AND(self._AF.high,value)
        self._m = 2

    def OPCode_E6(self):
        #AND A,n
        value = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._AF.high = self.__AND(self._AF.high,value)
        self._m = 2

    def OPCode_B7(self):
        #OR A,A
        self._AF.high = self.__OR(self._AF.high,self._AF.high)
        self._m = 1

    def OPCode_B0(self):
        #OR A,B
        self._AF.high = self.__OR(self._AF.high,self._BC.high)
        self._m = 1

    def OPCode_B1(self):
        #OR A,C
        self._AF.high = self.__OR(self._AF.high,self._BC.low)
        self._m = 1

    def OPCode_B2(self):
        #OR A,D
        self._AF.high = self.__OR(self._AF.high,self._DE.high)
        self._m = 1

    def OPCode_B3(self):
        #OR A,E
        self._AF.high = self.__OR(self._AF.high,self._DE.low)
        self._m = 1

    def OPCode_B4(self):
        #OR A,H
        self._AF.high = self.__OR(self._AF.high,self._HL.high)
        self._m = 1

    def OPCode_B5(self):
        #OR A,L
        self._AF.high = self.__OR(self._AF.high,self._HL.low)
        self._m = 1

    def OPCode_B6(self):
        #OR A,[HL]
        value = self._mem.rb(self._HL.value)
        self._AF.high = self.__OR(self._AF.high,value)
        self._m = 2

    def OPCode_F6(self):
        #OR A,n
        value = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._AF.high = self.__OR(self._AF.high,value)
        self._m = 2

    def OPCode_AF(self):
        #XOR A,A
        self._AF.high = self.__XOR(self._AF.high,self._AF.high)
        self._m = 1

    def OPCode_A8(self):
        #XOR A,B
        self._AF.high = self.__XOR(self._AF.high,self._BC.high)
        self._m = 1

    def OPCode_A9(self):
        #XOR A,C
        self._AF.high = self.__XOR(self._AF.high,self._BC.low)
        self._m = 1

    def OPCode_AA(self):
        #XOR A,D
        self._AF.high = self.__XOR(self._AF.high,self._DE.high)
        self._m = 1

    def OPCode_AB(self):
        #XOR A,E
        self._AF.high = self.__XOR(self._AF.high,self._DE.low)
        self._m = 1

    def OPCode_AC(self):
        #XOR A,H
        self._AF.high = self.__XOR(self._AF.high,self._HL.high)
        self._m = 1

    def OPCode_AD(self):
        #XOR A,L
        self._AF.high = self.__XOR(self._AF.high,self._HL.low)
        self._m = 1

    def OPCode_AE(self):
        #XOR A,[HL]
        value = self._mem.rb(self._HL.value)
        self._AF.high = self.__XOR(self._AF.high,value)
        self._m = 2

    def OPCode_EE(self):
        #XOR A,n
        value = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._AF.high = self.__XOR(self._AF.high,value)
        self._m = 2

    def OPCode_BF(self):
        #CP A,A
        self.__SUB8(self._AF.high,self._AF.high)
        self._m = 1

    def OPCode_B8(self):
        #CP A,B
        self.__SUB8(self._AF.high,self._BC.high)
        self._m = 1

    def OPCode_B9(self):
        #CP A,C
        self.__SUB8(self._AF.high,self._BC.low)
        self._m = 1

    def OPCode_BA(self):
        #CP A,D
        self.__SUB8(self._AF.high,self._DE.high)
        self._m = 1

    def OPCode_BB(self):
        #CP A,E
        self.__SUB8(self._AF.high,self._DE.low)
        self._m = 1

    def OPCode_BC(self):
        #CP A,H 
        self.__SUB8(self._AF.high,self._HL.high)
        self._m = 1

    def OPCode_BD(self):
        #CP A,L 
        self.__SUB8(self._AF.high,self._HL.low)
        self._m = 1

    def OPCode_BE(self):
        #CP A,[HL]
        value = self._mem.rb(self._HL.value)
        self.__SUB8(self._AF.high,value)
        self._m = 2

    def OPCode_FE(self):
        #CP A,n
        value = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self.__SUB8(self._AF.high,value)
        self._m = 2

    def OPCode_3C(self):
        #INC A
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__ADD8(self._AF.high,0x1)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_04(self):
        #INC B
        carry = self.__IsFlagSet(Flags.CARRY)
        self._BC.high = self.__ADD8(self._BC.high,0x1)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_0C(self):
        #INC C
        carry = self.__IsFlagSet(Flags.CARRY)
        self._BC.low = self.__ADD8(self._BC.low,0x1)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_14(self):
        #INC D
        carry = self.__IsFlagSet(Flags.CARRY)
        self._DE.high = self.__ADD8(self._DE.high,0x1)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_1C(self):
        #INC E
        carry = self.__IsFlagSet(Flags.CARRY)
        self._DE.low = self.__ADD8(self._DE.low,0x1)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_24(self):
        #INC H
        carry = self.__IsFlagSet(Flags.CARRY)
        self._HL.high = self.__ADD8(self._HL.high,0x1)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_2C(self):
        #INC L
        carry = self.__IsFlagSet(Flags.CARRY)
        self._HL.low = self.__ADD8(self._HL.low,0x1)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_34(self):
        #INC [HL]
        carry = self.__IsFlagSet(Flags.CARRY)
        value = self._mem.rb(self._HL.value)
        value = self.__ADD8(value,0x1)
        self._mem.wb(self._HL.value,value)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 3

    def OPCode_3D(self):
        #DEC A
        carry = self.__IsFlagSet(Flags.CARRY)
        self._AF.high = self.__SUB8(self._AF.high,0x1)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_05(self):
        #DEC B
        carry = self.__IsFlagSet(Flags.CARRY)
        self._BC.high = self.__SUB8(self._BC.high,0x1)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_0D(self):
        #DEC C
        carry = self.__IsFlagSet(Flags.CARRY)
        self._BC.low = self.__SUB8(self._BC.low,0x1)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_15(self):
        #DEC D
        carry = self.__IsFlagSet(Flags.CARRY)
        self._DE.high = self.__SUB8(self._DE.high,0x1)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_1D(self):
        #DEC E
        carry = self.__IsFlagSet(Flags.CARRY)
        self._DE.low = self.__SUB8(self._DE.low,0x1)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_25(self):
        #DEC H
        carry = self.__IsFlagSet(Flags.CARRY)
        self._HL.high = self.__SUB8(self._HL.high,0x1)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_2D(self):
        #DEC L
        carry = self.__IsFlagSet(Flags.CARRY)
        self._HL.low = self.__SUB8(self._HL.low,0x1)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_35(self):
        #DEC [HL]
        carry = self.__IsFlagSet(Flags.CARRY)
        value = self._mem.rb(self._HL.value)
        value = self.__SUB8(value,0x1)
        self._mem.wb(self._HL.value,value)
        if carry:
            self.__SetFlag(Flags.CARRY)
        self._m = 3

    #16-Bit ALU
    def OPCode_09(self):
        #ADD HL,BC
        self._HL.value = self.__ADD16(self._HL.value,self._BC.value)
        self._m = 2

    def OPCode_19(self):
        #ADD HL,DE
        self._HL.value = self.__ADD16(self._HL.value,self._DE.value)
        self._m = 2

    def OPCode_29(self):
        #ADD HL,HL
        self._HL.value = self.__ADD16(self._HL.value,self._HL.value)
        self._m = 2

    def OPCode_39(self):
        #ADD HL,SP
        self._HL.value = self.__ADD16(self._HL.value,self._SP.value)
        self._m = 2

    def OPCode_E8(self):
        #ADD SP,n
        value = self._mem.rb(self._PC.value)
        self._PC.value += 1
        value = self.__OFFSET8(value)
        result = self._SP.value + value
        self._AF.low = 0
        if value >= 0:
            if (self._SP.value & 0xFF) + value > 0xFF:
                self.__SetFlag(Flags.CARRY)
            if (self._SP.value & 0xF) + (value & 0xF) > 0xF:
                self.__SetFlag(Flags.HALF_CARRY)
        else:
            if (result & 0xFF) <= (self._SP.value & 0xFF):
                self.__SetFlag(Flags.CARRY)
            if (result & 0xF) <= (self._SP.value & 0xF):
                self.__SetFlag(Flags.HALF_CARRY)

        self.__ResetFlag(Flags.ZERO)
    
    def OPCode_03(self):
        #INC BC
        self._BC.value += 1
        self._m = 2

    def OPCode_13(self):
        #INC DE
        self._DE.value += 1
        self._m = 2

    def OPCode_23(self):
        #INC HL
        self._HL.value += 1
        self._m = 2

    def OPCode_33(self):
        #INC SP
        self._SP.value += 1
        self._m = 2

    def OPCode_0B(self):
        #DEC BC
        self._BC.value -= 1
        self._m = 2

    def OPCode_1B(self):
        #DEC DE
        self._DE.value -= 1
        self._m = 2

    def OPCode_2B(self):
        #DEC HL
        self._HL.value -= 1
        self._m = 2

    def OPCode_3B(self):
        #DEC SP
        self._SP.value -= 1
        self._m = 2

    #MISC
    def OPCode_CB(self):
        ir = self._mem.rb(self._PC.value)
        self._PC.value += 1
        self._opcbmap[ir]()
        

    def OPCode_CB37(self):
        #SWAP A
        self._AF.high = self.__SWAP8(self._AF.high)
        self._m = 2

    def OPCode_CB30(self):
        #SWAP B
        self._BC.high = self.__SWAP8(self._BC.high)
        self._m = 2

    def OPCode_CB31(self):
        #SWAP C
        self._BC.low = self.__SWAP8(self._BC.low)
        self._m = 2

    def OPCode_CB32(self):
        #SWAP D
        self._DE.high = self.__SWAP8(self._DE.high)
        self._m = 2

    def OPCode_CB33(self):
        #SWAP E
        self._DE.low = self.__SWAP8(self._DE.low)
        self._m = 2

    def OPCode_CB34(self):
        #SWAP H
        self._HL.high = self.__SWAP8(self._HL.high)
        self._m = 2

    def OPCode_CB35(self):
        #SWAP L
        self._HL.low = self.__SWAP8(self._HL.low)
        self._m = 2

    def OPCode_CB36(self):
        #SWAP [HL]
        value = self._mem.rb(self._HL.value)
        value = self.__SWAP8(value)
        self._mem.wb(value)
        self._m = 2


    def OPCode_27(self):
        #DAA
        a = self._AF.value
        if not(self.__IsFlagSet(Flags.SUB)):
            if self.__IsFlagSet(Flags.HALF_CARRY) or ((a & 0xF) > 0x9):
                a += 0x06

            if self.__IsFlagSet(Flags.CARRY) or (a > 0x9F):
                a += 0x60
        else:
            if self.__IsFlagSet(Flags.HALF_CARRY):
                a = (a-0x6) & 0xFF
            if self.__IsFLagSet(Flags.CARRY):
                a -= 0x60

        self.__ResetFlag(Flags.HALF_CARRY)
        self.__ResetFlag(Flags.ZERO)

        if (a & 0x100) == 0x100:
            self.__ToggleFlag(Flags.CARRY)

        a &= 0xFF
        if a == 0:
            self.__SetFlag(Flags.ZERO)

        self._AF.high = a
        self._m = 1

    def OPCode_2F(self):
        #CPL
        self._AF.high = (~self._AF.high & 0xFF)
        self.__SetFlag(Flags.SUB)
        self.__SetFlag(Flags.HALF_CARRY)
        self._m = 1

    def OPCode_3F(self):
        #CCF
        self.__ToggleFlag(Flags.CARRY)
        self.__ResetFlag(Flags.SUB)
        self.__ResetFlag(Flags.HALF_CARRY)
        self._m = 1

    def OPCode_37(self):
        #SCF
        self.__ResetFlag(Flags.SUB)
        self.__ResetFlag(Flags.HALF_CARRY)
        self._SetFlag(Flags.CARRY)
        self._m = 1

    def OPCode_78(self):
        #HALT
        self._halt = True
        self._m = 1

    def OPCode_1000(self):
        #STOP
        self._stop = True
        self._m = 1

    #TODO: Interruptions should stop after next instruction
    def OPCode_F3(self):
        #DI
        self._ime = False
        self._m = 1

    def OPCode_FB(self):
        #EI
        self._ime = True
        self._m = 1

    #Rotates and shifts
    def OPCode_17(self):
        #RLA
        self._AF.high = self.__RL(self._AF.high)
        self._m = 1

    def OPCode_07(self):
        #RLCA
        self._AF.high = self.__RLC(self._AF.high)
        self._m = 1

    def OPCode_1F(self):
        #RRA
        self._AF.high = self.__RR(self._AF.high)
        self._m = 1

    def OPCode_0F(self):
        #RRCA
        self._AF.high = self.__RRC(self._AF.high)
        self._m = 1

    def OPCode_CB07(self):
        #RLC A
        self._AF.high = self.__RLC(self._AF.high)
        self._m = 2

    def OPCode_CB00(self):
        #RLC B
        self._BC.high = self.__RLC(self._BC.high)
        self._m = 2

    def OPCode_CB01(self):
        #RLC C
        self._BC.low = self.__RLC(self._BC.low)
        self._m = 2

    def OPCode_CB02(self):
        #RLC D
        self._DE.high = self.__RLC(self._DE.high)
        self._m = 2

    def OPCode_CB03(self):
        #RLC E
        self._DE.low = self.__RLC(self._DE.low)
        self._m = 2

    def OPCode_CB04(self):
        #RLC H
        self._HL.high = self.__RLC(self._HL.high)
        self._m = 2

    def OPCode_CB05(self):
        #RLC L
        self._HL.low = self.__RLC(self._HL.low)
        self._m = 2

    def OPCode_CB06(self):
        #RLC [HL]
        value = self._mem.rb(self._HL.value)
        value = self.__RLC(value)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CB17(self):
        #RL A
        self._AF.high = self.__RL(self._AF.high)
        self._m = 2

    def OPCode_CB10(self):
        #RL B
        self._BC.high = self.__RL(self._BC.high)
        self._m = 2

    def OPCode_CB11(self):
        #RLB C
        self._BC.low = self.__RL(self._BC.low)
        self._m = 2

    def OPCode_CB12(self):
        #RL D
        self._DE.high = self.__RL(self._DE.high)
        self._m = 2

    def OPCode_CB13(self):
        #RL E
        self._DE.low = self.__RL(self._DE.low)
        self._m = 2

    def OPCode_CB14(self):
        #RL H
        self._HL.high = self.__RL(self._HL.high)
        self._m = 2

    def OPCode_CB15(self):
        #RL L
        self._HL.low = self.__RL(self._HL.low)
        self._m = 2

    def OPCode_CB16(self):
        #RL [HL]
        value = self._mem.rb(self._HL.value)
        value = self.__RL(value)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CB0F(self):
        #RRC A
        self._AF.high = self.__RRC(self._AF.high)
        self._m = 2

    def OPCode_CB08(self):
        #RRC B
        self._BC.high = self.__RRC(self._BC.high)
        self._m = 2

    def OPCode_CB09(self):
        #RRC C
        self._BC.low = self.__RRC(self._BC.low)
        self._m = 2

    def OPCode_CB0A(self):
        #RRC D
        self._DE.high = self.__RRC(self._DE.high)
        self._m = 2

    def OPCode_CB0B(self):
        #RRC E
        self._DE.low = self.__RRC(self._DE.low)
        self._m = 2

    def OPCode_CB0C(self):
        #RRC H
        self._HL.high = self.__RRC(self._HL.high)
        self._m = 2

    def OPCode_CB0D(self):
        #RRC L
        self._HL.low = self.__RRC(self._HL.low)
        self._m = 2

    def OPCode_CB0E(self):
        #RRC [HL]
        value = self._mem.rb(self._HL.value)
        value = self.__RRC(value)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CB1F(self):
        #RR A
        self._AF.high = self.__RR(self._AF.high)
        self._m = 2

    def OPCode_CB18(self):
        #RR B
        self._BC.high = self.__RR(self._BC.high)
        self._m = 2

    def OPCode_CB19(self):
        #RR C
        self._BC.low = self.__RR(self._BC.low)
        self._m = 2

    def OPCode_CB1A(self):
        #RR D
        self._DE.high = self.__RR(self._DE.high)
        self._m = 2

    def OPCode_CB1B(self):
        #RR E
        self._DE.low = self.__RR(self._DE.low)
        self._m = 2

    def OPCode_CB1C(self):
        #RR H
        self._HL.high = self.__RR(self._HL.high)
        self._m = 2

    def OPCode_CB1D(self):
        #RR L
        self._HL.low = self.__RR(self_HL.low)
        self._m = 2

    def OPCode_CB1E(self):
        #RR [HL]
        value = self._mem.rb(self._HL.value)
        value = self__RR(value)
        self._mem.wb(self._HL.value,value)
        self._m = 4


    def OPCode_CB27(self):
        #SLA A
        self._AF.high = self.__SLA(self._AF.high)
        self._m = 2
        
    def OPCode_CB20(self):
        #SLA B
        self._BC.high = self.__SLA(self._BC.high)
        self._m = 2
 
    def OPCode_CB21(self):
        #SLA C
        self._BC.low = self.__SLA(self._BC.low)
        self._m = 2
 
    def OPCode_CB22(self):
        #SLA D
        self._DE.high = self.__SLA(self._DE.high)
        self._m = 2
 
    def OPCode_CB23(self):
        #SLA E
        self._DE.low = self.__SLA(self._DE.low)
        self._m = 2
 
    def OPCode_CB24(self):
        #SLA H
        self._HL.high = self.__SLA(self._HL.high)
        self._m = 2
 
    def OPCode_CB25(self):
        #SLA L
        self._HL.low = self.__SLA(self._HL.low)
        self._m = 2
 
    def OPCode_CB26(self):
        #SLA [HL]
        value = self._mem.rb(self._HL.value)
        value = self.__SLA(value)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CB2F(self):
        #SRA A
        self._AF.high = self.__SRA(self._AF.high)
        self._m = 2

    def OPCode_CB28(self):
        #SRA B
        self._BC.high = self.__SRA(self._BC.high)
        self._m = 2

    def OPCode_CB29(self):
        #SRA C
        self._BC.low = self.__SRA(self._BC.low)
        self._m = 2

    def OPCode_CB2A(self):
        #SRA D
        self._DE.high = self.__SRA(self._DE.high)
        self._m = 2

    def OPCode_CB2B(self):
        #SRA E
        self._DE.high = self.__SRA(self._DE.high)
        self._m = 2

    def OPCode_CB2C(self):
        #SRA H
        self._HL.high = self.__SRA(self._HL.high)
        self._m = 2

    def OPCode_CB2D(self):
        #SRA L
        self._HL.low = self.__SRA(self._HL.low)
        self._m = 2

    def OPCode_CB2E(self):
        #SRA [HL]
        value = self._mem.rb(self._HL.value)
        value = self.__SRA(value)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CB3F(self):
        #SRL A
        self._AF.high = self.__SRL(self._AF.high)
        self._m = 2

    def OPCode_CB38(self):
        #SRL B
        self._BC.high = self.__SRL(self._BC.high)
        self._m = 2

    def OPCode_CB39(self):
        #SRL C
        self._BC.low = self.__SRL(self._BC.low)
        self._m = 2

    def OPCode_CB3A(self):
        #SRL D
        self._DE.high = self.__SRL(self._DE.high)
        self._m = 2

    def OPCode_CB3B(self):
        #SRL E
        self._DE.low = self.__SRL(self._DE.low)
        self._m = 2

    def OPCode_CB3C(self):
        #SRL H
        self._HL.high = self.__SRL(self._HL.high)
        self._m = 2

    def OPCode_CB3D(self):
        #SRL L
        self._HL.low = self.__SRL(self._HL.low)
        self._m = 2

    def OPCode_CB3E(self):
        #SRL [HL]
        value = self._mem.rb(self._HL.value)
        value = self.__SRL(value)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    #Bit OPcodes
    def OPCode_CB47(self):
        #BIT 0,A
        self.__BIT(self._AF.high,0)
        self._m = 2

    def OPCode_CB4F(self):
        #BIT 1,A
        self.__BIT(self._AF.high,1)
        self._m = 2
    
    def OPCode_CB57(self):
        #BIT 2,A
        self.__BIT(self._AF.high,2)
        self._m = 2

    def OPCode_CB5F(self):
        #BIT 3,A
        self.__BIT(self._AF.high,3)
        self._m = 2

    def OPCode_CB67(self):
        #BIT 4,A
        self.__BIT(self._AF.high,4)
        self._m = 2

    def OPCode_CB6F(self):
        #BIT 5,A
        self.__BIT(self._AF.high,5)
        self._m = 2

    def OPCode_CB77(self):
        #BIT 6,A
        self.__BIT(self._AF.high,6)
        self._m = 2

    def OPCode_CB7F(self):
        #BIT 7,A
        self.__BIT(self._AF.high,7)
        self._m = 2

    def OPCode_CB40(self):
        #BIT 0,B
        self.__BIT(self._BC.high,0)
        self._m = 2

    def OPCode_CB48(self):
        #BIT 1,B
        self.__BIT(self._BC.high,1)
        self._m = 2

    def OPCode_CB50(self):
        #BIT 2,B
        self.__BIT(self._BC.high,2)
        self._m = 2

    def OPCode_CB58(self):
        #BIT 3,B
        self.__BIT(self._BC.high,3)
        self._m = 2

    def OPCode_CB60(self):
        #BIT 4,B
        self.__BIT(self._BC.high,4)
        self._m = 2

    def OPCode_CB68(self):
        #BIT 5,B
        self.__BIT(self._BC.high,5)
        self._m = 2

    def OPCode_CB70(self):
        #BIT 6,B
        self.__BIT(self._BC.high,6)
        self._m = 2

    def OPCode_CB78(self):
        #BIT 7,B
        self.__BIT(self._BC.high,7)
        self._m = 2

    def OPCode_CB41(self):
        #BIT 0,C
        self.__BIT(self._BC.low,0)
        self._m = 2

    def OPCode_CB49(self):
        #BIT 1,C
        self.__BIT(self._BC.low,1)
        self._m = 2

    def OPCode_CB51(self):
        #BIT 2,C
        self.__BIT(self._BC.low,2)
        self._m = 2

    def OPCode_CB59(self):
        #BIT 3,C
        self.__BIT(self._BC.low,3)
        self._m = 2

    def OPCode_CB61(self):
        #BIT 4,C
        self.__BIT(self._BC.low,4)
        self._m = 2

    def OPCode_CB69(self):
        #BIT 5,C
        self.__BIT(self._BC.low,5)
        self._m = 2

    def OPCode_CB71(self):
        #BIT 6,C
        self.__BIT(self._BC.low,6)
        self._m = 2

    def OPCode_CB79(self):
        #BIT 7,C
        self.__BIT(self._BC.low,7)
        self._m = 2

    def OPCode_CB42(self):
        #BIT 0,D
        self.__BIT(self._DE.high,0)
        self._m = 2

    def OPCode_CB4A(self):
        #BIT 1,D
        self.__BIT(self._DE.high,1)
        self._m = 2

    def OPCode_CB52(self):
        #BIT 2,D
        self.__BIT(self._DE.high,2)
        self._m = 2

    def OPCode_CB5A(self):
        #BIT 3,D
        self.__BIT(self._DE.high,3)
        self._m = 2

    def OPCode_CB62(self):
        #BIT 4,D
        self.__BIT(self._DE.high,4)
        self._m = 2

    def OPCode_CB6A(self):
        #BIT 5,D
        self.__BIT(self._DE.high,5)
        self._m = 2

    def OPCode_CB72(self):
        #BIT 6,D
        self.__BIT(self._DE.high,6)
        self._m = 2

    def OPCode_CB7A(self):
        #BIT 7,D
        self.__BIT(self._DE.high,7)
        self._m = 2

    def OPCode_CB43(self):
        #BIT 0,E
        self.__BIT(self._DE.low,0)
        self._m = 2

    def OPCode_CB4B(self):
        #BIT 1,E
        self.__BIT(self._DE.low,1)
        self._m = 2

    def OPCode_CB53(self):
        #BIT 2,E
        self.__BIT(self._DE.low,2)
        self._m = 2

    def OPCode_CB5B(self):
        #BIT 3,E
        self.__BIT(self._DE.low,3)
        self._m = 2

    def OPCode_CB63(self):
        #BIT 4,E
        self.__BIT(self._DE.low,4)
        self._m = 2

    def OPCode_CB6B(self):
        #BIT 5,E
        self.__BIT(self._DE.low,5)
        self._m = 2

    def OPCode_CB73(self):
        #BIT 6,E
        self.__BIT(self._DE.low,6)
        self._m = 2

    def OPCode_CB7B(self):
        #BIT 7,E
        self.__BIT(self._DE.low,7)
        self._m = 2

    def OPCode_CB44(self):
        #BIT 0,H
        self.__BIT(self._HL.high,0)
        self._m = 2

    def OPCode_CB4C(self):
        #BIT 1,H
        self.__BIT(self._HL.high,1)
        self._m = 2

    def OPCode_CB54(self):
        #BIT 2,H
        self.__BIT(self._HL.high,2)
        self._m = 2

    def OPCode_CB5C(self):
        #BIT 3,H
        self.__BIT(self._HL.high,3)
        self._m = 2

    def OPCode_CB64(self):
        #BIT 4,H
        self.__BIT(self._HL.high,4)
        self._m = 2

    def OPCode_CB6C(self):
        #BIT 5,H
        self.__BIT(self._HL.high,5)
        self._m = 2

    def OPCode_CB74(self):
        #BIT 6,H
        self.__BIT(self._HL.high,6)
        self._m = 2

    def OPCode_CB7C(self):
        #BIT 7,H
        self.__BIT(self._HL.high,7)
        self._m = 2

    def OPCode_CB45(self):
        #BIT 0,L
        self.__BIT(self._HL.low,0)
        self._m = 2

    def OPCode_CB4D(self):
        #BIT 1,L
        self.__BIT(self._HL.low,1)
        self._m = 2

    def OPCode_CB55(self):
        #BIT 2,L
        self.__BIT(self._HL.low,2)
        self._m = 2

    def OPCode_CB5D(self):
        #BIT 3,L
        self.__BIT(self._HL.low,3)
        self._m = 2

    def OPCode_CB65(self):
        #BIT 4,L
        self.__BIT(self._HL.low,4)
        self._m = 2

    def OPCode_CB6D(self):
        #BIT 5,L
        self.__BIT(self._HL.low,5)
        self._m = 2

    def OPCode_CB75(self):
        #BIT 6,L
        self.__BIT(self._HL.low,6)
        self._m = 2

    def OPCode_CB7D(self):
        #BIT 7,L
        self.__BIT(self._HL.low,7)
        self._m = 2

    def OPCode_CB46(self):
        #BIT 0,[HL]
        value = self._mem.rb(self._HL.value)
        self.__BIT(value,0)
        self._m = 4

    def OPCode_CB4E(self):
        #BIT 1,[HL]
        value = self._mem.rb(self._HL.value)
        self.__BIT(value,1)
        self._m = 4

    def OPCode_CB56(self):
        #BIT 2,[HL]
        value = self._mem.rb(self._HL.value)
        self.__BIT(value,2)
        self._m = 4

    def OPCode_CB5E(self):
        #BIT 3,[HL]
        value = self._mem.rb(self._HL.value)
        self.__BIT(value,3)
        self._m = 4

    def OPCode_CB66(self):
        #BIT 4,[HL]
        value = self._mem.rb(self._HL.value)
        self.__BIT(value,4)
        self._m = 4

    def OPCode_CB6E(self):
        #BIT 5,[HL]
        value = self._mem.rb(self._HL.value)
        self.__BIT(value,5)
        self._m = 4

    def OPCode_CB76(self):
        #BIT 6,[HL]
        value = self._mem.rb(self._HL.value)
        self.__BIT(value,6)
        self._m = 4

    def OPCode_CB7E(self):
        #BIT 7,[HL]
        value = self._mem.rb(self._HL.value)
        self.__BIT(value,7)
        self._m = 4

    def OPCode_CBC7(self):
        #SET 0,A
        self._AF.high = elf.__SET(self._AF.high,0)
        self._m = 2

    def OPCode_CBCF(self):
        #SET 1,A
        self._AF.high = elf.__SET(self._AF.high,1)
        self._m = 2
    
    def OPCode_CBD7(self):
        #SET 2,A
        self._AF.high = elf.__SET(self._AF.high,2)
        self._m = 2

    def OPCode_CBDF(self):
        #SET 3,A
        self._AF.high = elf.__SET(self._AF.high,3)
        self._m = 2

    def OPCode_CBE7(self):
        #SET 4,A
        self._AF.high = elf.__SET(self._AF.high,4)
        self._m = 2

    def OPCode_CBEF(self):
        #SET 5,A
        self._AF.high = elf.__SET(self._AF.high,5)
        self._m = 2

    def OPCode_CBF7(self):
        #SET 6,A
        self._AF.high = elf.__SET(self._AF.high,6)
        self._m = 2

    def OPCode_CBFF(self):
        #SET 7,A
        self._AF.high = elf.__SET(self._AF.high,7)
        self._m = 2

    def OPCode_CBC0(self):
        #SET 0,B
        self._AF.high = self.__SET(self._BC.high,0)
        self._m = 2

    def OPCode_CBC8(self):
        #SET 1,B
        self._BC.high = self.__SET(self._BC.high,1)
        self._m = 2

    def OPCode_CBD0(self):
        #SET 2,B
        self._BC.high = self.__SET(self._BC.high,2)
        self._m = 2

    def OPCode_CBD8(self):
        #SET 3,B
        self._BC.high = self.__SET(self._BC.high,3)
        self._m = 2

    def OPCode_CBE0(self):
        #SET 4,B
        self._BC.high = self.__SET(self._BC.high,4)
        self._m = 2

    def OPCode_CBE8(self):
        #SET 5,B
        self._BC.high = self.__SET(self._BC.high,5)
        self._m = 2

    def OPCode_CBF0(self):
        #SET 6,B
        self._BC.high = self.__SET(self._BC.high,6)
        self._m = 2

    def OPCode_CBF8(self):
        #SET 7,B
        self._BC.high = self.__SET(self._BC.high,7)
        self._m = 2

    def OPCode_CBC1(self):
        #SET 0,C
        self._BC.low = self.__SET(self._BC.low,0)
        self._m = 2

    def OPCode_CBC9(self):
        #SET 1,C
        self._BC.low = self.__SET(self._BC.low,1)
        self._m = 2

    def OPCode_CBD1(self):
        #SET 2,C
        self._BC.low = self.__SET(self._BC.low,2)
        self._m = 2

    def OPCode_CBD9(self):
        #SET 3,C
        self._BC.low = self.__SET(self._BC.low,3)
        self._m = 2

    def OPCode_CBE1(self):
        #SET 4,C
        self._BC.low = self.__SET(self._BC.low,4)
        self._m = 2

    def OPCode_CBE9(self):
        #SET 5,C
        self._BC.low = self.__SET(self._BC.low,5)
        self._m = 2

    def OPCode_CBF1(self):
        #SET 6,C
        self._BC.low = self.__SET(self._BC.low,6)
        self._m = 2

    def OPCode_CBF9(self):
        #SET 7,C
        self._BC.low = self.__SET(self._BC.low,7)
        self._m = 2

    def OPCode_CBC2(self):
        #SET 0,D
        self._DE.high = self.__SET(self._DE.high,0)
        self._m = 2

    def OPCode_CBCA(self):
        #SET 1,D
        self._DE.high = self.__SET(self._DE.high,1)
        self._m = 2

    def OPCode_CBD2(self):
        #SET 2,D
        self._DE.high = self.__SET(self._DE.high,2)
        self._m = 2

    def OPCode_CBDA(self):
        #SET 3,D
        self._DE.high = self.__SET(self._DE.high,3)
        self._m = 2

    def OPCode_CBE2(self):
        #SET 4,D
        self._DE.high = self.__SET(self._DE.high,4)
        self._m = 2

    def OPCode_CBEA(self):
        #SET 5,D
        self._DE.high = self.__SET(self._DE.high,5)
        self._m = 2

    def OPCode_CBF2(self):
        #SET 6,D
        self._DE.high = self.__SET(self._DE.high,6)
        self._m = 2

    def OPCode_CBFA(self):
        #SET 7,D
        self._DE.high = self.__SET(self._DE.high,7)
        self._m = 2

    def OPCode_CBC3(self):
        #SET 0,E
        self._DE.low = self._SET(self._DE.low,0)
        self._m = 2

    def OPCode_CBCB(self):
        #SET 1,E
        self._DE.low = self._SET(self._DE.low,1)
        self._m = 2

    def OPCode_CBD3(self):
        #SET 2,E
        self._DE.low = self._SET(self._DE.low,2)
        self._m = 2

    def OPCode_CBDB(self):
        #SET 3,E
        self._DE.low = self._SET(self._DE.low,3)
        self._m = 2

    def OPCode_CBE3(self):
        #SET 4,E
        self._DE.low = self._SET(self._DE.low,4)
        self._m = 2

    def OPCode_CBEB(self):
        #SET 5,E
        self._DE.low = self._SET(self._DE.low,5)
        self._m = 2

    def OPCode_CBF3(self):
        #SET 6,E
        self._DE.low = self._SET(self._DE.low,6)
        self._m = 2

    def OPCode_CBFB(self):
        #SET 7,E
        self._DE.low = self._SET(self._DE.low,7)
        self._m = 2

    def OPCode_CBC4(self):
        #SET 0,H
        self._HL.high = self.__SET(self._HL.high,0)
        self._m = 2

    def OPCode_CBCC(self):
        #SET 1,H
        self._HL.high = self.__SET(self._HL.high,1)
        self._m = 2

    def OPCode_CBD4(self):
        #SET 2,H
        self._HL.high = self.__SET(self._HL.high,2)
        self._m = 2

    def OPCode_CBDC(self):
        #SET 3,H
        self._HL.high = self.__SET(self._HL.high,3)
        self._m = 2

    def OPCode_CBE4(self):
        #SET 4,H
        self._HL.high = self.__SET(self._HL.high,4)
        self._m = 2

    def OPCode_CBEC(self):
        #SET 5,H
        self._HL.high = self.__SET(self._HL.high,5)
        self._m = 2

    def OPCode_CBF4(self):
        #SET 6,H
        self._HL.high = self.__SET(self._HL.high,6)
        self._m = 2

    def OPCode_CBFC(self):
        #SET 7,H
        self._HL.high = self.__SET(self._HL.high,7)
        self._m = 2

    def OPCode_CBC5(self):
        #SET 0,L
        self._HL.low = self.__SET(self._HL.low,0)
        self._m = 2

    def OPCode_CBCD(self):
        #SET 1,L
        self._HL.low = self.__SET(self._HL.low,1)
        self._m = 2

    def OPCode_CBD5(self):
        #SET 2,L
        self._HL.low = self.__SET(self._HL.low,2)
        self._m = 2

    def OPCode_CBDD(self):
        #SET 3,L
        self._HL.low = self.__SET(self._HL.low,3)
        self._m = 2

    def OPCode_CBE5(self):
        #SET 4,L
        self._HL.low = self.__SET(self._HL.low,4)
        self._m = 2

    def OPCode_CBED(self):
        #SET 5,L
        self._HL.low = self.__SET(self._HL.low,5)
        self._m = 2

    def OPCode_CBF5(self):
        #SET 6,L
        self._HL.low = self.__SET(self._HL.low,6)
        self._m = 2

    def OPCode_CBFD(self):
        #SET 7,L
        self._HL.low = self.__SET(self._HL.low,7)
        self._m = 2

    def OPCode_CBC6(self):
        #SET 0,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__SET(value,0)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CBCE(self):
        #SET 1,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__SET(value,1)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CBD6(self):
        #SET 2,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__SET(value,2)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CBDE(self):
        #SET 3,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__SET(value,3)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CBE6(self):
        #SET 4,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__SET(value,4)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CBEE(self):
        #SET 5,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__SET(value,5)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CBF6(self):
        #SET 6,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__SET(value,6)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CBFE(self):
        #SET 7,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__SET(value,7)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CB87(self):
        #RES 0,A
        self._AF.high = elf.__RES(self._AF.high,0)
        self._m = 2

    def OPCode_CB8F(self):
        #RES 1,A
        self._AF.high = elf.__RES(self._AF.high,1)
        self._m = 2
    
    def OPCode_CB97(self):
        #RES 2,A
        self._AF.high = elf.__RES(self._AF.high,2)
        self._m = 2

    def OPCode_CB9F(self):
        #RES 3,A
        self._AF.high = elf.__RES(self._AF.high,3)
        self._m = 2

    def OPCode_CBA7(self):
        #RES 4,A
        self._AF.high = elf.__RES(self._AF.high,4)
        self._m = 2

    def OPCode_CBAF(self):
        #RES 5,A
        self._AF.high = elf.__RES(self._AF.high,5)
        self._m = 2

    def OPCode_CBB7(self):
        #RES 6,A
        self._AF.high = elf.__RES(self._AF.high,6)
        self._m = 2

    def OPCode_CBBF(self):
        #RES 7,A
        self._AF.high = elf.__RES(self._AF.high,7)
        self._m = 2

    def OPCode_CB80(self):
        #RES 0,B
        self._AF.high = self.__RES(self._BC.high,0)
        self._m = 2

    def OPCode_CB88(self):
        #RES 1,B
        self._BC.high = self.__RES(self._BC.high,1)
        self._m = 2

    def OPCode_CB90(self):
        #RES 2,B
        self._BC.high = self.__RES(self._BC.high,2)
        self._m = 2

    def OPCode_CB98(self):
        #RES 3,B
        self._BC.high = self.__RES(self._BC.high,3)
        self._m = 2

    def OPCode_CBA0(self):
        #RES 4,B
        self._BC.high = self.__RES(self._BC.high,4)
        self._m = 2

    def OPCode_CBA8(self):
        #RES 5,B
        self._BC.high = self.__RES(self._BC.high,5)
        self._m = 2

    def OPCode_CBB0(self):
        #RES 6,B
        self._BC.high = self.__RES(self._BC.high,6)
        self._m = 2

    def OPCode_CBB8(self):
        #RES 7,B
        self._BC.high = self.__RES(self._BC.high,7)
        self._m = 2

    def OPCode_CB81(self):
        #RES 0,C
        self._BC.low = self.__RES(self._BC.low,0)
        self._m = 2

    def OPCode_CB89(self):
        #RES 1,C
        self._BC.low = self.__RES(self._BC.low,1)
        self._m = 2

    def OPCode_CB91(self):
        #RES 2,C
        self._BC.low = self.__RES(self._BC.low,2)
        self._m = 2

    def OPCode_CB99(self):
        #RES 3,C
        self._BC.low = self.__RES(self._BC.low,3)
        self._m = 2

    def OPCode_CBA1(self):
        #RES 4,C
        self._BC.low = self.__RES(self._BC.low,4)
        self._m = 2

    def OPCode_CBA9(self):
        #RES 5,C
        self._BC.low = self.__RES(self._BC.low,5)
        self._m = 2

    def OPCode_CBB1(self):
        #RES 6,C
        self._BC.low = self.__RES(self._BC.low,6)
        self._m = 2

    def OPCode_CBB9(self):
        #RES 7,C
        self._BC.low = self.__RES(self._BC.low,7)
        self._m = 2

    def OPCode_CB82(self):
        #RES 0,D
        self._DE.high = self.__RES(self._DE.high,0)
        self._m = 2

    def OPCode_CB8A(self):
        #RES 1,D
        self._DE.high = self.__RES(self._DE.high,1)
        self._m = 2

    def OPCode_CB92(self):
        #RES 2,D
        self._DE.high = self.__RES(self._DE.high,2)
        self._m = 2

    def OPCode_CB9A(self):
        #RES 3,D
        self._DE.high = self.__RES(self._DE.high,3)
        self._m = 2

    def OPCode_CBA2(self):
        #RES 4,D
        self._DE.high = self.__RES(self._DE.high,4)
        self._m = 2

    def OPCode_CBAA(self):
        #RES 5,D
        self._DE.high = self.__RES(self._DE.high,5)
        self._m = 2

    def OPCode_CBB2(self):
        #RES 6,D
        self._DE.high = self.__RES(self._DE.high,6)
        self._m = 2

    def OPCode_CBBA(self):
        #RES 7,D
        self._DE.high = self.__RES(self._DE.high,7)
        self._m = 2

    def OPCode_CB83(self):
        #RES 0,E
        self._DE.low = self._RES(self._DE.low,0)
        self._m = 2

    def OPCode_CB8B(self):
        #RES 1,E
        self._DE.low = self._RES(self._DE.low,1)
        self._m = 2

    def OPCode_CB93(self):
        #RES 2,E
        self._DE.low = self._RES(self._DE.low,2)
        self._m = 2

    def OPCode_CB9B(self):
        #RES 3,E
        self._DE.low = self._RES(self._DE.low,3)
        self._m = 2

    def OPCode_CBA3(self):
        #RES 4,E
        self._DE.low = self._RES(self._DE.low,4)
        self._m = 2

    def OPCode_CBAB(self):
        #RES 5,E
        self._DE.low = self._RES(self._DE.low,5)
        self._m = 2

    def OPCode_CBB3(self):
        #RES 6,E
        self._DE.low = self._RES(self._DE.low,6)
        self._m = 2

    def OPCode_CBBB(self):
        #RES 7,E
        self._DE.low = self._RES(self._DE.low,7)
        self._m = 2

    def OPCode_CB84(self):
        #RES 0,H
        self._HL.high = self.__RES(self._HL.high,0)
        self._m = 2

    def OPCode_CB8C(self):
        #RES 1,H
        self._HL.high = self.__RES(self._HL.high,1)
        self._m = 2

    def OPCode_CB94(self):
        #RES 2,H
        self._HL.high = self.__RES(self._HL.high,2)
        self._m = 2

    def OPCode_CB9C(self):
        #RES 3,H
        self._HL.high = self.__RES(self._HL.high,3)
        self._m = 2

    def OPCode_CBA4(self):
        #RES 4,H
        self._HL.high = self.__RES(self._HL.high,4)
        self._m = 2

    def OPCode_CBAC(self):
        #RES 5,H
        self._HL.high = self.__RES(self._HL.high,5)
        self._m = 2

    def OPCode_CBB4(self):
        #RES 6,H
        self._HL.high = self.__RES(self._HL.high,6)
        self._m = 2

    def OPCode_CBBC(self):
        #RES 7,H
        self._HL.high = self.__RES(self._HL.high,7)
        self._m = 2

    def OPCode_CB85(self):
        #RES 0,L
        self._HL.low = self.__RES(self._HL.low,0)
        self._m = 2

    def OPCode_CB8D(self):
        #RES 1,L
        self._HL.low = self.__RES(self._HL.low,1)
        self._m = 2

    def OPCode_CB95(self):
        #RES 2,L
        self._HL.low = self.__RES(self._HL.low,2)
        self._m = 2

    def OPCode_CB9D(self):
        #RES 3,L
        self._HL.low = self.__RES(self._HL.low,3)
        self._m = 2

    def OPCode_CBA5(self):
        #RES 4,L
        self._HL.low = self.__RES(self._HL.low,4)
        self._m = 2

    def OPCode_CBAD(self):
        #RES 5,L
        self._HL.low = self.__RES(self._HL.low,5)
        self._m = 2

    def OPCode_CBB5(self):
        #RES 6,L
        self._HL.low = self.__RES(self._HL.low,6)
        self._m = 2

    def OPCode_CBBD(self):
        #RES 7,L
        self._HL.low = self.__RES(self._HL.low,7)
        self._m = 2

    def OPCode_CB86(self):
        #RES 0,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__RES(value,0)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CB8E(self):
        #RES 1,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__RES(value,1)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CB96(self):
        #RES 2,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__RES(value,2)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CB9E(self):
        #RES 3,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__RES(value,3)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CBA6(self):
        #RES 4,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__RES(value,4)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CBAE(self):
        #RES 5,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__RES(value,5)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CBB6(self):
        #RES 6,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__RES(value,6)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    def OPCode_CBBE(self):
        #RES 7,[HL]
        value = self._mem.rb(self._HL.value)
        value = self.__RES(value,7)
        self._mem.wb(self._HL.value,value)
        self._m = 4

    #Jumps
    def OPCode_C3(self):
        #JP nn
        self._PC.value = self._mem.rw(self._PC.value)
        self._m = 3

    def OPCode_C2(self):
        #JP NZ,nn
        addr = self._mem.rw(self._PC.value)
        self._PC.value += 2
        if not(self.__IsFlagSet(Flags.ZERO)):
            self._PC.value = addr
        self._m = 3

    def OPCode_CA(self):
        #JP Z,nn
        addr = self._mem.rw(self._PC.value)
        self._PC.value += 2
        if self.__IsFlagSet(Flags.ZERO):
            self._PC.value = addr
        self._m = 3

    def OPCode_D2(self):
        #JP NC,nn
        addr = self._mem.rw(self._PC.value)
        self._PC.value += 2
        if not(self.__IsFlagSet(Flags.CARRY)):
            self._PC.value = addr
        self._m = 3

    def OPCode_DA(self):
        #JP C,nn
        addr = self._mem.rw(self._PC.value)
        self._PC.value += 2
        if self.__IsFlagSet(Flags.CARRY):
            self._PC.value = addr
        self._m = 3

    def OPCode_E9(self):
        #JP HL
        self._PC.value = self._HL.value
        self._m = 1

    def OPCode_18(self):
        #JR n
        value = self._mem.rb(self._PC.value)
        self._PC.value += 1
        value = self.__OFFSET8(value)
        self._PC.value += value
        self._m = 2

    def OPCode_20(self):
        #JR NZ,n
        value = self._mem.rb(self._PC.value)
        value = self.__OFFSET8(value)
        self._PC.value += 1

        if not(self.__IsFlagSet(Flags.ZERO)):
            self._PC.value += value
        
        self._m = 2

    def OPCode_28(self):
        #JR Z,n
        value = self._mem.rb(self._PC.value)
        value = self.__OFFSET8(value)
        self._PC.value += 1
        if self.__IsFlagSet(Flags.ZERO):
            self._PC.value += value
        self._m = 2

    def OPCode_30(self):
        #JR NC,n
        value = self._mem.rb(self._PC.value)
        value = self.__OFFSET8(value)
        self._PC.value += 1
        if not(self.__IsFlagSet(Flags.CARRY)):
            self._PC.value += value
        self._m = 2

    def OPCode_38(self):
        #JR C,n
        value = self._mem.rb(self._PC.value)
        value = self.__OFFSET8(value)
        self._PC.value += 1
        if self.__IsFlagSet(Flags.CARRY):
            self._PC.value += value
        self._m = 2
       
    #CALLS
    def OPCode_CD(self):
        #CALL nn
        addr = self._mem.rw(self._PC.value)
        self._PC.value += 2
        self.__PUSH(self._PC.value)
        self._PC.value = addr
        self._m = 3

    def OPCode_C4(self):
        #CALL NZ,nn
        addr = self._mem.rw(self._PC.value)
        self._PC.value += 2
        if not(self.__IsFlagSet(Flags.ZERO)):
            self.__PUSH(self._PC.value)
            self._PC.value = addr
        self._m = 3

    def OPCode_CC(self):
        #CALL Z,nn
        addr = self._mem.rw(self._PC.value)
        self._PC.value += 2
        if self.__IsFlagSet(Flags.ZERO):
            self.__PUSH(self._PC.value)
            self._PC.value = addr
        self._m = 3

    def OPCode_D4(self):
        #CALL NC,nn
        addr = self._mem.rw(self._PC.value)
        self._PC.value += 2
        if not(self.__IsFlagSet(Flags.CARRY)):
            self.__PUSH(self._PC.value)
            self._PC.value = addr
        self._m = 3

    def OPCode_DC(self):
        #CALL C,nn
        addr = self._mem.rw(self._PC.value)
        self._PC.value += 2
        if self.__IsFlagSet(Flags.CARRY):
            self.__PUSH(self._PC.value)
            self._PC.value = addr
        self._m = 3

    #Restarts
    def OPCode_C7(self):
        #RST 0
        self.__PUSH(self._PC.value)
        self._PC.value = 0x0
        self._m = 8

    def OPCode_CF(self):
        #RST 8
        self.__PUSH(self._PC.value)
        self._PC.value = 0x8
        self._m = 8

    def OPCode_D7(self):
        #RST 10
        self.__PUSH(self._PC.value)
        self._PC.value = 0x10
        self._m = 8

    def OPCode_DF(self):
        #RST 18
        self.__PUSH(self._PC.value)
        self._PC.value = 0x18
        self._m = 8

    def OPCode_E7(self):
        #RST 20
        self.__PUSH(self._PC.value)
        self._PC.value = 0x20
        self._m = 8

    def OPCode_EF(self):
        #RST 28
        self.__PUSH(self._PC.value)
        self._PC.value = 0x28
        self._m = 8
        
    def OPCode_F7(self):
        #RST 30
        self.__PUSH(self._PC.value)
        self._PC.value = 0x30
        self._m = 8

    def OPCode_FF(self):
        #RST 38
        self.__PUSH(self._PC.value)
        self._PC.value = 0x38
        self._m = 8

    #Returns
    def OPCode_C9(self):
        #RET
        self._PC.value = self.__POP()
        self._m = 2

    def OPCode_C0(self):
        #RET NZ
        if not(self.__IsFlagSet(Flags.ZERO)):
            self._PC.value = self.__POP()
        self._m = 2

    def OPCode_C8(self):
        #RET Z
        if self.__IsFlagSet(Flags.ZERO):
            self._PC.value = self.__POP()
        self._m = 2

    def OPCode_D0(self):
        #RET NC
        if not(self.__IsFlagSet(Flags.CARRY)):
            self._PC.value = self.__POP()
        self._m = 2

    def OPCode_D8(self):
        #RET C
        if self.__IsFlagSet(Flags.CARRY):
            self._PC.value = self.__POP()
        self._m = 2

    def OPCode_D9(self):
        self._PC.value = self.__POP()
        self._ime = True
        self._m = 2

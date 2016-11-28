class R16(object):
    def __init__(self):
        self._l = R8()
        self._h = R8()

    @property
    def value(self):
        return (self._h.value << 8) | self._l.value
    
    @value.setter
    def value(self,val):
        val &= 0xFFFF
        self._l.value = val & 0xFF
        self._h.value = val >> 8

    @property
    def high(self):
        return self._h.value
    
    @property
    def low(self):
        return self._l.value

    @low.setter
    def low(self,value):
        self._l.value = value
    
    @high.setter
    def high(self,value):
        self._h.value = value



class R8(object):
    def __init__(self):
        self._value = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,val):
        self._value = val
        self._value &= 0xFF

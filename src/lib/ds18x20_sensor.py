class DS18X20():
    def __init__(self, dssensor, rom, **kwargs) -> None:
        """
        :param ds18x20.DS18X20 dssensor: instance of micropythons built-in DS18X20 class
        :param bytearray rom: Bytearray address of the sensor
        :param str friendlyname: Friendlyname for human readable sensor name
        """

        self.dssensor = dssensor
        self.rom: bytearray = rom if isinstance(rom, bytearray) else self.str2rom(rom)
        self._friendlyname = kwargs.get("friendlyname", self.rom2str())

    def __repr__(self) -> str:
        return f'<{self.rom} : {self.friendlyname}>'

    def __eq__(self, other: object) -> bool:
        return self.rom == other.rom

    def __lt__(self, other:object):
        return self.rom2str() < other.rom2str()

    @property
    def friendlyname(self):
        return self._friendlyname

    @friendlyname.setter
    def friendlyname(self, fname):
        self._friendlyname = fname

    def read_temp(self) -> str:
        temp = self.dssensor.read_temp(self.rom)
        return '{0:.2f}'.format(temp)

    def rom2str(self) -> str:
        return ''.join('%02X' % i for i in iter(self.rom))

    def str2rom(self, rom) -> bytearray:
        a = bytearray(8)
        for i in range(8):
            a[i] = int(rom[i * 2:i * 2 + 2], 16)
        return a

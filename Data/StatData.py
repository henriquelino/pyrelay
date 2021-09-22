from Constants.StatTypes import *
import Data.CompressedInt as CompressedInt

types = StatTypes()

class StatData:
    def __init__(self, statType=0, statValue=0, strStatValue="", secondaryValue=0):
        self.statType = statType
        self.statValue = statValue
        self.strStatValue = strStatValue
        self.secondaryValue = secondaryValue

    def isStringStat(self):
        return self.statType in [types.NAMESTAT, types.ACCOUNTIDSTAT, types.GUILDNAMESTAT,
                                 types.PETNAMESTAT, types.GRAVEACCOUNTID, types.OWNERACCOUNTIDSTAT,
                                 types.UNKNOWN80, types.UNKNOWN121, types.UNKNOWN123]

    def statToName(self, type=None):
        if type is None:
            return types.nameOf(self.statType)
        else:
            return types.nameOf(type)   

    def read(self, reader):
        self.statType = reader.readUnsignedByte()
        if self.isStringStat():
            self.strStatValue = reader.readStr()
        else:
            self.statValue = CompressedInt.read(reader)
        self.secondaryValue = CompressedInt.read(reader)

    def write(self, writer):
        writer.writeUnsignedByte(self.statType)
        if self.isStringStat():
            writer.writeStr(self.strStatValue)
        else:
            writer.writeInt32(self.statValue)

    def clone(self):
        return StatData(self.statType, self.statValue, self.strStatValue)

    def __str__(self):
        if self.isStringStat():
            return f"statType: {self.statType}\nstrStatValue: {self.strStatValue}\nsecondaryValue: {self.secondaryValue}"
        else:
            return f"statType: {self.statType}\nstatValue: {self.statValue}\nsecondaryValue: {self.secondaryValue}"


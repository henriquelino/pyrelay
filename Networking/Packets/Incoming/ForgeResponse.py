from Data.SlotObjectData import SlotObjectData

class ForgeRespnsePacket:
    def __init__(self):
        self.type = "FORGERESPONSE"
        self.slot = SlotObjectData()

    def read(self, reader):
        print(reader.buffer)
        self.slot.read(reader)

    def write(self, writer):
        self.slot.write(writer)
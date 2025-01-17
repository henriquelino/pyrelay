class MapInfoPacket:
    def __init__(self):
        self.type = "MAPINFO"
        self.width = 0
        self.height = 0
        self.name = ""
        self.displayName = ""
        self.realmName = ""
        self.fp = 0
        self.background = 0
        self.difficulty = 0
        self.allowPlayerTeleport = False
        self.showDisplays = False
        self.maxPlayers = 0
        self.gameOpenedTime = 0
        self.buildVersion = ""

    def read(self, reader):
        self.width = reader.readInt32()
        self.height = reader.readInt32()
        self.name = reader.readStr()
        self.displayName = reader.readStr()
        self.realmName = reader.readStr()
        self.fp = reader.readUInt32()
        self.background = reader.readInt32()
        self.difficulty = reader.readInt32()
        self.allowPlayerTeleport = reader.readBool()
        self.showDisplays = reader.readBool()
        self.maxPlayers = reader.readShort()
        self.gameOpenedTime = reader.readUInt32()
        self.buildVersion = reader.readStr()
        self.unknownString = reader.readStr32()

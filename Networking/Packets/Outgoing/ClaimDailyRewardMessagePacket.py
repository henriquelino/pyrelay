class ClaimDailyRewardMessagePacket:
    def __init__(self):
        self.type = "CLAIMLOGINREWARDMSG"
        self.claimKey = ''
        self.claimType = ''

    def write(self, writer):
        writer.writeStr(self.claimKey)
        writer.writeStr(self.claimType)

    def read(self, reader):
        self.claimKey = reader.readStr()
        self.claimType = reader.readStr()

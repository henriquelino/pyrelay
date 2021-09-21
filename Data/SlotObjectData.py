
class SlotObjectData:
    def __init__(self, objectId=0, slotId=0, objectType=0):
        # The object id of the entity which owns the slot.
        self.objectId = objectId
        
        # The index of the slot. E.g. The 4th inventory slot has the slot id 3.
        self.slotId = slotId
        
        # The item id of the item in the slot, or -1 if it is empty.
        self.objectType = objectType

    def read(self, reader):
        self.objectId = reader.readInt32()
        self.slotId = reader.readInt32()
        self.objectType = reader.readInt32()

    def write(self, writer):
        writer.writeInt32(self.objectId)
        writer.writeInt32(self.slotId)
        writer.writeInt32(self.objectType)

    def __str__(self):
        return f"SlotObjectData\nobjectId: {self.objectId}\nslotId: {self.slotId}\nobjectType: {self.objectType}"

    def clone(self):
        return SlotObjectData(self.objectId, self.slotId, self.objectType)
        

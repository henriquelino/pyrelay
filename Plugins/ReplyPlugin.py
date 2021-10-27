import time
import json
from Networking.PacketHelper import CreatePacket
from PluginManager import hook, plugin

shouldEnter = False

#All plugins should have a plugin decorater
@plugin(active=True)
class ReplyPlugin:
    def __init__(self):
        with open('owner.json', 'r') as f:
            infos = json.load(f)
        
        self.owner = infos['owner']
        self.password = infos['password']

    #To hook a packet use the hook decorator with the packet type you wish to hook
    @hook("text")
    def onText(self, client, packet):
        global shouldEnter
        if packet.name == self.owner and packet.recipient == client.playerData.name:
            if packet.text.lower() == "hello":
                replyPacket = CreatePacket("PLAYERTEXT")
                replyPacket.text = f"/tell {packet.name} Hey!"
                client.send(replyPacket)
                
            elif packet.text.lower() == "pos":
                replyPacket = CreatePacket("PLAYERTEXT")
                replyPacket.text = f"/tell {packet.name} My posision is {client.pos}"
                client.send(replyPacket)
                
            elif packet.text.lower() == "nexus":
                client.nexus()
                
            elif packet.text.lower()[:3] == "con":
                server = packet.text.replace('con', '')
                client.changeServer(server)
                
            elif packet.text.lower().startswith("server"):
                client.changeServer(packet.text.split()[1])
                
            elif packet.text.lower() == "enter vault":
                replyPacket = CreatePacket("PLAYERTEXT")
                shouldEnter = True
                replyPacket.text = f"/tell {packet.name} Entering vault..."
                client.send(replyPacket)

#There can be multiple plugins in one file, be aware that all plugins
#will be used on all clients
@plugin(active=False)
class PortalPlugin:
    def __init__(self):
        self.vaultPortal = None

    @hook("ping")
    def onPing(self, client, packet):
        global shouldEnter
        if shouldEnter and not self.vaultPortal is None:
            shouldEnter = False
            self.enterVault(client)
    
    #To hook a packet use the hook decorator with the packet type you wish to hook
    @hook("update")
    def onUpdate(self, client, packet):
        for e in packet.newObjs:
            if e.objectType == 1824:
                self.vaultPortal = e

    def enterVault(self, client):
        if client.pos.dist(self.vaultPortal.status.pos) < 0.5:
            usePortal = CreatePacket("USEPORTAL")
            usePortal.objectId = self.vaultPortal.status.objectId
            client.send(usePortal)
        else:
            client.nextPos = [self.vaultPortal.status.pos]
            time.sleep(0.5)
            self.enterVault(client)

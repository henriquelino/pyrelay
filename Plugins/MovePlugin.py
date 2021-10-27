
import time
import json
from Networking.PacketHelper import CreatePacket
from PluginManager import hook, plugin
from Data.WorldPosData import *

shouldEnter = False



        
@plugin(active=True)
class MovePlugin:
    def __init__(self):
        with open('owner.json', 'r') as f:
            infos = json.load(f)
        self.owner = infos['owner']
        self.password = infos['password']
        
        self.owner_id = None
        self.owner_pos = None
        self.following = False
                    
    @hook("NEWTICK")
    def onNewTick_follow_updater(self, client, packet):
        if self.owner_id:
            for stat in packet.statuses: # list of ObjectStatusData
                if stat.objectId == self.owner_id:
                    self.owner_pos = stat.pos
    
    @hook("update")
    def onUpdate(self, client, packet):
        for e in packet.newObjs:
            obj_type = e.objectType #type = ObjectData
            obj_status = e.status #type = ObjectStatusData -> StatData
            
            obj_stats = obj_status.stats
            obj_id = obj_status.objectId
            obj_pos = obj_status.pos #type = WorldPosData
            
            for stats in obj_stats:
                if stats.statType == 31:
                    # print(stats.strStatValue) # print name of connected players
                    if stats.strStatValue == self.owner:
                        self.owner_id = obj_id          
    
    @hook("text")
    def onText(self, client, packet):
        # print(f"'{packet.name}: {packet.text}' | Recipient: '{packet.recipient}'")
        
        if packet.name == self.owner and packet.recipient == client.playerData.name:
                  
            if packet.text.lower()[:4] == "move":
                pos = packet.text.replace('move ', '') # remove the command
                pos = pos.split(' ') # get x, y pos, separated by space
                if pos[0] == 'here':
                    client.nextPos.append(self.owner_pos)
                    return
                
                packet_created = WorldPosData()
                # packet_created.x = random.randint(90,110)
                # packet_created.y = random.randint(155,175)
                
                packet_created.x = float(pos[0])
                packet_created.y = float(pos[1])
                
                client.nextPos.append(packet_created)
            
            if packet.text.lower() == "follow":
                self.following = True
                packet_created = CreatePacket("PLAYERTEXT")
                packet_created.text = f"/tell {packet.name} Now I'm following you :D"
                client.send(packet_created)
                self.follow(client)
                
            if packet.text.lower() == "stop follow":
                self.following = False
                packet_created = CreatePacket("PLAYERTEXT")
                packet_created.text = f"/tell {packet.name} I'll stop following you :D"
                client.send(packet_created)
                
            if packet.text.lower() == "pos":
                packet_created = CreatePacket("PLAYERTEXT")
                packet_created.text = f"/tell {packet.name} I'm @ {client.pos}"
                client.send(packet_created)
                
            if packet.text.lower() == "server":
                packet_created = CreatePacket("PLAYERTEXT")
                packet_created.text = f"/tell {packet.name} I'm on server: '{client.server}'"
                client.send(packet_created)
                
            if packet.text.lower() == "nexus":
                packet_created = CreatePacket("ESCAPE")
                client.send(packet_created)
                
            if packet.text.lower() == "tutorial":
                packet_created = CreatePacket("PLAYERTEXT")
                packet_created.text = f"/tutorial"
                client.send(packet_created)
                
        return

    def follow(self, client):
        while True:
            if not self.following:
                return
            else:
                client.nextPos.append(self.owner_pos)
                time.sleep(0.5)
                
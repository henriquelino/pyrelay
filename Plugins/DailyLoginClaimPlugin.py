
from Networking.PacketHelper import CreatePacket
from PluginManager import hook, plugin
from Data.WorldPosData import *
from Data.SlotObjectData import *
import json, time

#All plugins should have a plugin decorater
@plugin(active=True)
class DailyLoginClaimPlugin:
    def __init__(self):
        with open('owner.json', 'r') as f:
            infos = json.load(f)
        
        self.owner = infos['owner']
        self.password = infos['password']
        self.daily_quest_room_portal = False
        self.should_enter_daily_quest_portal=False
    
    @hook("MAPINFO")
    def onMapInfo(self,client,packet):
        
        if packet.name == "Daily Quest Room":
            time.sleep(.5)
            replyPacket = CreatePacket("PLAYERTEXT")
            replyPacket.text = f"/tell {self.owner} I'm @ DQR"
            client.send(replyPacket)
        
    @hook("update")
    def onUpdate(self, client, packet):
        for e in packet.newObjs:
            obj_type = e.objectType #type = ObjectData
            obj_status = e.status #type = ObjectStatusData -> StatData
            
            obj_stats = obj_status.stats
            obj_id = obj_status.objectId
            obj_pos = obj_status.pos #type = WorldPosData
            
            for stat in obj_stats:
                if not stat.strStatValue:
                    continue
                if stat.strStatValue == "Daily Quest Room":
                    self.daily_quest_room_portal = e

    @hook("ping")
    def onPing(self, client, packet):
        if self.should_enter_daily_quest_portal and self.daily_quest_room_portal is not False:
            self.should_enter_daily_quest_portal = False
            self.enterDailyQuestRoom(client)

    def enterDailyQuestRoom(self, client):
        print('entering Daily Quest Room')
        # if the distance from the portal is less than 0.5, use it
        if client.pos.dist(self.daily_quest_room_portal.status.pos) < 0.5:
            usePortal = CreatePacket("USEPORTAL")
            usePortal.objectId = self.daily_quest_room_portal.status.objectId
            client.send(usePortal)
        else: # if the distance is bigger than 0.5, move player to portal pos
            client.nextPos.append(self.daily_quest_room_portal.status.pos)
            # check again if it can enter
            while client.pos.dist(self.daily_quest_room_portal.status.pos) > 0.5:
                # wait for player to get closer to vault before trying to enter again
                time.sleep(0.1)
            self.enterDailyQuestRoom(client)
                        
    @hook("text")
    def onText(self, client, packet):
        if packet.text.lower() == f"admin {self.password}":
            self.owner = packet.name
            packet_created = CreatePacket("PLAYERTEXT")
            packet_created.text = f"/tell {packet.name} admin ok :)"
            client.send(packet_created)
            return
        
        if packet.name == self.owner and packet.recipient == client.playerData.name:
            
            if packet.text.lower() == "enter login portal":
                
                client.nextPos.append(WorldPosData(107,161))
                client.nextPos.append(WorldPosData(107,155))
                client.nextPos.append(WorldPosData(113,145))
                self.should_enter_daily_quest_portal = True
                
            if packet.text.lower() == "claim":
                replyPacket = CreatePacket("PLAYERTEXT")
                replyPacket.text = f"/tell {packet.name} claiming..."
                client.send(replyPacket)
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgIC4t7C58wsM
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgIC4j_rq0woM
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgIC4t_rI6wkM
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgIC4z6TriQkM
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgIC434D94QgM
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgIC438DQvggM
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgID4gN239AsM
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgID4oOfDqAsM
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgID40Lyh3QkM
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgID48Ljp-ggM
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgID40Ou_xwsM
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgID48KDMwwoM
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgID48PH9uAgM
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgID4mOynzgsM
                # key to claim: ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgID4mLzJ0AoM
                claim_login = CreatePacket("CLAIMLOGINREWARDMSG")
                claim_login.claimKey = "ahVzfnJlYWxtb2Z0aGVtYWRnb2RocmRyLwsSB0FjY291bnQYgICQrpG-uAgMCxIORGFpbHlMb2dpbkRhdGEYgIC4t7C58wsM"
                claim_login.claimType = ""
                print('sending claim')
                client.send(claim_login)
                print('sent')
                
                replyPacket = CreatePacket("PLAYERTEXT")
                replyPacket.text = f"/tell {packet.name} done"
                client.send(replyPacket)
                
        

import time
import json
from Networking.PacketHelper import CreatePacket
from PluginManager import hook, plugin
from Data.WorldPosData import *

shouldEnter = False



@plugin(active=False)
class DiscoveryPackets:
    @hook("ENEMYSHOOT")
    def onEnemyShoot(self, client, packet):
        print("ENEMYSHOOT")
        print(packet.bulletId)
        print(packet.ownerId)
        print(packet.bulletType)
        print(packet.startingPos)
        print(packet.angle)
        print(packet.damage)
        print(packet.numShots)
        print(packet.angleInc)
        
    @hook("DAMAGE")
    def onDamage(self, client, packet):
        print("onDamage")
        print(packet.targetId)
        print(packet.effects)
        print(packet.damageAmount)
        print(packet.armorPierce)
        print(packet.bulletId)
        print(packet.objectId)
        
    @hook("CLAIMDAILYREWARDRESPONSE")
    def onClaimDailyReward(self, client, packet):
        print("onTradeStart")
        print(packet.itemId)
        print(packet.quantity)
        print(packet.gold)
    
    
    @hook("ALLYSHOOT")
    def onAllyShoot(self, client, packet):
        print("onAllyShoot")
        print(packet.bulletId)
        print(packet.ownerId)
        print(packet.containerType)
        print(packet.angle)
        print(packet.bard)
        
    # @hook("SERVERPLAYERSHOOT")
    # def onServerPlayerShoot(self, client, packet):
    #     print("onServerPlayerShoot")
    #     print(packet.bulletId)
    #     print(packet.ownerId)
    #     print(packet.containerType)
    #     print(packet.startingPos)
    #     print(packet.angle)
    #     print(packet.damage)

    @hook("NEWTICK")
    def onTick(self, client, packet):
        for obj in packet.statuses:
            if len(obj.stats) == 0:
                continue
            for i in obj.stats:
                obj_pos = obj.pos
                obj_name = i.strStatValue
                obj_value = i.statValue
                if not obj_name:
                    continue
                print(f"{obj_name: <25} @ {round(obj_pos.x,2): <6}x {round(obj_pos.y,2): <6}y - Value = {obj_value}")
                # print(type(i))
                # print(dir(i))
                break
    
    @hook("update")
    def onUpdate(self, client, packet):
        # print( '\n'*1, '-'*60)
        # print("onUpdate")
        # # print("tiles",packet.tiles)
        # print("objs")
        
        # print all new objects name and coordinates
        for e in packet.newObjs:
            obj_name = e.status.stats[2].strStatValue
            if not obj_name:
                continue
            obj_pos = e.status.pos
            obj_type = e.objectType
            print(f"{obj_name: <25} @ {obj_pos.x: >6}x {obj_pos.y: >6}y     type={obj_type}")
            # if e.objectType == 1824:
            #     print(e.status.stats[2].strStatValue)
            # print('objectType:', e.objectType)
            # print('objectId:', e.status.objectId)
            # print('pos:', e.status.pos)
        # print("drops",packet.drops)
        # print('-'*60, '\n\n')
                
    @hook("PLAYERSHOOT")
    def onPlayerShoot(self, client, packet):
        print("onPlayerShoot")
        print(packet.time)
        print(packet.bulletId)
        print(packet.containerType)
        print(packet.pos)
        print(packet.angle)
        print(packet.speedMult)
        print(packet.lifeMult)
        print(packet.isBurst)
        
        
@plugin(active=False)
class DiscoveryOut:
    def __init__(self):
        with open('owner.json', 'r') as f:
            infos = json.load(f)
        
        self.owner = infos['owner']
        self.password = infos['password']
        self.stop_shoot = None
        
    @hook("text")
    def onText(self, client, packet):
        # print(f"'{packet.name}: {packet.text}' | Recipient: '{packet.recipient}'")
        
        if packet.name == self.owner and packet.recipient == client.playerData.name:
                            
            if "move" in packet.text.lower():
                pos = packet.text.replace('move ', '') # remove the command
                pos = pos.split(' ') # get x, y pos, separated by space
                
                packet_created = WorldPosData()
                # packet_created.x = random.randint(90,110)
                # packet_created.y = random.randint(155,175)
                
                packet_created.x = float(pos[0])
                packet_created.y = float(pos[1])
                
                client.nextPos.append(packet_created)
            
            if packet.text.lower() == "center":
                packet_created = WorldPosData()
                packet_created.x = 107
                packet_created.y = 165
                client.nextPos=[packet_created]
                
            if packet.text.lower() == "go to portals":
                packet_created = WorldPosData()
                packet_created.x = 107
                packet_created.y = 133
                client.nextPos=[packet_created]
                
            if packet.text.lower() == "pos":
                packet_created = CreatePacket("PLAYERTEXT")
                packet_created.text = f"/tell {packet.name} {client.pos}"
                client.send(packet_created)
                
            if packet.text.lower() == "server":
                packet_created = CreatePacket("PLAYERTEXT")
                packet_created.text = f"/tell {packet.name} {client.server}"
                client.send(packet_created)
                
            if packet.text.lower() == "nexus":
                packet_created = CreatePacket("ESCAPE")
                client.send(packet_created)
                
            if packet.text.lower() == "tutorial":
                packet_created = CreatePacket("PLAYERTEXT")
                packet_created.text = f"/tutorial"
                client.send(packet_created)
                
        return

#There can be multiple plugins in one file, be aware that all plugins
#will be used on all clients
@plugin(active=False)
class PortalPlugin:
    def __init__(self):
        self.vaultPortal = None

    @hook("ping")
    def onPing(self, client, packet):
        global shouldEnter
        if shouldEnter and self.vaultPortal is not None:
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
            client.nextPos.append(self.vaultPortal.status.pos)
            time.sleep(0.5)
            self.enterVault(client)

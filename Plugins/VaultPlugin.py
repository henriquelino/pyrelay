
from Networking.PacketHelper import CreatePacket
from PluginManager import hook, plugin
from Data.WorldPosData import *
from Data.SlotObjectData import *
import json, time

#All plugins should have a plugin decorater
@plugin(active=True)
class VaultPlugin:
    def __init__(self):
        with open('owner.json', 'r') as f:
            infos = json.load(f)
        
        self.owner = infos['owner']
        self.password = infos['password']
        self.aviso_que_loguei = None
        self.dropped_bags = list()
        
        self.vault_portal_id = 1824 
        self.vault_portal = None
        self.should_enter_vault = False
        
        self.vault_chest_object_id=None
        self.vault_chest_content=None
        self.vault_chest_pos = None 
        
        self.gift_chest_object_id = None
        self.gift_chest_content = None
        self.gift_chest_pos = None
        
        self.potion_chest_object_id = None
        self.potion_chest_content = None
        self.potion_chest_pos = None

    @hook("text")
    def onText(self, client, packet):
        print(f"'{packet.name}: {packet.text}' | Recipient: '{packet.recipient}'")
        if packet.text.lower() == f"admin {self.password}":
            self.owner = packet.name
            packet_created = CreatePacket("PLAYERTEXT")
            packet_created.text = f"/tell {packet.name} admin ok :)"
            client.send(packet_created)
            return
        
        if packet.name == self.owner and packet.recipient == client.playerData.name:
            if packet.text.lower() == "enter vault":
                self.should_enter_vault = True
                replyPacket = CreatePacket("PLAYERTEXT")
                replyPacket.text = f"/tell {packet.name} Entering vault..."
                client.send(replyPacket)
                
            if packet.text.lower() == "deposit chest":
                print("starting deposit")
                client.nextPos.append(self.vault_chest_pos)
                
                # wait client get closer to bag if its not
                while client.pos.dist(self.vault_chest_pos) > .2:
                    time.sleep(.05)
                    
                items_in_player_inv = 0
                # ignore first 4 slots (equips)
                for item in client.playerData.inv[4:]:
                    if item != -1:
                        items_in_player_inv += 1
                
                free_slots_in_chest = 0
                for item in self.vault_chest_content:
                    if item == -1:
                        free_slots_in_chest += 1
                
                if items_in_player_inv > free_slots_in_chest:
                    # if player has more itens than chest has slots
                    # then we will deposit the max that chest can hold
                    count_items_to_deposit = free_slots_in_chest
                elif free_slots_in_chest >= items_in_player_inv:
                    # we can deposit all player inv
                    count_items_to_deposit = items_in_player_inv
                else:
                    print(items_in_player_inv, free_slots_in_chest)
                index_to_deposit = 0
                next_chest_free_slot = 0
                # list to append used free slots
                used_slots = list()
                # ---------------------------------------------------------------------
                for _ in range(count_items_to_deposit):
                    while client.playerData.inv[4:][index_to_deposit] == -1:
                        index_to_deposit += 1

                    # iter over chest contents searching empty slots
                    # when find one, use if its not used before
                    for index in range(len(self.vault_chest_content)):
                        if self.vault_chest_content[index] == -1:
                            if index in used_slots:
                                continue
                            next_chest_free_slot = index
                            used_slots.append(index)
                            break
                    
                    # create slot object for bag
                    vault_slot = SlotObjectData();
                    vault_slot.objectId = self.vault_chest_object_id
                    vault_slot.slotId = next_chest_free_slot # index of chest slot that contains -1 (nothing)
                    vault_slot.objectType = -1 # item of said slot (in this case -1 that is nothing)
                    
                    # create slot object for player
                    player_slot = SlotObjectData();
                    player_slot.objectId = client.objectId #object is the player itself
                    player_slot.slotId = index_to_deposit+4 # ignore the first 4 (equips)
                    player_slot.objectType = client.playerData.inv[index_to_deposit+4]
                                        
                    # create inv swap packet
                    inv_swap = CreatePacket("INVSWAP")
                    inv_swap.time = client.getTime() # time that happens
                    inv_swap.pos = self.vault_chest_pos # where the swap occurs
                
                    inv_swap.slotObject1 = player_slot #from
                    inv_swap.slotObject2 = vault_slot #to
                    
                    # wait client get closer to bag if its not
                    client.send(inv_swap)
                    
                    index_to_deposit+=1
                    time.sleep(.5)
                    
                print("done deposit")
                
            if packet.text.lower() == "bag swap":
                print("starting swap")
                
                for bag in self.dropped_bags:
                                        
                    # go to bag
                    client.nextPos.append(bag['pos'])
                    
                    # wait client get closer to bag if its not
                    while client.pos.dist(bag['pos']) > .2:
                        time.sleep(.05)
                    
                    for item_index in range(len(bag['contents'])):
                        if bag['contents'][item_index] == -1:
                            continue
                        
                        time.sleep(0.6) # delay between multiple items in same bag
                        
                        # create slot object for bag
                        bag_slot = SlotObjectData();
                        bag_slot.objectId = bag['id']
                        bag_slot.slotId = item_index # index of chest slot that contains -1 (nothing)
                        bag_slot.objectType = bag['contents'][item_index] # item of said slot (in this case -1 that is nothing)
                        
                        # create slot object for player
                        player_slot = SlotObjectData();
                        player_slot.objectId = client.objectId #objeto is the player itself
                        player_slot.slotId = client.playerData.inv[4:].index(-1) # ignore the first 4 (equips)
                        player_slot.objectType = -1 # empty
                        
                        # create inv swap packet
                        inv_swap = CreatePacket("INVSWAP")
                        inv_swap.time = client.getTime() # time that happens
                        inv_swap.pos = bag['pos'] # player position
                    
                        inv_swap.slotObject1 = bag_slot #from
                        inv_swap.slotObject2 = player_slot #to
                        
                        client.send(inv_swap)
                        print('-'*60)
                
                # reset dropped bags
                self.dropped_bags = list()
                print("end swap")
            
            if packet.text.lower() == "drop":
                
                inv_slot=4
                
                slotObject = SlotObjectData();
                
                # The object id of the entity which owns the slot.
                # slotObject.objectId = client.objectId # ? is this one?
                slotObject.objectId = client.charData.currentCharId # ? or this one?
                # or neither?
                
                # The index of the slot. E.g. The 4th inventory slot has the slot id 3.
                slotObject.slotId = inv_slot
                
                # The item id of the item in the slot, or -1 if it is empty. Needs to be an INT
                slotObject.objectType = client.playerData.inv[inv_slot]
                print(slotObject)
                inv_drop = CreatePacket("INVDROP")
                inv_drop.slotObject = slotObject
                client.send(inv_drop)

    @hook("VAULTINFO")
    def onVaultInfo(self, client, packet):
        print('vault info updated')
        # objs IDs
        self.vault_chest_object_id = packet.chestObjectId
        self.gift_chest_object_id = packet.giftObjectId
        self.potion_chest_object_id = packet.potionObjectId
        # contents
        self.vault_chest_content = packet.vaultContent
        self.gift_chest_content = packet.giftContent
        self.potion_chest_content = packet.potionContent
        return # not print the infos
        print('-'*30, 'vault infos', '-'*30)
        print(f"info1 | type=({type(packet.info1)} - {packet.info1}")
        
        print(f"chestObjectId | type=({type(packet.chestObjectId)} - {packet.chestObjectId}")
        print(f"giftObjectId | type=({type(packet.giftObjectId)} - {packet.giftObjectId}")
        print(f"potionObjectId | type=({type(packet.potionObjectId)} - {packet.potionObjectId}")
        
        print(f"vaultContent | type=({type(packet.vaultContent)} - {packet.vaultContent}")
        print(f"giftContent | type=({type(packet.giftContent)} - {packet.giftContent}")
        print(f"potionContent | type=({type(packet.potionContent)} - {packet.potionContent}")
        
        print(f"vaultUpgrageCost | type=({type(packet.vaultUpgrageCost)} - {packet.vaultUpgrageCost}")
        print(f"potionUpgradeCose | type=({type(packet.potionUpgradeCose)} - {packet.potionUpgradeCose}")
        
        print(f"curPotionMax | type=({type(packet.curPotionMax)} - {packet.curPotionMax}")
        print(f"nextPotionMax | type=({type(packet.nextPotionMax)} - {packet.nextPotionMax}")

        print('-'*71)

    @hook("ping")
    def onPing(self, client, packet):
        if self.should_enter_vault and self.vault_portal is not False:
            self.should_enter_vault = False
            self.enterVault(client)
        
        # ping owner saying that client is ready
        if not self.aviso_que_loguei:
            self.aviso_que_loguei = True
            packet_created = CreatePacket("PLAYERTEXT")
            packet_created.text = f"/tell {self.owner} logged"
            client.send(packet_created)

    @hook("NEWTICK")
    def onNewTick_save_vault_chests_pos(self, client, packet):
        for object_status_data in packet.statuses:
            if object_status_data.objectId == self.vault_chest_object_id:
                self.vault_chest_pos = object_status_data.pos
                
            if object_status_data.objectId == self.gift_chest_object_id:
                self.gift_chest_pos = object_status_data.pos
                
            if object_status_data.objectId == self.potion_chest_object_id:
                self.potion_chest_pos = object_status_data.pos
                
            # if object_status_data.objectId == self.vault_chest_id:
            #     # print(object_status_data)
            #     pass
            # for stat_data in object_status_data.stats:
            #     # stat_data.statType
            #     # stat_data.statValue
            #     # stat_data.strStatValue
            #     # stat_data.secondaryValue
            #     pass

    @hook("NEWTICK")
    def onNewTick_bag_updater(self, client, packet):
        # goes over all status of the tick
        for i in packet.statuses: # list of ObjectStatusData
            # print('self.dropped_bags',self.dropped_bags)
            # and check every dropped bags
            for bag in self.dropped_bags:
                # if the bag id and tick object id is the same
                if i.objectId == bag['id']:
                    # then save the statstype from 8 to 15 in a list
                    for stats in i.stats:
                        #8 is the first item position in bag
                        #15 is the last item
                        if stats.statType >= 8 and stats.statType <= 15:
                            # need to create an array accordly to the bag real item places
                            # so if the item is in the first slot, this will be 
                            # statType=8;  statType-8 = 0, that is the first slot in the bag
                            # capiche?
                            bag['contents'][stats.statType-8] = stats.statValue

    @hook("update")
    def onUpdate(self, client, packet):
        for e in packet.newObjs:
            obj_type = e.objectType #type = ObjectData
            obj_status = e.status #type = ObjectStatusData -> StatData
            
            obj_stats = obj_status.stats
            obj_id = obj_status.objectId
            obj_pos = obj_status.pos #type = WorldPosData
            
            # get bags ids + pos
            if obj_type == 1280 or obj_type == 1283 or (obj_type >= 1286 and obj_type <= 1296):
                # if any bag drops
                # 1280 -> brown bag
                # 1283 -> ?? idk
                # 1286 >> ?? idk
                # 1296 << ?? idk
                bag = {
                    'id' :  obj_id,  # save the bag object ID
                    'pos' : obj_pos, # save bag position
                    'contents' : [-1]*8, # create a list with 8 items -1
                }
                # append to the drop bags list
                self.dropped_bags.append(bag)
            
            # get vault portal id
            if obj_type == self.vault_portal_id:
                self.vault_portal = e
            
            # get owner obj id
            for stats in obj_stats:
                if stats.statType == 31:
                    if stats.strStatValue == self.owner:
                        self.owner_id = obj_id
                        break

    def enterVault(self, client):
        print('entering vault')
        # if the distance from the portal is less than 0.5, use it
        if client.pos.dist(self.vault_portal.status.pos) < 0.5:
            usePortal = CreatePacket("USEPORTAL")
            usePortal.objectId = self.vault_portal.status.objectId
            client.send(usePortal)
        else: # if the distance is bigger than 0.5, move player to portal pos
            client.nextPos.append(self.vault_portal.status.pos)
            # check again if it can enter
            while client.pos.dist(self.vault_portal.status.pos) > 0.5:
                # wait for player to get closer to vault before trying to enter again
                time.sleep(0.1)
            self.enterVault(client)
    
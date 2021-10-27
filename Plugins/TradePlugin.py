from Networking.PacketHelper import CreatePacket
from PluginManager import hook, plugin
from Data.WorldPosData import *
import json

#All plugins should have a plugin decorater
@plugin(active=True)
class TradePlugin:
    def __init__(self):
        with open('owner.json', 'r') as f:
            infos = json.load(f)
            
        self.owner = infos['owner']
        self.password = infos['password']
        
        
        # list of bools of each inv slot
        self.partner_changed_offer = list()
        self.client_offer = list()
        
        # not really used
        self.trade_client_items = list()
        self.trade_partner_items = list()
        
    # -------------------- OUTGOING PACKETS --------------------
    # when someone request a trade to you
    @hook("TRADEREQUESTED")
    def onTradeRequested(self, client, packet):
        print(f"Trade requested by '{packet.name}'")
        # if the requester is the owner
        if packet.name == self.owner:
            print('Accepting trade')
            # create an accept packet and send to client
            trade_request = CreatePacket("REQUESTTRADE")
            trade_request.name = packet.name
            client.send(trade_request)
            
    # occurs when the trade start, the menu shows up and you can select items
    @hook("TRADESTART")
    def onTradeStart(self, client, packet):
        self.trade_client_items = packet.clientItems
        self.trade_partner_items = packet.partnerItems
        
        # change the size of the partner offer to the size of their inventory (default to no item selected)
        self.partner_changed_offer = [False]*len(packet.partnerItems)
        
        # change the size of the clients array to the size of our inventory (default to no item selected)
        self.client_offer = [False]*len(self.trade_client_items)
        
    
    # occurs when a item get selected or deselected on trade menu
    @hook("TRADECHANGED")
    def onTradeChanged(self, client, packet):
        # this returns an array [False]*len(player_inventory)
        # the item selected will be True, the position will be accordly to the inv pos
        # ex: 2nd inv slot will give:
        # [False, True, False, False...]
        self.partner_changed_offer = packet.offer
    
    # -------------------- INCOMING PACKETS --------------------
    @hook("text")
    def onText(self, client, packet):
        # if receive a text with admin <pass> then change owner name
        if packet.text.lower() == f"admin {self.password}" and packet.recipient == client.playerData.name:
            self.owner = packet.name
            packet_created = CreatePacket("PLAYERTEXT")
            packet_created.text = f"/tell {packet.name} admin ok :)"
            client.send(packet_created)
            return
        
        # answer only if the owner is talking to
        if packet.name == self.owner and packet.recipient == client.playerData.name:
            # accept trade will conclude the trade
            #/tell <bot_name> accept trade
            if packet.text.lower() == "accept trade":
                print('Accepting trade')
                trade_acept = CreatePacket("ACCEPTTRADE")
                # partner/client offer = list of bools with the size equals the player inv (backpack=20, no backpack=12 (the 4 first items are equips, ignore them))
                trade_acept.partnerOffer=self.partner_changed_offer
                trade_acept.clientOffer=self.client_offer
                client.send(trade_acept)
                            
            #/tell <bot_name> start trade
            # will make the bot request trade to you
            if packet.text.lower() == "trade":
                print(f"Requesting trade to {self.owner}")
                packet_created = CreatePacket("REQUESTTRADE")
                packet_created.name = self.owner
                client.send(packet_created)
                print("Trade requested")
                        
            # select a item
            #/tell <bot_name> give 0 1 2 3
            # will select the first 4 items in bot inventory
            if packet.text.lower()[:4] == "give":
                items = packet.text.replace('give ', '') # remove the command
                items = items.split(' ') # get a list of items split by space ' '
                if items[0] == 'all':
                    items = list(range(16))
                # iterate over items and change the status
                for item in items:
                    item=int(item)+4 # 4 first are equips, ignore them
                    
                    # change each item position in inventory to True
                    self.client_offer[item] = True
                
                # send a packet to update the selected items
                change_offer = CreatePacket("CHANGETRADE")
                change_offer.offer = self.client_offer
                client.send(change_offer)
            
            # deselect a item
            #/tell <bot_name> give 0 1 2 3
            # will deselect the first 4 items in bot inventory
            if packet.text.lower()[:6] == "cancel":
                items = packet.text.replace('cancel ', '') # remove the command
                items = items.split(' ') # get a list of items split by space ' '
                
                # iterate over items and change the status
                for item in items:
                    item=int(item)+4 # 4 first are equips, ignore them
                    
                    # change each item position in inventory to False
                    self.client_offer[item] = False 
                    
                # send a packet to update the selected items
                change_offer = CreatePacket("CHANGETRADE")
                change_offer.offer = self.client_offer
                client.send(change_offer)
        return
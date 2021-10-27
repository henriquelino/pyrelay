import json

class OwnerPlugin():
    def __init__(self):
        with open('owner.json', 'r') as f:
            infos = json.load(f)
        
        self.owner = infos['owner']
        self.password = infos['password']

import imports

class pokemon :
    def __init__(self, name, hitpoints, attack, defense, speed, level, movechoice): #add IVs, EVs, Types
        self.name = name
        self.level = level
        self.hp = round(2*hitpoints*level/100) + level + 10
        self.atk = round((attack*2*level)+5) #*nature)
        self.df = round(defense*2*level)+5
        self.spd = round(speed*2*level)+5
        self.moveset = movechoice

import imports
import random

def damagecalc(level,atk,defense, movepower) -> "damage":
    damage =round(((((2*level +2)*movepower*atk/defense )/50)+2)*(random.randrange(85,100)/100))
    return damage

def choosemove(pokemon):    
    print(list(pokemon.moveset))
    choice = input()
    if choice not in pokemon.moveset:
        while choice not in pokemon.moveset:
            print("choose a valid move")
            choice = input()
    return choice


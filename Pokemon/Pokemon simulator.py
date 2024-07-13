'''
def kinetic_energy(m:'in KG', v:'in M/S')->'Joules': 
    return 1/2*m*v**2
 
print(kinetic_energy.__annotations__)
print(kinetic_energy(5,10),
      kinetic_energy.__annotations__['return'])
'''

import imports







charmander = imports.classes.pokemon("Charmander", 39,52,43,65,5, imports.moveset.charmandermoveset)



squirtle = imports.classes.pokemon("Squirtle", 44,48,65,43,5, imports.moveset.squirtlemoveset)
print(squirtle.hp)
def battle(poke1,poke2):
    while poke1.hp >0 and poke2.hp > 0:
        if poke1.spd > poke2.spd:
            move = imports.functions.choosemove(poke1)
            poke2.hp -= imports.functions.damagecalc(poke1.level,poke1.atk,poke2.df, poke1.moveset[move]["power"])
            if poke2.hp < 0:
                break
            move = imports.functions.choosemove(poke2)
            poke1.hp -= imports.functions.damagecalc(poke2.level,poke2.atk,poke1.df, poke2.moveset[move]["power"])
        elif poke1.spd < poke2.spd:
            poke1.hp -= imports.functions.damagecalc(poke2.level,poke2.atk,poke1.df, poke2.moveset[move]["power"])
            if poke1.hp < 0:
                break
            poke2.hp -= imports.functions.damagecalc(poke1.level,poke1.atk,poke2.df, poke1.moveset[move]["power"])
        print(poke1.name + ": " + str(poke1.hp))
        print(poke2.name + ": " + str(poke2.hp))
    if poke1.hp < 0:
        print(poke1.name + " fainted! " + poke2.name + " is the winner!")
    else:
        print(poke2.name + " fainted! " + poke1.name + " is the winner!")


battle(charmander, squirtle)
            


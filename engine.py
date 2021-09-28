from bf import *
import random
from os import system, name
atomic_chars = "<>+-.,"

winrows = [[0,3,6],[1,4,7],[2,5,8],[0,1,2],[3,4,5],[6,7,8],[0,4,8],[2,4,6]]

cached = {}
already_gen = {}
MAX_INSTR = 128
POP_SIZE = 2000

def win(boardstate):
    for v in winrows:
        if(boardstate[v[0]] == 1 and boardstate[v[1]] == 1 and boardstate[v[2]] == 1):
            return True

def mutate(parent):
    child = list(parent)
    mut_type = random.randint(0,10)

    # insert sometimes.
    # average of 3 letters = .3 chance to get
    if(mut_type < 3):
        for i in range(random.randint(1,5)):
            char = random.choice(atomic_chars)
            child.insert(random.randint(0,len(child)),char)

    # .6 chance to drop
    if(mut_type >= 3 and mut_type <= 9):

        to_del_idx = random.randint(0,len(child)-1)
        value_to_del = child[to_del_idx]

        if(value_to_del == "["):
            right = child[to_del_idx:].index("]")
            del child[to_del_idx + right]
            del child[to_del_idx]

        elif (value_to_del == "]"):
            rlist = child[:to_del_idx]
            rlist.reverse()
            left = (to_del_idx - 1) - (rlist.index("["))
            del child[to_del_idx]
            del child[left]
        else:
            del child[to_del_idx]
        
        pass

    #loop - used sparingly
    if(mut_type == 10):
        #insert loop. Generate a start position
        start = random.randint(0,len(child))
        end = random.randint(start+1,len(child)+1)

        child.insert(start,"[")
        child.insert(end,"]")
    return ''.join(child)

# winning worth 100
WIN = 100
# losing worth 50 (hey, you didn't crash!!)
LOSE = 50
# survival worth 0 - doesn't say much about you
SURVIVE = 0
# losing because you sent shit is -10000
LOSE_OOB = -1000
# losing because you did NOTHING is -100000
LOSE_NO_INPUT = -1000
# losing because you ran out of computation time is the worst thing.
# (need to have an i-- before you can have a while{})
LOSE_LOOP = -10000 * POP_SIZE

KILL = -20000 * POP_SIZE

def run_and_apply(code, state, printstr):
    out = run(",>,>,>,>,>,>,>,>,>"+code,state,MAX_INSTR)
    if(printstr):
        print(out[1])
    if(len(out[0]) == 0):
        return LOSE_NO_INPUT
    if(out[0][0] > 8):
        return LOSE_OOB
    if(out[0][0] == -1):
        return LOSE_LOOP
    if(state[out[0][0]] != 0):
        return LOSE_OOB
    state[out[0][0]] = 1
    return 0

def flip(game):
    out = []
    for v in game:
        if(v == 1):
            out.append(2)
        elif(v == 2):
            out.append(1)
        else:
            out.append(v)
    return out


def play_game(i, adv, game,useinstr):
    while(True):
        # our turn
        move = run_and_apply(i,game,useinstr)
        if(move == 0):
            # we made a valid move and won
            if(win(game)):
                return [WIN, game]
        else:
            return [move,game]
        # their turn
        game = flip(game)
        move = run_and_apply(adv,game,useinstr)
        if(move == 0):
            # they made a valid move and won
            if(win(game)):
                return [LOSE, game]
        else:
            # they crashed
            return [SURVIVE,game]
        game = flip(game)


#it can mutate into something neat.
def get_relative_fitness(i,pop):
    # having extra shit down the line is possibly good?
    # however, prioritizing shorter programs wastes FAR less time.
    # up to you about len(i)
    # IDEA - period of experimenation and then a "squeeze?"
    games_won = 0
    for adv in pop:
        game = [0,0,0,0,0,0,0,0,0]
        if(i+"|"+adv not in cached):
            # Take points for winning, tieing, or losing, going first
            val = play_game(i,adv,game,False)[0]
            game = [0,0,0,0,0,0,0,0,0]

            # Take points for winning, tieing, or losing, going second.
            # But, the opponent goes first.
            em = run_and_apply(adv, game, False)
            if(em == 0):
                val += play_game(i,adv,game, False)[0]

            cached[i+"|"+adv] = val
        games_won += cached[i+"|"+adv]
    return games_won

def printgame(v,adv):
    game = [0,0,0,0,0,0,0,0,0]
    res = play_game(v,adv,game,True) 
    print("winner: " + (v if res[0] >= 0 else adv))
    print(res[1][0:3])
    print(res[1][3:6])
    print(res[1][6:9])


def print_scores(score):
    for v in score:
        print(str(v[0]) + " " + v[1])


pop = []

def play():
    game = [0,0,0,0,0,0,0,0,0]
    while(True):
        run_and_apply("+>,+[,<++>,]<-.",game)
        print(game[0:3])
        print(game[3:6])
        print(game[6:9])
        game[int(input())] = 2
    exit()

def filter_diverse(scores):
    # Don't let one line of algorithms dominate. Encourage diverity.
    bucket = {}
    for i in scores:
        if(i[0] not in bucket):
            bucket[i[0]] = []
        bucket[i[0]].append(i)

    scores2 = []
    for i in bucket:
        opts = sorted(bucket[i], key=lambda x: len(x[1]))
        if(opts[0][0] > KILL):
            # keep the shortest codes in the class
            for v in opts:
                if(len(v[1]) == len(opts[0][1])):
                    scores2.append(v)
    scores2 = sorted(scores2, key=lambda x: x[0])
    scores2.reverse()
    return scores2

#play()

#START
#Generate the initial population
for v in atomic_chars:
    pop.append(v)

scores = []

#Compute fitness
for v in pop:
    scores.append([get_relative_fitness(v,pop),v])

gen = 2
# only need about 15 mutations.
genitr = 15
best_gen = list(map(lambda n: n[1],scores))

bests= []

while (True):

    gen += 1

    # intermediate filter or nah?
    
    # We have mutated all the parents from each generation.
    # Lets see if any have surpassed their parents.
    if(gen % genitr == 0):

        print("c1->" + str(len(cached.values()) / (POP_SIZE * POP_SIZE * 4)))
        if(len(cached.values()) > POP_SIZE * POP_SIZE * 4):
            cached.clear()

        print("c2->" + str(len(already_gen) / 100000))
        if(len(already_gen) > 100000):
            already_gen.clear()
        
        # This is a check to make sure that any algo that gets this far and dies does NOT come back.
        pop2 = []
        for p in pop:
            if(p not in already_gen):
                pop2.append(p)
            already_gen[p] = True
        pop = pop2

        best_gen = best_gen + list(map(lambda n: n[1],scores))
        scores = []
        for v in pop:
            scores.append([get_relative_fitness(v,best_gen),v])
    
        # cut down the best algorithms into a diverse list, and set it as new best gen.
        scores = filter_diverse(scores)
        scores = scores[:POP_SIZE]
        best_gen = list(map(lambda n: n[1],scores))
        pop[:] = list(best_gen)

        bests.append(scores[0][0])

        print("GENERATION " + str(gen))
        print(str(scores[0][0]) + " VS " + str(scores[len(scores)-1][0]))
        printgame(scores[0][1],scores[1][1])
        #print_scores(scores)

        # business as usual. 
        pop = list(map(lambda n: n[1],scores))


    # allow another step of mutation if there are not many algos alive.
    if(len(pop) <= POP_SIZE):
        pop = pop + list(map(lambda n: mutate(n),pop))
    else:
        pop = list(map(lambda n: mutate(n),pop))

    # make only unique programs
    pop = set(pop)
    
    #print("prune")

    # remove the null program
    if "" in pop:
        pop.remove("")

    # remove useless []'s, which best case is NOOP and worse case is endless loop
    pop =  [x for x in pop if not "[]" in x]

    #print("score")
    scores = []



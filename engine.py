from bf import *
import random

atomic_chars = "<>+-.,"

winrows = [[0,3,6],[1,4,7],[2,5,8],[0,1,2],[3,4,5],[6,7,8],[0,4,8],[2,4,6]]

cached = {}

MAX_INSTR = 256
POP_SIZE = 50

def win(boardstate):
    for v in winrows:
        if(boardstate[v[0]] == 1 and boardstate[v[1]] == 1 and boardstate[v[2]] == 1):
            return True

def mutate(parent):
    child = list(parent)
    mut_type = random.randint(0,10)

    if(mut_type < 2):
        #insert
        child.insert(random.randint(0,len(child)),random.choice(atomic_chars))

        # delete, special care to delete both parts of a loop.
    if(mut_type >= 2 and mut_type <= 9):

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

    if(mut_type == 10):
        #insert loop. Generate a start position
        start = random.randint(0,len(child))
        end = random.randint(start+1,len(child)+1)

        child.insert(start,"[")
        child.insert(end,"]")
    return ''.join(child)

WIN = 100
LOSE = -5
SURVIVE = 0
LOSE_OOB = -50
LOSE_NO_INPUT = -100
LOSE_LOOP = -1000 * POP_SIZE

def run_and_apply(code, state):
    out = run(code,state,MAX_INSTR)
    if(len(out) == 0):
        return LOSE_NO_INPUT
    if(out[0] > 8):
        return LOSE_OOB
    if(out[0] == -1):
        return LOSE_LOOP
    if(state[out[0]] != 0):
        return LOSE_OOB
    state[out[0]] = 1
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


def play_game(i, adv, game):
    while(True):
        # our turn
        move = run_and_apply(i,game)
        if(move == 0):
            # we made a valid move and won
            if(win(game)):
                return [WIN, game]
        else:
            return [move,game]
        # their turn
        game = flip(game)
        move = run_and_apply(adv,game)
        if(move == 0):
            # they made a valid move and won
            if(win(game)):
                return [LOSE, game]
        else:
            # they crashed
            return [SURVIVE,game]
        game = flip(game)

def get_relative_fitness(i,pop):
    games_won = -len(i)
    for adv in pop:
        game = [0,0,0,0,0,0,0,0,0]
        if(i+"|"+adv not in cached):
            # Take points for winning, tieing, or losing, going first
            val = play_game(i,adv,game)[0]
            game = [0,0,0,0,0,0,0,0,0]

            # Take points for winning, tieing, or losing, going second.
            # But, the opponent goes first.
            em = run_and_apply(adv, game)
            if(em == 0):
                val += play_game(i,adv,game)[0]

            cached[i+"|"+adv] = val
        games_won += cached[i+"|"+adv]
    return games_won

def printgame(v,adv):
    game = [0,0,0,0,0,0,0,0,0]
    res = play_game(v,adv,game) 
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
        run_and_apply(">,[<<+>,]<<.,->-[,]",game)
        print(game[0:3])
        print(game[3:6])
        print(game[6:9])
        game[int(input())] = 2
    exit()


#START
#Generate the initial population
for v in atomic_chars:
    pop.append(v)

scores = []


#Compute fitness
for v in pop:
    scores.append([get_relative_fitness(v,pop),v])

printitr = 10
gen = 0

while (True):
    #print("select")
    #Selection
    scores = sorted(scores, key=lambda x: x[0])
    scores.reverse()
    scores = scores[:POP_SIZE]

    # Don't let one line of algorithms dominate. Encourage diveristy.
    bucket = {}
    for i in scores:
        if(i[0] not in bucket):
            bucket[i[0]] = []
        bucket[i[0]].append(i)

    scores2 = []
    while(len(scores2) < POP_SIZE and len(scores2) != len(scores)):
        for i in bucket:
            if(len(bucket[i]) > 0):
                scores2.append(bucket[i].pop())

    scores = scores2

    printitr -= 1
    gen += 1
    if(printitr == 0):
        print("GENERATION " + str(gen))
        print(scores[0][1] + " VS " + scores[1][1])
        printitr = 10
        printgame(scores[0][1],scores[1][1])
    #print_scores(scores)

    pop = list(map(lambda n: n[1],scores))

    #Crossover
    pop = pop + list(map(lambda n: mutate(n),pop))

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
    #Compute fitness
    for v in pop:
        scores.append([get_relative_fitness(v,pop),v])


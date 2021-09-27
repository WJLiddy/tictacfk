from bf import *
import random



atomic_chars = "<>+-.,"

winrows = [[0,3,6],[1,4,7],[2,5,8],[0,1,2],[3,4,5],[6,7,8],[0,4,8],[2,4,6]]

MAX_INSTR = 1000
POP_SIZE = 100

def win(boardstate):
    for v in winrows:
        if(boardstate[v[0]] == 1 and boardstate[v[1]] == 1 and boardstate[v[2]] == 1):
            return 1
        if(boardstate[v[0]] == 1 and boardstate[v[1]] == 1 and boardstate[v[2]] == 1):
            return -1
    return 0

def mutate(parent):
    child = list(parent)
    mut_type = random.randint(0,2)
    if(mut_type == 0):
        #insert
        child.insert(random.randint(0,len(child)),random.choice(atomic_chars))

        # delete, special care to delete both parts of a loop.
    if(mut_type == 1):

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

    if(mut_type == 2):
        #insert loop. Generate a start position
        start = random.randint(0,len(child))
        end = random.randint(start+1,len(child)+1)

        child.insert(start,"[")
        child.insert(end,"]")
    return ''.join(child)


def run_and_apply(code, state):
    out = run(code,state,MAX_INSTR)
    if(len(out) == 0):
        return False
    if(out[0] > 8):
        return False
    if(out[0] == -1):
        return False

    if(state[out[0]] != 0):
        return False
    state[out[0]] = 1
    return True

def flip(game):
    out = []
    for v in game:
        if(v == 1):
            out.append(2)
        if(v == 2):
            out.append(1)
        out.append(v)
    return out

def get_relative_fitness(i,pop):
    games_won = 0
    for adv in pop:
        game = [0,0,0,0,0,0,0,0,0]
        while(True):
            # our turn
            if(run_and_apply(i,game)):
                # we made a valid move and won
                if(win(game)):
                    games_won += 1
                    break
            else:
                # we crashed
                break

            # their turn
            game = flip(game)
            if(run_and_apply(i,game)):
                # they made a valid move and won
                if(win(game)):
                    break
            else:
                # they crashed
                games_won += 1
                break
    return games_won

def print_scores(score):
    for v in score:
        print(str(v[0]) + " " + v[1])


pop = []

#START
#Generate the initial population
for v in atomic_chars:
    pop.append(v)

scores = []

#Compute fitness
for v in pop:
    scores.append([get_relative_fitness(v,pop),v])


while (True):
    #Selection
    scores = sorted(scores, key=lambda x: x[0])
    scores = scores[:POP_SIZE]
    print_scores(scores)

    pop = list(map(lambda n: n[1],scores))

    #Crossover
    pop = pop + list(map(lambda n: mutate(n),pop))

    pop = set(pop)
    # remove the null program
    if "" in pop:
        pop.remove("")

    scores = []
    #Compute fitness
    for v in pop:
        scores.append([get_relative_fitness(v,pop),v])


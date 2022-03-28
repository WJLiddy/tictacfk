from bf import *
import random
from os import system, name

winrows = [[0,3,6],[1,4,7],[2,5,8],[0,1,2],[3,4,5],[6,7,8],[0,4,8],[2,4,6]]

# --- TIC TAC TOE LOGIC ---

# detect win state.
def win(boardstate):
    for v in winrows:
        if(boardstate[v[0]] == 1 and boardstate[v[1]] == 1 and boardstate[v[2]] == 1):
            return True
    return False

# flip tic tac toe game board.
def flip(game):
    out = []
    out = game[9:18]
    out += game[0:9]
    return out

# winning worth 100
WIN = 1
# losing worth 0 (hey, you didn't crash!!)
LOSE = 0
# losing because you sent shit is -10 000
LOSE_OOB = -100
# losing because you did NOTHING is -100 000
LOSE_NO_INPUT = -1000
LOSE_LOOP_FLAG = -1000000

# run and apply the brainfuck code to the game board. printstr if you want to see the new state.
# returns 0 if success, otherwise, the penalty for an invalid output that means the program is invalid and should be stopped.
def run_and_apply(code, state, printstr):
    #,>,>,>... just loads the state into memory
    out = run(",>,>,>,>,>,>,>,>,>,>,>,>,>,>,>,>,>,>"+code,state,MAX_INSTR)
    if(printstr):
        print("instr executed: " + str(out[1]))
        print("Move was " + str(out[0]))
    #  you didn't leave a move in the output
    if(len(out[0]) == 0):
        return LOSE_NO_INPUT
    #  your move wasn't 1-9.
    if(out[0][0] > 8):
        return LOSE_OOB
    #  you tried to place a move where there already was one.
    if(state[out[0][0]] != 0 or state[out[0][0]+9] != 0):
        return LOSE_OOB
    #  you endless loop'd.
    if(out[0][0] == -1):
        return LOSE_LOOP_FLAG
    # set the piece, and continue.
    state[out[0][0]] = 1
    return 0


# --- ANALYSIS CODE --- 

# one million i guess lol
CACHE_SIZE = 1000000

# cache results of game already played.
cached = {}
# do not submit functions that were culled
culled_blacklist = {}

# play a game between brainfuck programs "i" and "adv". Return the weighted value of the result (see above) and the board state.
# 99 of our functions spend time in here so call as infrequently as possible.
def play_game(i, adv, game, useinstr):
    while(True):
        # our turn
        move = run_and_apply(i,game,useinstr)
        if(move == 0):
            # we made a valid move and won
            if(win(game)):
                return [WIN, game]
        else:
            # run_and_apply returned non-zero, return it.
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
            return [WIN,game]
        game = flip(game)

def run_game_set(i,adv):
    game = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    # Take points for winning, tieing, or losing, going first
    val = play_game(i,adv,game,False)[0]
    if(val == LOSE_LOOP_FLAG):
        return LOSE_LOOP_FLAG

    # Now, the opponent goes first.
    game = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    # if em == 0 -> valid first move.
    em = run_and_apply(adv, game, False)
    game = flip(game)
    if(em == 0):
        val += play_game(i,adv,game, False)[0]
    else:
        val += WIN
    return val

# play a game against every other program in the population, and sum the scores.
def get_relative_fitness(i,pop):
    games_won = 0
    for adv in pop:
        # cache games we've already played.
        if(i+"|"+adv not in cached):
            cached[i+"|"+adv] = run_game_set(i,adv)
        games_won += cached[i+"|"+adv]
    return games_won

# print the result between two programs.
def printgame(v,adv):
    game = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    res = play_game(v,adv,game,True) 
    print("winner: " + (v if res[0] >= 0 else adv))
    print(res[1][0:3])
    print(res[1][3:6])
    print(res[1][6:9])
    print("---")
    print(res[1][9:12])
    print(res[1][12:15])
    print(res[1][15:18])

# --- GENETIC ALGO CODE ---
atomic_chars = "<>+-."
# don't include "," since there's nothing else to read.
MAX_INSTR = 512

def mutaten(parent,N):
    out = parent
    for i in range(random.randint(1,N)):
        out = mutate(out)
    return out

# simple mutation, adds or deletes atomic character(s) or a list.
def mutate(parent):
    child = list(parent)
    # 1/3 chance to add
    # 1/3 chance to delete
    # 1/3 chance for list.
    mut_type = random.randint(0,15)

    # insert sometimes.
    if(mut_type < 3):
            char = random.choice(atomic_chars)
            pos = random.randint(0,len(child))
            for i in range(random.randint(1,4)):
                child.insert(pos,char)

    # big chance to drop
    if(len(child) > 0 and mut_type >= 4 and mut_type <= 12):

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
    if(mut_type >= 13):
        #insert loop. Generate a start position
        start = random.randint(0,len(child))
        end = random.randint(start+1,len(child)+1)

        child.insert(start,"[")
        child.insert(end,"]")
    return ''.join(child)



def print_scores(score):
    for v in score:
        print(str(v[0]) + " " + v[1])

def friendlyname(bfcode):
    chars = ["E","A","R","I","O","T","N","S","L","C"]
    name = []
    for x in str(hash(bfcode)  % (10 ** 8)):
        name.append(chars[int(x)])
    return ''.join(name)
# This is a way to filter algorithms that are too similar, or honestly, just bad.
# If an algorithm has a score of less than KILL, it is considered a bad algorithm.
# Or, if the score between two algorithms is the same, we take the shorter one.
def cull(scores):
    bucket = {}
    for i in scores:
        if(i[0] not in bucket):
            bucket[i[0]] = []
        bucket[i[0]].append(i)

    scores2 = []
    for i in bucket:
        opts = sorted(bucket[i], key=lambda x: len(x[1]))
        if(opts[0][0] != LOSE_LOOP_FLAG):
            # keep the shortest codes in the class
            for v in opts:
                if(len(v[1]) == len(opts[0][1])):
                    scores2.append(v)
                else:
                    culled_blacklist[v[1]] = True
    scores2 = sorted(scores2, key=lambda x: x[0])
    scores2.reverse()
    return scores2

def remove_blacklisted(pop):
    ret = []
    for i in pop:
        if(i not in culled_blacklist):
            ret.append(i)
    return ret

def test():
    game = [0,0,0,0,0,0,0,0,0]
    while(True):
        #run_and_apply("<<+[<]>>++++++.",game,True)
        run_and_apply("<<+++++++<<++++<+<<<<[>+>][<]<.",game,True)
        print(game[0:3])
        print(game[3:6])
        print(game[6:9])
        game[int(input())] = 2
    exit()

#START

def runengine(gen_max):
    BEST_GEN_SIZE = 500
    POP_RATIO = 3
    POP_SIZE = BEST_GEN_SIZE * POP_RATIO

    #Generate the initial population
    pop = []

    # some good starter functions, use at your own risk. (these are pretty good, but could stifle diversity.)
    # pop.append("<<<<+[[<<<]+[<]<<<++++<<<++[[<<[<<[>>>>[>>>[>]]]]+>]]]>.")
    # pop.append("<<<+[[<<+<<]+[<]<<<+++<<<++[<<[<<[+>>>>>>]]+>]]>.")
    # pop.append("<++++++<<<+++[[++<<<]+<<<<+<<<++[<<[<[>>>>>>>[>>]]]+>]]>.")

    for v in atomic_chars:
        pop.append(v)

    # boost generation with these AIs which start in the corner.
    scores = []

    #Compute fitness
    for v in pop:
        scores.append([get_relative_fitness(v,pop),v])

    gen = 2

    # we keep the best generated algorithms around as a benchmark.
    # the population does not test against, itself, but rather, the new popuation.
    best_gen = list(map(lambda n: n[1],scores))

    last_best = ""
    while (gen < gen_max):
        gen += 1

        # allow a step of mutation if the population has not reached the max size yet.
        if(len(pop) <= POP_SIZE):
            pop = pop + list(map(lambda n: mutaten(n, 10),pop))

            # make only unique programs
            pop = set(pop)

            # remove the null program
            if "" in pop:
                pop.remove("")

            # remove programs with NOOPS which are just ineffecient.
            pop =  [x for x in pop if not "[]" in x]
            pop =  [x for x in pop if not "<>" in x]
            pop =  [x for x in pop if not "><" in x]
            pop =  [x for x in pop if not "+-" in x]
            pop =  [x for x in pop if not "-+" in x]
            pop =  [x for x in pop if not ".." in x]

        # We have reached the max population. Compare and take the best.
        else:

            # ocassionally reset the cache, so it doesn't eat all the memory.
            if(len(cached.values()) > 10 * CACHE_SIZE):
                cached.clear()
                print("matchup cache cleared.")

            # ocassionally reset the cache, so it doesn't eat all the memory.
            if(len(culled_blacklist.values()) > CACHE_SIZE):
                culled_blacklist.clear()
                print("blacklist cache cleared.")

            # remove any functions we culled in the past.
            print("\n---")
            print("GENERATION " + str(gen))
            print("POP SIZE: " + str(len(pop)))
            pop = remove_blacklisted(pop)
            print("POP SIZE AFTER BLACKLIST: " + str(len(pop)))
            print("LAST SURVIVOR SIZE: " + str(len(best_gen)))
        
            scores = []
            for v in pop:
                scores.append([get_relative_fitness(v,best_gen),v])
            # now, pick the best algorithms in each class. they are the shortest ones that behaved the best against the "best gen" algos.
            scores = cull(scores)
            print(str(len(scores)) + " unique children were generated.")

            if(len(scores) > BEST_GEN_SIZE):
                print(str(len(scores) - BEST_GEN_SIZE) + " children were dropped due to population limits")
            # set these as the new population.
            scores = scores[:BEST_GEN_SIZE]
            
            best_gen = list(map(lambda n: n[1],scores))
            pop[:] = list(best_gen)

            print("---")
            #print("SURVIVORS:\n" + str(best_gen))
            print("TOP FUNCTIONS")
            print(friendlyname(scores[0][1]) + " : " + str(scores[0][0]) + " (" + scores[0][1] + ")")
            print(friendlyname(scores[1][1]) + " : " + str(scores[1][0]) + " (" + scores[1][1] + ")")
            print(friendlyname(scores[2][1]) + " : " + str(scores[2][0]) + " (" + scores[2][1] + ")")

            print("BOTTOM FUNCTIONS")
            print(friendlyname(scores[-1][1]) + " : " + str(scores[-1][0]) + " (" + scores[-1][1] + ")")
            print(friendlyname(scores[-2][1]) + " : " + str(scores[-2][0]) + " (" + scores[-2][1] + ")")
            print(friendlyname(scores[-3][1]) + " : " + str(scores[-3][0]) + " (" + scores[-3][1] + ")")

            if(last_best == friendlyname(scores[0][1])+friendlyname(scores[1][1])+friendlyname(scores[2][1])):
                POP_SIZE = min(10000,POP_SIZE * POP_RATIO)
                print("stagnation detected. increasing population size...")
            else:
                POP_SIZE = BEST_GEN_SIZE * POP_RATIO
            last_best = friendlyname(scores[0][1])+friendlyname(scores[1][1])+friendlyname(scores[2][1])
            print("---")
            print("BEST GAME")
            printgame(scores[0][1],scores[1][1])
            printgame(scores[1][1],scores[0][1])
            print("---")
            print("Now mutating from " + str(len(pop)) + " parents.")
            #print_scores(scores)
    print(best_gen)

runengine(300)

# tictacfk
genetic algorithms to try to learn tic tac toe in brainf***

Can a genetic algorithm generate an AI to play tic tac toe?
Probably???

It works, but it's not good and makes mistakes, it can generate simple win conditions (such as putting three X's down the left row) but it struggles to pick up more sophisticated behaviors, such as starting in the middle with an "X" or stopping an opponent from winning.
my guess is that i need a HUGE amount of mutation in generation to stumble into a better AI which is just not likely. 

I added a preamble "<,<,<,<,<,<,<,<,<," which loads the game state into the cells, and it can very quickly pick up on >>>>>>>>>, which means it will learn to read the value of the board and react accordingly, but still, it struggles to get more sophisticated behaviors from there.


also, compile this with PyPy instead of stock Python, it's really incredibly fast. What a nice tool.


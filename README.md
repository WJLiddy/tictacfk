# tictacfk
genetic algorithms to try to learn tic tac toe in brainf***

Can a genetic algorithm generate an AI to play tic tac toe?
Probably???

It's close to generating an optimal strategy.
It generated the program <<+++<<+<+<<<<[>+[>[+>++++>]-]]<. which is remarkably close to only
generating a "perfect" output.

At some point, I want to convert to rust. Python is slow and hard to profile properly. 

Also, I added a preamble "<,<,<,<,<,<,<,<,<," which loads the game state into the cells, and it can very quickly pick up on >>>>>>>>>, which means it will learn to read the value of the board and react accordingly, but still, it struggles to get more sophisticated behaviors from there.


also, compile this with PyPy instead of stock Python, it's really incredibly fast. What a nice tool.


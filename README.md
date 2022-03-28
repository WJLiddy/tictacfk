# tictacfk

QUESTION

Can we use a genetic algorithm to generate AIs to solve things?

The answer is yes. https://github.com/primaryobjects/AI-Programmer.

But I wanted to try to do it myself, with an unbounded genome size, and in good old python.

It also uses an adversarial model for fitness, so it's a kind of unsupervised learning, as opposed to the git project posted above.

EXPERIMENT

Using a tiny langauge (brainf***), generate random programs to win a tiny game (tic tac toe), then evaluate fitness, keep the N fittest programs, mutate, rinse, repeat

RESULTS

ehhhhhhhhhhhhhhhhhhhhhhhhhh

It's CLOSE to generating an optimal strategy.

I was able to generate a program that usually wins and usually gives legal output, but it's not optimal, sometimes it will suggest an illegal move or blunder.

I think it shows promise, but I have bigger fish to fry right now.

Possible improvements: use an abbreviated form of brain*** (such as brain*** extended III) so I don't need to adjust ++++++++++++'s all day.

RUNNING

run engine.py with pypy3. It will run FAR faster on linux, for whatever reason.

I think someday I will convert this to Rust or Go or one of those newfangled trendly languages.

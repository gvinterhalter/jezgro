PROG = traversal
FLAGS = --std=c++11 -Wall -I/usr/lib/llvm-3.8/include -L/usr/lib/x86_64-linux-gnu/ -lclang-3.8

.PHONY all clean:

all:
	g++ $(PROG).cc -o $(PROG)  $(FLAGS);

clean: all
	rm $(PROG);

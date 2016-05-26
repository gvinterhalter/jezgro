CC = g++
CFLAGS = -I /usr/lib/llvm-3.6/include
CLIB = -L /usr/lib/llvm-3.6/lib
libs = -lclang

clg : clg.cpp utils.hpp
	$(CC) clg.cpp -o clg $(CFLAGS) $(CLIB) $(libs)

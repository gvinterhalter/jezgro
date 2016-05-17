from ctypes import *

prog = CDLL('./in.so', mode=RTLD_GLOBAL)
prog.print()
prog1 = CDLL('./in1.so', mode=RTLD_GLOBAL)
prog1.f()


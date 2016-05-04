import os, sys

r, w = os.pipe()

processid = os.fork()
if processid:
    os.close(w)
    r = os.fdopen(r)
    str = r.read()
    print( "text =", str)
else:
    # This is the child process
    os.close(r)
    w = os.fdopen(w, 'w')
    w.write("Text written by child...")



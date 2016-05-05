import os
import sys
import re

def show(t):
    for x in t:
        print(x)

text = ""
with open('bla.cpp', 'r') as f:
    text = f.read()



bodies = []
b = 0
c = b
start = end = 0
komentar = False
for m in re.finditer("'{'|'}'|{|}|\"|", text):
    t = m.group()
    if t == '"':
        # if '"' non escape provera TODO
        komentar = True if komentar==False else False  
    if t == "'{'" or t == "'}'" or komentar:
        continue
    if t  == '{':
        if c == b:
            start = m.start()
        c +=1
    elif t == '}':
        c -=1
        if c == b:
            end = m.end()
            bodies.append((start,end))

print(bodies)




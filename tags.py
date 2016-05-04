import os
import sys
import re
import io
import subprocess
import tempfile

otherRegex = re.compile(
    r'''^\s*(#define|#include|using(?:\s+namespace)?)(.+)'''
    , re.MULTILINE)


class decl:
    def __init__(self, name, full):
        self.name = name
        self.full = full

    def __str__(self):
        return "%s => %s" % (self.name, self.full)
    def __repr__(self):
        return "%s => %s" % (self.name, self.full)

    def __eq__(self, a):
        return a.name == self.name

    def __hash__(self):
        return hash(self.name)


class sharedObject:
    def __init__(self):
        self.decls ={
                'types'     : set(),
                'variables' : set(),
                'functions' : set(),
                'classes'   : set(),
                'include'   : set(),
                'define'    : set(),
                'using'     : set(),
                }

    def merge(self, new_decl):
        for key in self.decls:
            self.decls[key] = new_decl.decls[key].union(self.decls[key])

    def deleteIfExists(self, new_decl):
        for key in self.decls:
            self.decls[key].difference_update( new_decl.decls[key] )
    
    def printt(self):
        for d in self.decls:
            print(d, self.decls[d])

    def get(self, key):
        result = []
        for d in self.decls[key]:
            result.append(d.full)
        return '\n'.join(result)


def get_declarations(code):

    f = tempfile.NamedTemporaryFile(suffix='.cpp')
    f.write(bytes(code, 'utf-8'))
    f.flush()
    name = f.name

    cmd = ['ctags',
            '--sort=no',
            '--language-force=C++', 
            '--fields=knsSzt', 
            '-f', '/dev/stdout', name]

    tokenText = subprocess.getoutput(" ".join(cmd))

    def get(kind, lines):
        for l in lines[3:]:
            k, v = l.split(':')
            if k == kind:
                return v
        return None 

    so = sharedObject()



    for tokens in tokenText.split('\n'):
        tokens = tokens.split('\t')

        kind = get("kind", tokens)

        if kind  == 'f': #function
            if not get("class", tokens):
                d = tokens[0] + tokens[5].split(':')[1] + ';'
                return_value = tokens[2][2:].split(tokens[0])
                d = return_value[0] + d 
                # print(d)
                so.decls['functions'].add(decl(tokens[0], d))
        elif kind == 'v': #variable
            d = tokens[2][2:-4].split('=')
            d = d[0] if len(d) == 1 else d[0]+';'
            if not d.startswith('static'):
                # print(d)
                so.decls['variables'].add( decl(tokens[0], 'extern ' + d) )
        elif kind == 't': # new type
            d = tokens[2][2:-4]
            # print(d)
            so.decls['types'].add(decl(tokens[0], d))
        elif kind == 'c': # class
            so.decls['classes'].add(decl(tokens[0], tokens[0]))

    # sad moramo rucno da izvucemo ostale informacije
    for m in re.finditer(otherRegex, code):
        kind = m.group(1)
        if kind == '#include':
            so.decls['include'].add( decl(m.group(2), m.group(0).strip()) )
        elif kind == '#define':
            so.decls['define'].add(
                    decl(m.group(2).split()[0], m.group(0).strip()))
        else:  # mora da bude using
            name = m.group(2).split(';')[0]
            name = name.strip()
            so.decls['using'].add(decl(name, m.group(0).strip()))

    return so


import clang.cindex as clg, asciitree, sys
index = clg.Index.create()
tu = index.parse("t1.cpp")

i = 0
def prodji(n):
    global i

    f = n.location.file.name if n.location.file else None
    if f and (f.endswith(b'.h') or f.endswith(b'.hpp')):
      return

    tokens = ''
    if n.kind.is_declaration():
      tokens = ' '.join([str(t.spelling, encoding='utf-8') 
                      for t in n.get_tokens()])
      
    info = "%s (%s) :  %s" % (
            str(n.displayname, encoding='utf-8'), 
            str(n.kind).split(".")[1],
            tokens
            )


    print("%s%s" %(i*"  ", info))

    for x in n.get_arguments():
        print(x.displayname)

    for c in n.get_children():
        i += 1
        prodji(c)
        i -=1
        

prodji(tu.cursor)




from shell import *

poruke = [
"""
int a = 6;
int *p = nullptr;
%r cout  << a<< endl;
""",
"""
%%r 
cout << a  << endl;
""",
]

import shutil

shell = ShellPlusPlus()
for p in poruke:
    shell.execute_cell(p)

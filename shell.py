import os, fcntl, sys ,io, tempfile
import subprocess
import re
import copy

import ctypes

from tags import *

RTLD_NOW = 1
RTLD_LAZY = 2
RTLD_GLOBAL = 256
RTLD_LOCAL = 0
RTLD_NODELETE = 4096
RTLD_NOLOAD = 4
RTLD_DEEPBIND = 8


objects = []

libc = ctypes.CDLL(None)

class CompileErr(BaseException):
    def __str__(self):
        return ""

class ShellPlusPlus:
    reComment = re.compile(r'/\*.*?\*/|//.*?$', re.MULTILINE|re.DOTALL)
    # ograniceni smo da magic mora da se zavrsi sa \n a pre je dozvoljeno samo blanko
    reMagic = re.compile(r'^\s*(%[a-zA-Z_][a-zA-Z_0-9]*.*)', re.MULTILINE)
    reCellMagic = re.compile(r'^\s*(%%[a-zA-Z_][a-zA-Z_0-9]*.*)')

    def  __init__(self):

        # opcije za kompajliranje i linkovanje
        self.compile_flags = [ "-std=c++11", "-Wall" ]
        self.include_paths = []
        self.lib_paths = []
        self.libs = []
        self.compiler = "g++"

        # gde ce biti smesteni tmp fajlovi za kompilaciju
        self.tmp_path = tempfile.mkdtemp("_c++jezgro")
        self.i = 0

        self.decl = sharedObject();
        self.tmp_decl = sharedObject();
        self.eval_lines = []
        

        r, w = os.pipe()
        fcntl.fcntl(r, fcntl.F_SETFL, os.O_NONBLOCK)
        os.dup2(w, 1)
        self.out = os.fdopen(r)

        r, w = os.pipe()
        fcntl.fcntl(r, fcntl.F_SETFL, os.O_NONBLOCK)
        os.dup2(w, 2)
        self.err = os.fdopen(r)

        r, w = os.pipe()
        fcntl.fcntl(r, fcntl.F_SETFL, os.O_NONBLOCK)
        os.dup2(r, 0)
        os.write(w, b'aa')


    def insert_declarations(self, code):
        result = []
        result.append( self.tmp_decl.get('define') )
        result.append( self.tmp_decl.get('include') )
        result.append( self.tmp_decl.get('using') )
        result.append( self.tmp_decl.get('types') )
        result.append( self.tmp_decl.get('variables') )
        result.append( self.tmp_decl.get('functions') )
        result.append(code)
        if len(self.eval_lines) > 0:
            result.append("""
void __run__(void) { 
try{ %s }
catch (std::exception& e)
{
    std::cout << "Exception catched : " << e.what() << std::endl;
}
}
                    """ %
                           '\n'.join(self.eval_lines))
        return '\n'.join(result)

    def prepare(self, code):
        self.tmp_decl = copy.deepcopy(self.decl)

        new_decl = get_declarations(code)

        self.tmp_decl.deleteIfExists(new_decl)
        code = self.insert_declarations(code)

        self.tmp_decl.merge(new_decl)

        return code



    def compile(self, code):
        ''' Kompajliramo kod i proizvodimo .cpp i .so'''
        self.i += 1

        compile_path = self.tmp_path + "/%i.cpp" % self.i
        result_path  = self.tmp_path + "/%i.so"  % self.i

        with open(compile_path, 'w') as f: 
            f.writelines(code)

        compile_command = [self.compiler, "-fpic", "-shared"]
        compile_command += self.compile_flags 
        compile_command += self.include_paths 
        compile_command += self.lib_paths
        compile_command += [ compile_path, "-o", result_path]
        compile_command += self.libs


        if subprocess.call(compile_command):
            #error ( vraca razlicito od nula kad je greska)
            raise CompileErr

        return result_path

    def load(self, so_file):
        so_handle = ctypes.CDLL(so_file, RTLD_GLOBAL|RTLD_DEEPBIND|RTLD_NOW)
        return so_handle

    def execute_code(self, code):
        '''Izvrsavamo kod(prepare,compile,load,execute)'''

        status = ["ok", '']

        if code == None or len(code.strip()) == 0:
            return status

        try:
            code = self.prepare(code)
            so_file = self.compile(code)
            so_handle = self.load(so_file)
            so_handle[b'_Z7__run__v']() # pozivamo funkciju void __run__(void)
            status[1] = self.out.read()

        except CompileErr:
            status = ['Compile Error', str(self.err.read())]

        except OSError:
            status = ['Link Error', 'link greska']

        except AttributeError:
            pass # funkcija run ne postoji
        
        return status

    def execute_cell(self, code):
        self.eval_lines = []   # Ovde cuvamo linije sa %r 
        code = re.sub(self.reComment, "", code) #uklanjamo komentare

        status = []
        #pokusavamo da uparimo cell magic
        m = re.match(self.reCellMagic, code)
        if m:
            magic = m.group(1)
            status = self.execute_cell_magic(magic, code[m.end():])
        else:
            code = self.inject_magic(code) # mozda ima line magic 
            status = self.execute_code(code)

        if status[0] == 'ok':
            self.decl = self.tmp_decl

        return status
        


    def execute_cell_magic(self, magic, code):
        return self.execute_code(code)

    def execute_magic(self, magic):
        # return "/* %s */" % (magic)
        ms = magic.split()
        magic, code = ms[0], ' '.join(ms[1:])
        if magic == "%r":
            self.eval_lines.append(code)
        return "/* %s */" % (magic)

    def inject_magic(self, code):
        magic_code = ""
        ms = re.finditer(self.reMagic, code) # trazimo sva pojavljivanja
        i = 0
        for m in ms:
            magic_code += code[i : m.start()]
            magic_code += self.execute_magic(m.group(1))
            i = m.end()
        magic_code += code[i:]
        return magic_code


t0 = """
#include <iostream>
using namespace std;

int a = ;
%r cout << a << endl;

"""
#
# t0_1 = """
#
# int print(){
#   cout << "hello world " << a << endl;
#   return 4;
# }
#
# %r    print();
# """

# t1 = """
# %%hello -s -c -d -f
#
#     int print(){
#       cout << "hello world " << a << endl;
#       return 4;
#     }
#
#     int pprint(){
#         print();
#         print();
#         return 0;
#     }
#
#
#     void __run__(void){
#         print();
#     }
#
# """ 
# t2 = """
#
#     void print(){
#        cout << " MAAAAAA " << endl;
#     }
#
#     void __run__(void){
#         print();
#     }
#
#  """ 
# t3= """
#
#
#     voi __run__(void){ print(); }
#
#  """ 
#
# import shutil
#
# shell = ShellPlusPlus()
# try:
#     shell.execute_cell(t0)
#     # shell.execute_cell(t0_1)
#     # shell.execute_cell(t1)
#     # shell.execute_cell(t2)
#     # shell.execute_cell(t3)
# finally:
#     shutil.rmtree(shell.tmp_path)

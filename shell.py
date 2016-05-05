import os, fcntl, sys ,io, tempfile
import subprocess
import re
import copy

import ctypes

from jezgro.tags import *

# ctypes ne definise sve konstantne za C dl_open f-ju pa ih rucno definisemo
RTLD_NOW = 1
RTLD_LAZY = 2
RTLD_GLOBAL = 256
RTLD_LOCAL = 0
RTLD_NODELETE = 4096
RTLD_NOLOAD = 4
RTLD_DEEPBIND = 8

regex_comment = re.compile(r'/\*.*?\*/|//.*?$', re.MULTILINE|re.DOTALL)
# magic je ogranicen na jednu liniju
regex_line_magic = re.compile(r'^\s*(%[a-zA-Z_][a-zA-Z_0-9]*)(.*)', re.MULTILINE)
regex_cell_magic = re.compile(r'^\s*(%%[a-zA-Z_][a-zA-Z_0-9]*)(.*)', re.DOTALL)
regex_msg_fillter = re.compile(r'^/tmp/[^ \s\t]*\s', re.MULTILINE)

class CompileErr(BaseException):
    def __init__(self, msg):
        print(msg)
        self.error = msg
    def __str__(self):
        return self.error

class MagicError(BaseException):
    def __init__(self, msg=""):
        self.error=msg
    def __str__(self):
        return self.error


def fillter_msg(msg):
    return re.sub(regex_msg_fillter, '', msg, re.MULTILINE)


class ShellPlusPlus:

    def  __init__(self):

        # opcije za kompajliranje i linkovanje
        self.compile_flags = [ "-std=c++11", "-Wall" ]
        self.include_paths = []
        self.lib_paths = []
        self.libs = []
        self.compiler = "g++"

        # gde ce biti smesteni tmp fajlovi za kompilaciju
        self.tmp_path = tempfile.mkdtemp("_c++jezgro")
        self.i = 1

        self.debug = False # da li da prikaze kod koji se kompajlira

        self.decl = sharedObject();
        self.tmp_decl = sharedObject();
        self.eval_lines = []
        

        # stdin, stdout, adn stderr redirection

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

        self.run_template = """
void __run__(void) { 
  try{
      %s
      cout.flush();
  } catch (std::exception& e) {
      std::cout << "Exception catched : " << e.what() << std::endl;
  }
}
        """
        status = self.execute_cell("#include <iostream>\nusing namespace std;")


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
            result.append( self.run_template % '\n'.join(self.eval_lines))


        return '\n'.join(result).strip()

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

        # ne zelim da korisnik moze da ukloni -fpic i -shared, zato
        # ih eksplicitno navodim
        compile_command = [self.compiler, "-fpic", "-shared"]
        compile_command += self.compile_flags 
        compile_command += self.include_paths 
        compile_command += self.lib_paths
        compile_command += [ compile_path, "-o", result_path]
        compile_command += self.libs


        if subprocess.call(compile_command):
            #error ( vraca razlicito od nula kad je greska)
            raise CompileErr(self.err.read())

        return result_path

    def load(self, so_file):
        ''' Ucitavamo deljenu biblioteku, koristimo:
            RTLD_GLOBAL, RTLD_DEEPBIND i RTLD_NOW '''
        so_handle = ctypes.CDLL(so_file, RTLD_GLOBAL|RTLD_DEEPBIND|RTLD_NOW)
        return so_handle

    def run(self, handle):
        ''' Pozivamo funkciju void __run__(void)) u deljenom objektu
            Ako ne postoji bice bacen izuzetak AttributeError koji ignorisemo '''
        handle[b'_Z7__run__v']() 

    def execute_code(self, code):
        '''Izvrsavamo kod(prepare,compile,load,execute)'''

        status = ["ok", '']

        no_code = False
        if no_code and (len(code.strip())):
            no_code = True
            if self.eval_lines == []:
                return status

        try:
            code = self.prepare(code)
            so_file = self.compile(code)
            so_handle = self.load(so_file)
            self.run(so_handle)
            status[1] = self.out.read()

            if no_code:
                pass
                # unload so_handle TODO 

        except CompileErr as e:
            status = ['Compile Error', fillter_msg(str(e)) ]

        except OSError as e:
            status = ['Link Error', fillter_msg(str(e))]

        except AttributeError:
            pass # funkcija run ne postoji

        if self.debug:
            status[1] = '<-code->\n%s\n<------>\n%s' % (code, status[1])
        
        return status

    def execute_cell(self, code):
        '''Izvrsavamo kod celije'''

        status = []
        self.eval_lines = []   # Ovde cuvamo linije sa %r 
        code = re.sub(regex_comment, "", code) #uklanjamo komentare

        #pokusavamo da uparimo cell magic, m.group(0) je magic
        m = re.match(regex_cell_magic, code)

        try:
            if m:
                status = self.execute_magic(m.group(1), m.group(2))
            else:
                code = self.inject_magic(code) # mozda ima line magic 
                status = self.execute_code(code)
        
        except MagicError as e:
            return ['error', str(e)]

        if status[0] == 'ok':
            self.decl = self.tmp_decl


        return status
        


    def execute_magic(self, magic, code):
        if magic in self.magics:
            return self.magics[magic](self, code)

        raise MagicError("%s is not defined" % magic)

        

    def inject_magic(self, code):
        magic_code = ""

        i = 0
        for m in re.finditer(regex_line_magic, code):
            magic_code += code[i : m.start()] # sta smo uhvatili pre %r
            magic_code += self.execute_magic(m.group(1), m.group(2)) # obradjena %r linija
            i = m.end()

        magic_code += code[i:] # sta ide nakon poslednje %r linije

        return magic_code



    ##  definisemo magic funkcije ##

    def _line_r(self, code):
        self.eval_lines.append(code)
        return ''

    def _cell_r(self, code):
        code = self.inject_magic(code) # mozda ima nekih line magic-a
        self.eval_lines.append(code)
        self.prepare(code)
        return self.execute_code('/* run */') 

    magics = {
            "%r" : _line_r,
            "%%r" : _cell_r,
             }

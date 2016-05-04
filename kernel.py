import io
from ipykernel.kernelbase import Kernel

from subprocess import call

from shell import *


class Jezgro(Kernel):
    language = 'C++'
    language_version = 'c++11'
    language_info = {'mimetype': 'text/plain'}
    banner = "Test C++ Kernel"

    compiler = "clang"

    # Info o Jezgru 
    implementation = 'C++Jezgro'
    implementation_version = '0.01'
    language_info = {
                     'name': 'c++',
# FIX_ME, get it run time
                     'version': "3.9",
                     'mimetype': 'text/x-c++src',
                     # 'codemirror_mode': {'name': 'ipython',
                     #                     'version': sys.version_info[0]},
                     # 'pygments_lexer': 'ipython%d' % (3 if PY3 else 2),
                     # 'nbconvert_exporter': 'python',
                     'file_extension': '.cpp'
                    }


    my_shell = ShellPlusPlus()


    def do_execute(self, code, silent, store_history=True,
                 user_expressions=None, allow_stdin=False):
        """
    code             : str  - kod koji treba izvršiti
    silent           : bool - Ako je True izvršavanje će bit što je tiše moguće:
                             + neće se slati signal na IOPUB kanal
                             + neće postojati execute_result
    store_history    : bool - Ako je True jezgro će sačuvati izvršavanje u istoriji.
                          Ako je silent True onda je store_history False
    user_expressions : dict - 
    allow_stdin      : bool -

    return vrednost je dict sledećeg oblika (execute_replay): 

    {
    'status' : str,  # One of: 'ok' OR 'error' OR 'abort'

    'execution_count' : int, # The global kernel counter that increases by
                           # one with each request that stores history.

    # ako je status = 'abort' ovo je kraj poruke. (Recimo kernel je prekinut)
    # ako je status = 'ok' imamo dodatna polja:
        'payload' : list(dict),  # deprecated default None
        'user_expressions' : dict, # Results for the user_expressions.
    # ako je status = 'error' imamo dodatna polja:
    'ename' : str,     # Exception name, as a string
    'evalue' : str,    # Exception value, as a string
    'tracebak' : list, # The traceback will contain a list of frames,
                       # represented eač as a string
    }
        """

        
        #odgovor koji vraćamo sa return
        replay_content = {'execution_count' : self.execution_count}

        # f = io.BytesIO()
        # with shell.stdout_redirector(f):
        #     print("HEllo")

        status = 'ok'
        evalue = ''
        if not silent:
            reply = self.my_shell.execute_cell(code)
            status = reply[0]
            reply = reply[1]
            evalue = reply
            stream_content = {'name': 'stdout', 'text': reply}
            self.send_response(self.iopub_socket, 'stream', stream_content)


        if status == 'ok':
            replay_content['status'] = 'ok'
            replay_content['payload'] = []
            replay_content['user_expressions'] = {}
        elif status == 'error':
            replay_content['status'] = 'error'
            replay_content['ename'] = 'GRESKA!!!'
            replay_content['evalue'] = evalue
            replay_content['traceback'] = []


        return replay_content




    def do_complete(self, code : str, cursor_pos : int) -> dict:
        # FIXME: IPython completers currently assume single line,
        # but completion messages give multi-line context
        # For now, extract line from cell, based on cursor_pos:
        if cursor_pos is None:
            cursor_pos = len(code)
        # line, offset = line_at_cursor(code, cursor_pos)
        # line_cursor = cursor_pos - offset

        # txt, matches = self.shell.complete('', line, line_cursor)
        matches = ["Hello", "Hellllloooo", "Hy", "Complete me"]


        return {'matches' : matches,
                'cursor_end' : cursor_pos, # gde da se zavrsi zamena
                'cursor_start' : 0, # odakle da pocne zamena
                'metadata' : {},
                'status' : 'ok'}

    def do_inspect(self, code, cursor_pos, detail_level=0):
        name = token_at_cursor(code, cursor_pos)
        info = self.shell.object_inspect(name)

        # reply_content = {'status' : 'ok'}
        # reply_content['data'] = data = {}
        # reply_content['metadata'] = {}
        # reply_content['found'] = info['found']
        # if info['found']:
        #     info_text = self.shell.object_inspect_text(
        #         name,
        #         detail_level=detail_level,
        #     )
        #     data['text/plain'] = info_text

        return reply_content

    def do_history(self, hist_access_type, output, raw, session=None, start=None,
                   stop=None, n=None, pattern=None, unique=False):
        hist = []
        # if hist_access_type == 'tail':
        #     hist = self.shell.history_manager.get_tail(n, raw=raw, output=output, include_latest=True)
        # elif hist_access_type == 'range':
        #     hist = self.shell.history_manager.get_range(session, start, stop, raw=raw, output=output)
        # elif hist_access_type == 'search':
        #     hist = self.shell.history_manager.search( pattern, raw=raw, output=output, n=n, unique=unique)

        return {'history' : list(hist)}




    # def do_is_complete(self, code):
    #     status, indent_spaces = self.shell.input_transformer_manager.check_complete(code)
    #     r = {'status': status}
    #     if status == 'incomplete':
    #         r['indent'] = ' ' * indent_spaces
    #     return r




    # def do_apply(self, content, bufs, msg_id, reply_metadata):
    #     from .serialize import serialize_object, unpack_apply_message
    #     shell = self.shell
    #     try:
    #         working = shell.user_ns
    #
    #         prefix = "_"+str(msg_id).replace("-","")+"_"
    #
    #         f,args,kwargs = unpack_apply_message(bufs, working, copy=False)
    #
    #         fname = getattr(f, '__name__', 'f')
    #
    #         fname = prefix+"f"
    #         argname = prefix+"args"
    #         kwargname = prefix+"kwargs"
    #         resultname = prefix+"result"
    #
    #         ns = { fname : f, argname : args, kwargname : kwargs , resultname : None }
    #         # print ns
    #         working.update(ns)
    #         code = "%s = %s(*%s,**%s)" % (resultname, fname, argname, kwargname)
    #         try:
    #             exec(code, shell.user_global_ns, shell.user_ns)
    #             result = working.get(resultname)
    #         finally:
    #             for key in ns:
    #                 working.pop(key)
    #
    #         result_buf = serialize_object(result,
    #             buffer_threshold=self.session.buffer_threshold,
    #             item_threshold=self.session.item_threshold,
    #         )
    #
    #     except:
    #         # invoke IPython traceback formatting
    #         shell.showtraceback()
    #         # FIXME - fish exception info out of shell, possibly left there by
    #         # run_code.  We'll need to clean up this logic later.
    #         reply_content = {}
    #         if shell._reply_content is not None:
    #             reply_content.update(shell._reply_content)
    #             # reset after use
    #             shell._reply_content = None
    #             
    #             # FIXME: deprecate piece for ipyparallel:
    #             e_info = dict(engine_uuid=self.ident, engine_id=self.int_id, method='apply')
    #             reply_content['engine_info'] = e_info
    #
    #         self.send_response(self.iopub_socket, u'error', reply_content,
    #                             ident=self._topic('error'))
    #         self.log.info("Exception in apply request:\n%s", '\n'.join(reply_content['traceback']))
    #         result_buf = []
    #     else:
    #         reply_content = {'status' : 'ok'}
    #
    #     return reply_content, result_buf

    def do_clear(self):
        # self.shell.reset(False)
        return dict(status='ok')



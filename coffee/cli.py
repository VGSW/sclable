from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token
import subprocess
import yaml
import os
import re

from coffee.coffee import Issue, Transition, FSM
from coffee.graph import graph


class CLI ():

    def __init__ (self):
        self.fsm = None
        self.issues = None
        self.loaded_from = []
        self.history = FileHistory (os.path.expanduser ('~/.coffee.history'))
        self.lives = 5

        self.start()


    def get_bottom_toolbar_tokens (self, cli):
        last = ''
        if self.history and len (self.history.strings) > 0:
            last = self.history.strings[-1]

        return [(Token.Toolbar,
            '*** Lives: <{lives}> *** Loaded: {loaded} *** Enter "help" for help ***'.format (
                lives  = self.lives,
                loaded = ', '.join (sorted (self.loaded_from)) or '/dev/zero',
        ))]


    def print_all (self, **kwa):
        fsm = kwa.get ('fsm')
        issues = kwa.get ('issues')

        print ()
        for state in fsm.workflow():
            print ('  (*) {}'.format (state.name))
            for issue in list (filter (lambda i: i.state == state.name, issues)):
                print ('    (-) {}'.format (issue.title))
        print ()


    def print_fsm (self, **kwa):
        fsm = kwa.get ('fsm')

        print ()
        for state in fsm.workflow():
            print ('  (*) {name} ({next_states}){is_start}{is_end}'.format (
                name = state.name,
                next_states = ', '.join (
                    '-> {}'.format (e.next_state.name)
                    for e in sorted (state.events, key = lambda e: e.next_state.name)) or '-',
                is_start = ' (S)' if state.is_start else '',
                is_end = ' (E)' if state.is_end else '',
            ))

        print ()
        print ('(S) ... state is a start state')
        print ('(E) ... state is an end state')
        print ()


    def draw_fsm (self, **kwa):
        try:
            graph (
                fsm          = self.fsm,
                source_files = sorted (self.loaded_from),
                output_file  = kwa.get ('output_file'),
                fmt          = kwa.get ('fmt'),
            )
        except Exception as e:
            print ('ERROR: {}'.format (e))


    def load (self, **kwa):
        filename = kwa.get ('filename')

        with open (filename, 'r') as ymlfile:
            fsm, issues = None, None
            inputs = yaml.load (ymlfile)

            if type (inputs) != dict:
                print ('ERROR: can\'t load from <{}>\n'.format (filename))
                self.lives -= 1
                return dict (fsm = None, issues = None)

            if inputs.get ('issues'):
                issues = [
                    Issue (
                        title = issue.get ('title'),
                        state = issue.get ('state'),
                    )
                    for issue in inputs.get ('issues')
                ]

            if inputs.get ('transitions'):
                fsm = FSM (transitions = inputs.get ('transitions'))

            return dict (fsm = fsm, issues = issues)


    def usage (self):
        print ('\nAvailable commands')
        print ('  load <filename> ..... load the given yaml file')
        print ('  !<command> .......... run <command> in a shell')
        print ('  print ............... print loaded data')
        print ('  print fsm ........... print the FSM only')
        print ('  print fsm-svg ....... draw the FSM (SVG)')
        print ('  print fsm-ascii ..... draw the FSM (ASCII)')
        print ('  clear ............... clear data')
        print ('  quit ................ quit')
        print ('  help ................ you\'re reading it, HTH\n')


    def clear (self):
        self.fsm = None
        self.issues = None
        self.loaded_from = []


    def start (self):
        self.usage()

        while self.lives:
            cmd = prompt (
                '>> ',
                completer = WordCompleter ('load print clear quit help'.split()),
                history = self.history,
                auto_suggest = AutoSuggestFromHistory(),
                get_bottom_toolbar_tokens = self.get_bottom_toolbar_tokens,
                style = style_from_dict ({ Token.Toolbar: '#ffffff bg:#333333' }),
            )

            if re.search ('^load (.+)', cmd):
                filename = cmd [5:]

                if not filename or not os.path.isfile (filename):
                    print ('ERROR: Please enter a valid filename\n')
                    self.lives -= 1
                    continue

                try:
                    jim = self.load (filename = filename)
                except RuntimeWarning as w:
                    print ('ERROR: invalid data: <{}>\n'.format (w))
                    self.lives -= 1
                    continue

                self.loaded_from.append (filename)
                loaded_ok = False

                if jim.get ('fsm'):
                    self.fsm = jim.get ('fsm')
                    loaded_ok = True
                if jim.get ('issues'):
                    self.issues = jim.get ('issues')
                    loaded_ok = True
                if not loaded_ok:
                    len (self.loaded_from) and self.loaded_from.pop()
            elif re.search ('^!(.+)', cmd):
                print (subprocess.run (
                    cmd[1:].split(),
                    stdout = subprocess.PIPE,
                ).stdout.decode())
            elif re.search ('^print.*', cmd):
                if not self.fsm:
                    print ('ERROR: Please load an FSM\n')
                    self.lives -= 1
                    continue
                if cmd == 'print':
                    if not self.issues:
                        print ('ERROR: Please load issues\n')
                        self.lives -= 1
                        continue
                    self.print_all (fsm = self.fsm, issues = self.issues)
                else:
                    if cmd == 'print fsm':
                        self.print_fsm (fsm = self.fsm)
                    elif cmd == 'print fsm-svg':
                        self.draw_fsm (
                            fsm = self.fsm,
                            fmt = 'svg',
                        )
                    elif cmd == 'print fsm-ascii':
                        self.draw_fsm (
                            fsm = self.fsm,
                            fmt = 'ascii',
                        )
                    else:
                        print ('ERROR: invalid command, try again :-)\n')
                        self.lives -= 1
                        self.usage()
            elif cmd == 'clear':
                self.clear()
            elif cmd == 'quit':
                exit()
            elif cmd == 'help':
                self.usage()
            elif cmd == 'oneup':
                self.lives += 1
            else:
                print ('ERROR: invalid command, try again :-)\n')
                self.lives -= 1
                self.usage()

        print ('\n\n\tG A M E   O V E R\n\n')

if __name__ == '__main__':
    CLI().start()

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
        self.issues = []
        self.loaded_from = []
        self.history = FileHistory (os.path.expanduser ('~/.coffee.history'))
        self.lives = 5

        self.commands = [
            dict (command = 'load',            description = 'load the given yaml file', handler = self.load,      usage = 'load <filename>'),
            dict (command = '!',               description = 'run <command> in a shell', handler = self.shell,     usage = '! <command>'),
            dict (command = 'print',           description = 'print loaded data',        handler = self.printer),
            dict (command = 'print fsm',       description = 'print the FSM only',       handler = self.printer),
            dict (command = 'print fsm-svg',   description = 'draw the FSM (SVG)',       handler = self.printer),
            dict (command = 'print fsm-ascii', description = 'draw the FSM (ASCII)',     handler = self.printer),
            dict (command = 'clear',           description = 'clear data',               handler = self.clear),
            dict (command = 'quit',            description = 'quit',                     handler = self.quit),
            dict (command = 'help',            description = 'you\'re reading it, HTH',  handler = self.usage),
        ]

        self.start()


    def start (self):
        self.usage ()

        # note: must put '-' as last to prevent its meaning for ranges
        prog = re.compile ('^(?P<command>[\w!]+)( (?P<param>[\w./-]+)){0,1}')

        while self.lives:
            cmd = prompt (
                '>> ',
                completer = WordCompleter ('load print clear quit help fsm fsm-ascii fsm fsm-svg'.split()),
                history = self.history,
                auto_suggest = AutoSuggestFromHistory(),
                get_bottom_toolbar_tokens = self.get_bottom_toolbar_tokens,
                style = style_from_dict ({ Token.Toolbar: '#ffffff bg:#333333' }),
            )

            if not cmd:
                print ('ERROR: empty command, try again\n')
                self.lives -= 1
                continue

            result = (prog.match (cmd))

            #  print ('cmd: {}'.format(cmd))
            #  print ('command: {}'.format(result.group('command')))
            #  print ('param: {}'.format(result.group('param')))

            command = [c for c in self.commands if c.get ('command') == result.group ('command')]

            if not len (command):
                print ('ERROR: invalid command, try again\n')
                self.lives -= 1
                continue

            try:
                if result.group('param'):
                    command.pop().get('handler')(result.group('param'))
                else:
                    command.pop().get('handler')()

            except Exception as e:
                print ('ERROR: invalid command, try again: {}\n'.format (e))
                raise e
                self.lives -= 1
                self.usage()

        print ('\n\n\tG A M E   O V E R\n\n')


    def get_bottom_toolbar_tokens (self, cli):
        last = ''
        if self.history and len (self.history.strings) > 0:
            last = self.history.strings[-1]

        return [(Token.Toolbar,
            '*** Lives: <{lives}> *** Loaded: {loaded} *** Enter "help" for help ***'.format (
                lives  = self.lives,
                loaded = ', '.join (sorted (self.loaded_from)) or '/dev/zero',
        ))]


    def printer (self, *kw):
        # note: invalid commands such as 'print stupsi' will
        # simply ignore the second word and do a 'print'
        if len (kw) == 1:
            arg = kw[0]
        else:
            arg = None

        if not self.fsm:
            print ('ERROR: Please load FSM\n')
            self.lives -= 1
            return

        if arg == 'fsm-ascii':
            try:
                graph (
                    fsm          = self.fsm,
                    source_files = sorted (self.loaded_from),
                    fmt          = 'ascii',
                )
            except Exception as e:
                print ('ERROR: {}'.format (e))

        elif arg == 'fsm-svg':
            try:
                graph (
                    fsm          = self.fsm,
                    source_files = sorted (self.loaded_from),
                    fmt          = 'svg',
                )
            except Exception as e:
                print ('ERROR: {}'.format (e))

        elif arg == 'fsm':
            print ()
            for state in self.fsm.workflow():
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

        else:
            if not self.issues:
                print ('ERROR: Please load issues\n')
                self.lives -= 1
                return

            print ()
            for state in self.fsm.workflow():
                print ('  (*) {name} {is_start}{is_end}'.format (
                    name = state.name,
                    is_start = ' (S)' if state.is_start else '',
                    is_end = ' (E)' if state.is_end else '',
                ))
                for issue in (i for i in self.issues if i.state == state.name):
                    print ('    (-) {}'.format (issue.title))

            print ()
            print ('(S) ... state is a start state')
            print ('(E) ... state is an end state')
            print ()


    def load (self, filename):
        if not filename or not os.path.isfile (filename):
            print ('ERROR: Please enter a valid filename\n')
            self.lives -= 1
            return

        try:
            loaded_ok = False

            with open (filename, 'r') as ymlfile:
                fsm, issues = None, None
                inputs = yaml.load (ymlfile)

                if type (inputs) != dict:
                    raise RuntimeWarning ('can\'t load data')

                if inputs.get ('issues'):
                    self.issues = [
                        Issue (
                            title = issue.get ('title'),
                            state = issue.get ('state'),
                        )
                        for issue in inputs.get ('issues')
                    ]
                    loaded_ok = True

                if inputs.get ('transitions'):
                    self.fsm = FSM (transitions = inputs.get ('transitions'))
                    loaded_ok = True

                if loaded_ok:
                    self.loaded_from.append (filename)
                else:
                    raise RuntimeWarning ('can\'t load data')

        except Exception as w:
            print ('ERROR: invalid data: <{}>\n'.format (w))
            self.lives -= 1


    def usage (self):
        # find the longest line for padding of right column
        max_len = (
            8
          + max ([len (c.get ('usage') or c.get ('command')) for c in self.commands])
          + max ([len (c.get ('description')) for c in self.commands])
        )

        usage = 'Available commands\n'
        usage += '\n'.join ([
            '  {command} {description:.>{padding}}'.format (
                padding     = max_len - len (c.get ('usage') or c.get ('command')),
                command     = c.get ('usage') or c.get ('command'),
                description = ' {}'.format (c.get ('description')),
            )
            for c in self.commands
        ])

        print ('\n{}\n'.format (usage))


    def clear (self):
        self.fsm = None
        self.issues = None
        self.loaded_from = []


    def shell (self, cmd):
        print (subprocess.run (
            cmd.split(),
            stdout = subprocess.PIPE,
        ).stdout.decode())


    def quit (self):
        exit()


    def oneup (self):
        self.lives += 1


if __name__ == '__main__':
    CLI().start()

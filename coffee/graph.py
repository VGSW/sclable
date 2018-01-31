from graphviz import Digraph
import tempfile
import subprocess

from coffee.coffee import FSM

def graph (**kwa):
    fsm  = kwa.get ('fsm')
    fmt  = kwa.get ('fmt')

    if fmt not in 'svg ascii'.split():
        raise RuntimeWarning ('invalid format: <{}>'.format (fmt))

    g = Digraph ('FSM', format  = 'svg')
    g.attr (rankdir = 'LR')

    for node in fsm.states:
        if node.is_start:
            g.node (node.name, label = node.name, shape = 'doublecircle')
        elif node.is_end:
            g.node (node.name, label = node.name)
        for edge in node.events:
            g.edge (node.name, edge.next_state.name)

    # how to overengineer: strategy pattern :-)
    if fmt == 'svg':
        g.render (view = True)
    elif fmt == 'ascii':
        g.render (view = False)
        print (subprocess.run (
            'graph-easy FSM.gv'.split(),
            stdout = subprocess.PIPE,
        ).stdout.decode())

from graphviz import Digraph
import tempfile

from coffee.coffee import FSM

def graph (**kwa):
    fsm  = kwa.get ('fsm')
    view = kwa.get ('view') or False

    g = Digraph ('FSM', format  = 'svg')
    g.attr (rankdir = 'LR')

    for node in fsm.states:
        if node.is_start:
            g.node (node.name, label = node.name, shape = 'doublecircle')
        elif node.is_end:
            g.node (node.name, label = node.name)
        for edge in node.events:
            g.edge (node.name, edge.next_state.name)

    g.render (view = view)

import unittest
import json
import yaml

from coffee.coffee import FSM, State

class Test_Coffee (unittest.TestCase):

    def test_fsm_01 (self):
        fsm = FSM (transitions = [
            { 'from' : 'to do', 'to' : 'doing' },
            { 'from' : 'to do', 'to' : 'on hold' },
        ])
        self.assertEqual (3, len (fsm.states))

        self.assertEqual (1, len ([s for s in fsm.states if s.name == 'to do']))
        self.assertEqual (1, len ([s for s in fsm.states if s.name == 'doing']))
        self.assertEqual (1, len ([s for s in fsm.states if s.name == 'on hold']))

        self.assertEqual (2, len ([s for s in fsm.states if s.name == 'to do'].pop().events))

        self.assertEqual ('to do', [s for s in fsm.states if s.is_start].pop().name)
        self.assertEqual (
            sorted (['doing', 'on hold']),
            sorted (s.name for s in [s for s in fsm.states if s.is_end])
        )

    def test_state_ordering_01 (self):
        fsm = FSM (transitions = [
            { 'from' : 'to do', 'to' : 'doing' },
            { 'from' : 'to do', 'to' : 'on hold' },
        ])

        self.assertEqual (
            [state.name for state in fsm.workflow()],
            [ 'to do',
              'doing',
              'on hold',
            ],
        )

    def test_state_ordering_02 (self):
        fsm = FSM (transitions = [
            { 'from' : 'to do',   'to' : 'doing' },
            { 'from' : 'to do',   'to' : 'on hold' },
            { 'from' : 'doing',   'to' : 'done' },
            { 'from' : 'doing',   'to' : 'failed' },
            { 'from' : 'doing',   'to' : 'on hold' },
            { 'from' : 'on hold', 'to' : 'doing' },
        ])

        self.assertEqual (
            [state.name for state in fsm.workflow()],
            [ 'to do',
              'doing',
              'done',
              'failed',
              'on hold',
            ],
        )

    def test_state_ordering_02 (self):
        # no (detectable) startstates
        with self.assertRaises (RuntimeWarning):
            FSM (transitions = [
                { 'from' : 'A', 'to' : 'B' },
                { 'from' : 'B', 'to' : 'C' },
                { 'from' : 'C', 'to' : 'A' },
            ])

    def test_state_ordering_021 (self):
        # missing end states
        with self.assertRaises (RuntimeWarning):
            FSM (transitions = [
                { 'from' : 'A', 'to' : 'B' },
                { 'from' : 'B', 'to' : 'C' },
                { 'from' : 'C', 'to' : 'B' },
            ])

    def test_state_ordering_03 (self):
        # multiple startstates
        with self.assertRaises (RuntimeWarning):
            FSM (transitions = [
                { 'from' : 'A', 'to' : 'B' },
                { 'from' : 'C', 'to' : 'B' },
            ])

    def test_state_ordering_04 (self):
        # multiple startstates
        with self.assertRaises (RuntimeWarning):
            FSM (transitions = [
                { 'from' : 'A', 'to' : 'B' },
                { 'from' : 'C', 'to' : 'D' },
            ])

    def test_state_ordering_05 (self):
        # multiple startstates
        with self.assertRaises (RuntimeWarning):
            FSM (transitions = [
                { 'from' : 'A', 'to' : 'B' },
                { 'from' : 'B', 'to' : 'A' },
            ])

    def test_state_ordering_06 (self):
        fsm = FSM (transitions = [
            { 'from' : 'A', 'to' : 'B' },
        ])

        self.assertEqual (2, len (fsm.states))
        self.assertEqual ('A', [s for s in fsm.states if s.is_start].pop().name)
        self.assertEqual ('B', [s for s in fsm.states if s.is_end].pop().name)

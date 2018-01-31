class Issue ():

    def __init__ (self, **kwa):
        self._title = kwa.get ('title')
        self._state = kwa.get ('state')

    def __repr__ (self):
        return 'Issue (title="{title}", state={state})'.format (
            title = self.title,
            state  = self.state,
        )

    @property
    def title (self):
        return self._title

    @title.setter
    def title (self, title):
        self._title = title

    @property
    def state (self):
        return self._state

    @state.setter
    def state (self, state):
        self._state = state


class Transition ():

    def __init__ (self, **kwa):
        self._frm = kwa.get ('frm')
        self._to = kwa.get ('to')
        self._input = kwa.get ('input')  # or None

    def __repr__ (self):
        return 'Transition (frm="{frm}", to="{to}")'.format (
            frm   = self.frm,
            to    = self.to,
        )

    @property
    def frm (self):
        return self._frm

    @frm.setter
    def frm (self, frm):
        self._frm = frm

    @property
    def to (self):
        return self._to

    @to.setter
    def to (self, to):
        self._to = to

    @property
    def none (self):
        return self._none

    @none.setter
    def none (self, none):
        self._none = none


class State ():

    def __init__ (self, **kwa):
        self._name     = kwa.get ('name')
        self._events   = kwa.get ('events') or []
        self._is_start = kwa.get ('is_start') or True
        self._is_end   = kwa.get ('is_end') or True

    def __repr__ (self):
        return 'State (name="{name}", events={events}, is_start={is_start}, is_end={is_end})'.format (
            name     = self.name,
            events   = self.events,
            is_start = self.is_start,
            is_end   = self.is_end,
        )

    @property
    def name (self):
        return self._name

    @name.setter
    def name (self, name):
        self._name = name

    @property
    def events (self):
        return self._events

    @events.setter
    def events (self, events):
        self._events = events

    def add_event (self, event):
        self._events.append (event)

    @property
    def is_start (self):
        return self._is_start

    @is_start.setter
    def is_start (self, is_start):
        self._is_start = is_start

    @property
    def is_end (self):
        return self._is_end

    @is_end.setter
    def is_end (self, is_end):
        self._is_end = is_end

class Event ():

    def __init__ (self, **kwa):
        self._enter = kwa.get ('enter')
        self._next_state = kwa.get ('next_state')

    def __repr__ (self):
        return 'Transition (enter="{enter}", next_state={next_state})'.format (
            enter      = self.enter,
            next_state = self.next_state,
        )

    @property
    def enter (self):
        return self._enter

    @enter.setter
    def enter (self, enter):
        self._enter = enter

    @property
    def next_state (self):
        return self._next_state

    @next_state.setter
    def next_state (self, next_state):
        self._next_state = next_state

class FSM ():

    def __init__ (self, **kwa):
        self._states = []
        self._start = []
        self._end = []

        self._build_fsm (transitions = [
            Transition (
                frm = t.get ('from'),
                to  = t.get('to'),
            )
            for t in kwa.get ('transitions')
        ])


    def known_state (self, state_name):
        # IN:  state-name
        # OUT: True if corresponding state exists
        #      False otherwise
        return any (s for s in self.states if s.name == state_name)

    def fetch_state (self, state_name):
        # IN:  state-name
        # OUT: corresponding, known state object
        if not self.known_state (state_name):
            raise LookupError ('can not fetch unknown state')

        return [s for s in self.states if s.name == state_name].pop()

    def create_or_fetch_state (self, state_name):
        return self.known_state (state_name) and self.fetch_state (state_name) or State (name = state_name)

    def fetch_start_state (self):
        # OUT: (first) start state, actually, only one start state is allowed
        # XXX run _check_fsm() here too ?
        return [s for s in self.states if s.is_start].pop()

    def _build_fsm (self, **kwa):
        """ build the FSM based on given transitions
            start/end states are detected. basically any new state
            is assumed to be both, being the source/destination of
            an transition invalidates the state as end/start state
            respectively. start and end states will remain (for
            valid inputs).
        """

        for t in kwa.get ('transitions'):
            to_state  = self.create_or_fetch_state (t.to)
            frm_state = self.create_or_fetch_state (t.frm)

            if not self.known_state (t.to):
                  self.states.append (to_state)

            if not self.known_state (t.frm):
                  self.states.append (frm_state)

            to_state.is_start = False
            frm_state.is_end = False

            frm_state.add_event (Event (
                enter = None,
                next_state = to_state,
            ))

        self._check_fsm ()

    def workflow (self):
        """ create and return a list representing the workflow
            based on state transitions. workflow is found depth-first
            and alphabetically for alternative paths
        """

        # ISA pure function
        def _wf (state, states = []):
            # keep this state
            states.append (state)

            # recursively process any yet unknown next_states
            for event in sorted (state.events, key = lambda e: e.next_state.name):
                if event.next_state not in states:
                    _wf (event.next_state, states)

            return states

        if not self.states:
            raise RuntimeWarning ('no states')

        self._check_fsm ()

        return _wf (self.fetch_start_state())


    @property
    def transitions (self):
        return self._transitions

    @transitions.setter
    def transitions (self, transitions):
        self._transitions = transitions

    @property
    def states (self):
        return self._states

    @states.setter
    def states (self, states):
        self._states = states

    def __repr__ (self):
        return "FSM (states={states}".format (
            states = self.states,
        )

    def _check_fsm (self):
        """ a valid FSM must have exactly one start state and
            one or more end states, YMMV
        """

        start_states = [s for s in self.states if s.is_start]
        end_states = [s for s in self.states if s.is_end]

        if len (start_states) == 0:
            raise RuntimeWarning ('missing start state')
        if len (start_states) > 1:
            raise RuntimeWarning ('multiple startstates')
        if len (end_states) == 0:
            raise RuntimeWarning ('missing end state')

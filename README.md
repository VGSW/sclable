# Scalable exercise "Group and sort by states"

*Due  to the  given  example  data only,  this  little  piece of  code,  quite
misleadingly, was titled "coffee"; I'm open to suggestions for a better name :-)*

### Runnin coffee

The easiest way to  run coffee is to build using  the Makefile. ```make build```
will bild a Docker  image and ```make run``` will run  an one-off container from
this image.

Doing it all in one step:

```
make clean test build run
```

Alternatively the command line interface  can be executed directly too:

```
python -m coffee.cli
```

### Notes on the implementation

Drawing an SVG of  the FSM (command ```print fsm-svg``` at  the CLI prompt) will
also try to  immediately open the created SVG file,  while ```print fsm-ascii```
will print  to the console.  Immediately opening an SVG  can only work  when run
locally  and not  inside of  a docker  container. (Dot  and SVG  output will  be
written to the files ```FSM.gv``` and ```FSM.gv.svg``` in any case.)

Based on the given  transitions internally an FSM (a graph)  is built. Start and
end states are  detected by initially assuming every new  state is actually both
(start and end state).

If a state is the source of the transition  it is based on, it can not be an end
state, if  it is the  destination it can  not be a  start state. Any  node never
entered through a transition will remain a start state, as will nodes never left
remain end states.

A valid FSM must have exactly one start state and one or more end states, YMMV.

Data must  be given  in YAML  files with  ```transitions``` and  ```issues``` as
top-level keys  which can  be given in  separate files or  combined in  a single
file. See the  supplied .yml files for examples (the  examples are also included
in the Docker image).

### A quick session could look like this

```
>> load fsm.yml
>> load issues1.yml
>> print
>> print fsm-ascii
```

:eyes: Use ```! ls``` to take a look around in the filesystem.

### The supplied YAML files
```
combined.yml ... Given example from the exercise description
fsm.ym ......... Given FSM
fsm01.yml ...... More elaborate FSM
issues1.yml .... Given set of issues
issues2.yml .... Alternate set of issues (issues in different states)
```

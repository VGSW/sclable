build:
	docker build --tag coffee .

run:
	docker run --rm -it coffee

test:
	nosetests coffee/tests/

clean:
	find . -name '__pycache__' | xargs rm -rf
	find . -name '*pyc' | xargs rm -f
	rm -f FSM.gv FSM.gv.svg

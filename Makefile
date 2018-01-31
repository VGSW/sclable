build:
	docker build --tag coffee .

run:
	docker run --rm -it coffee

test:
	nosetests coffee/tests/

clean:
	find . -name '__pycache__' -o -name '*pyc' | xargs rm -rf
	rm -f FSM.gv FSM.gv.svg

all:
	python -m twoc tests/for.c.py

wall:
	watchexec -cr "make all"

tests: FORCE
	clear
	python -m twoc tests/if.c.py
	python -m twoc tests/while.c.py
	python -m twoc tests/for.c.py
	python -m twoc tests/continue.c.py
	python -m twoc tests/array.c.py
	python -m twoc tests/class.c.py

wtests:
	watchexec -cr "make tests"

.PHONY: FORCE

FORCE:


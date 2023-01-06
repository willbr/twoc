all:
	python -m twoc tests\continue.c.py

wall:
	watchexec -cr "make all"


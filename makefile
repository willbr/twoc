all:
	python -m twoc tests\if.c.py

wall:
	watchexec -cr "make all"


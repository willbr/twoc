all:
	python -m twoc tests\for.c.py

wall:
	watchexec -cr "make all"


all:
	python -m twoc example.c.py

wall:
	watchexec -cr "make all"


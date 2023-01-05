all:
	python -m twoc tests\while.c.py

wall:
	watchexec -cr "make all"


include_lib("stdio.h")

define(false, 0)
define(true, not false)

def main():
    puts("hello")
    if true:
        while true:
            pass
        puts("true")
    else:
        puts("false")

    i:int = 10

    if i > 10:
        puts("big")
    elif i > 0:
        puts("small")
    elif i == 0:
        puts("zero")
    else:
        puts("negative")

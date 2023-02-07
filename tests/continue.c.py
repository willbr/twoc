include_lib("stdio.h")

def main():
    i:int = 0
    while 1:
        i += 1
        if i % 2 == 0:
            continue
        print("{i:d}")
        if i >= 10:
            break
    pass


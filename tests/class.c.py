include_lib("stdio.h")

class Point():
    x: int
    y: int

def main():
    a: Point = init_block(1, 2)
    println("Point({a.x:d}, {a.y:d})")


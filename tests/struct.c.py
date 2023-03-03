class Point:
    x: int
    y: int

def main():
    p: Point = init_block(1, 2)
    px: int = p.x
    py: int = p.y
    println("{px:d}, {py:d}")

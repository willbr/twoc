include_lib("stdio.h")

def main():
    a: array(10, char) = "hi"
    a[1] = char("o")
    println("{a:s}")

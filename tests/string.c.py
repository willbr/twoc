include_lib("stdio.h")

def main() -> int:
    name: tuple[char] = "will"
    name[0] = char('W')
    println("Hi {name:s}")
    return 0

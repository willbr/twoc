def test():
    f:pointer[FILE] = null
    c:char = char('h')
    pc:pointer[char] = addressof(c)
    puts("hi")
    d:char = contents(pc)
    println("{d:c}")

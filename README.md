# twoc

```python
include_lib("stdio.h")

def main() -> int:
    puts("hi")
    return 0
```

`python -m twoc example.c.py`

```c
#include <stdio.h>

int
main(void) {
    puts("hi");
    return 0;
}
```

run flag pipes the output to `tcc`

`python -m twoc -run example.c.py`

```
STDOUT:
hi
```

# tests

```
x while
x for
x continue
x break

x if
switch

print macro
struct
typedef
enum
cast to type
goto & labels
pointers
arrays
unions

```

# repl

add dependancy graph
server + client

# areans

# python types

* dict
* list
* set

# default argument values

# python match
# python class
# python with statement

# store compiler settings inside the file

link settings saved in file e.g. SDL

# silly ideas

https://en.wikipedia.org/wiki/Swizzling_(computer_graphics)

swizzle rgb bgr like Odin?

# Uniform Function Call Syntax

https://en.wikipedia.org/wiki/Uniform_Function_Call_Syntax

```python
c = add(a, b)
c = a.add(b)
```

```c
c = add(a, b)
c = add(a, b)
```
# Member functions

```python
a:int = 0
a.print()
```

```c
int a = 0;
int__print(&a)
```


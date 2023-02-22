# twoc

a silly toy to compile python to c

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

## tests

```
x while
x for
x continue
x break

x if
switch

print macro
struct/union, inherit from Struct or Union like ctypes
typedef
enum
cast to type
goto & labels
pointers
arrays
unions

```

## python syntax

```
in
match
class
with
is

ctypes
i = 42
a = pointer(i)
print(a.contents) deref
addressof(i) or i.addressof
byref
cast(obj, type)
```

## python types

* dict
* list
* set
* interned strings

# threec

twoc is simple and ignorant

threec will track contents and scope

play with silly hacky ideas

## repl

add dependancy graph
server + client

## areans

## fat arrays
data, cap, len

## default argument values

## store compiler settings inside the file

link settings saved in file e.g. SDL

## silly ideas

[wikipedia swizzling](https://en.wikipedia.org/wiki/Swizzling_(computer_graphics))

swizzle rgb bgr like Odin?

## Member functions

```python
a:int = 0
a.print()
```

```c
int a = 0;
int__print(&a)
```

## inver variable type on first use

```python
a = 128
```

```c
int a = 128;
```


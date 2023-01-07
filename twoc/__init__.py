from rich.console import Console
from rich.traceback import install
from .compiler import CompilationUnit

"""
remove split_newline
remove references to ie/
can I remove transform_infix
remove keywords?
"""

install(show_locals=True)

console = Console(markup=False)
python_print = print
print = console.print

#here = Path(__file__).parent
#print('here', here)

def compile_comment(comment):
    r = f'/* {comment[1:-1]} */'
    return r


def compile_returns(spec):
    assert spec[1] == 'ie/newline'
    assert len(spec) == 2
    return spec[0]


def compile_var(args, body):
    assert body == []
    num_args = len(args)
    if num_args == 2:
        var_name, var_type = args
        return f"{var_type} {var_name}"
    elif num_args == 3:
        var_name, var_type, var_val = args
        return f"{var_type} {var_name} = {var_val}"
    else:
        assert False


def split_on_symbol(lst, s):
    r = [[]]
    for e in lst:
        if e == s:
            r.append([])
        else:
            r[-1].append(e)
    return r


def transform_infix(x):
    if ',' in x:
        sections = split_on_symbol(x, ',')
    else:
        sections = [x]

    transformed_sections = []
    for section in sections:
        n = len(section)

        if n == 0:
            transformed_sections.append(section)
            continue
        elif n == 1:
            transformed_sections.append(section[0])
            continue
        elif (n % 2) == 0:
            print(x)
            assert False

        first_arg, first_op, *rest = x
        xx = [first_op, first_arg]
        for i in range(2, len(x)):
            if i % 2:
                assert first_op == x[i]
            else:
                xx.append(x[i])
        return xx

    n = len(transformed_sections)

    if n == 0:
        assert False
    elif n == 1:
        return transformed_sections[0]
    else:
        return transformed_sections


def is_string_literal(s):
    if len(s) < 2:
        return False
    return s[0] == '"' and s[-1] == '"'


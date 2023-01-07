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


def is_string_literal(s):
    if len(s) < 2:
        return False
    return s[0] == '"' and s[-1] == '"'


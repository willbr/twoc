from unwind import unwind_file
from pathlib import Path
from .rope import Rope

class CompilationUnit():
    def __init__(self, filename=None):
        self.structs = {}
        self.functions = {}
        self.global_vars = {}
        self.top_level = []
        self.keywords = []
        self.infix_symbols = """
        = == !=
        + += - -= * *= / /=
        % %=
        > >= < <=
        && ||
        and or
        & &= | |= ^ ^=
        << <<= >> >>=
        """.split()
        self.filenames = []
        self.lib_directories = []

        #libs_dir = here.joinpath('../libs')

        self.lib_directories.append(Path.cwd())
        #self.lib_directories.append(libs_dir)

        if filename:
            self.read_file(filename)


    def read_file(self, filename):
        self.filenames.append(filename)
        prog = unwind_file(filename)

        x = prog.pop(0)
        assert x == 'module'

        for x in prog:
            head, *args = x
            if head in ['def', 'func-decl']:
                self.compile_func_decl(*args)

        for x in prog:
            # puts_expr(x)
            self.compile(x)

        if self.keywords:
            self.compile_keywords()


    def compile_keywords(self):
        escaped_keywords = ('keyword_' + x for x in self.keywords)
        body = ([kw, 'ie/newline'] for kw in escaped_keywords)
        x = ('enum', 'toco_keyword', 'ie/newline', *body)
        self.compile(x)

        x = "typedef toco_keyword enum toco_keyword".split()
        self.compile(x)


    def compile(self, x):
        if is_atom(x):
            if x == 'ie/newline':
                try:
                    prev = self.top_level[-1]
                except IndexError:
                    prev = ''

                if prev != '':
                    self.top_level.append('')
            else:
                assert False
            return

        head, *args = x

        if head == 'def':
            self.compile_proc(*args)
        elif head == 'func_decl':
            self.compile_func_decl(*args)
        elif head == 'include_lib':
            self.top_level.append(self.compile_lib(*args))
        elif head == 'import':
            self.compile_import(*args)
        elif head == 'struct':
            self.compile_struct(*args)
        elif head == 'globals':
            self.compile_globals(args)
        elif head == 'typedef':
            self.compile_typedef(*args)
        elif head == 'define':
            self.compile_define(*args)
        elif head == 'hash_if':
            cx = self.compile_hash_if(*args)
            self.top_level.extend(cx)
        elif head == 'comment':
            self.top_level.append(compile_comment(*args))
        elif head == 'enum':
            self.top_level.append(self.compile_enum(*args))
        elif head == 'ie/newline':
            assert args == []
        else:
            print(head)
            assert False


    def compile_func_decl(self, fn_name, params, returns, body):
        self.functions[fn_name] = [params, returns, body]


    def compile_lib(self, name):
        cname = name.strip('"')
        clib = f"#include <{cname}>"
        return clib


    def compile_import(self, lib_name, *body):
        filenames = [lib_name, lib_name + '.h.ie', lib_name + '.c.ie']
        assert body == ('ie/newline',)
        for lib_dir in self.lib_directories:
            for name in filenames:
                path = os.path.join(lib_dir, name)
                # print(path)
                if os.path.exists(path):
                    self.read_file(path)
                    return
        assert False


    def compile_proc(self, fn_name, params, returns, body):
        cbody = [self.compile_statement(x) for x in body]
        self.functions[fn_name] = [params, returns, cbody]


    def compile_statement(self, x):
        #print(x)

        if is_atom(x):
            if isinstance(x, str) and x[0] == '"':
                return compile_comment(x)
            else:
                assert False

        head, *args = x

        if head == 'while':
            return self.compile_while(*args)
        elif head == 'for':
            return self.compile_for(*args)
        elif head == 'cond':
            return self.compile_cond(*args)
        elif head == 'comment':
            return compile_comment(*args, *body)
        elif head == 'return':
            return self.compile_return_statement(*args, *body)
        elif head == 'assign':
            ce = self.compile_expression(['=', *args]) + ';'
            return ce
        elif head == 'ann_assign':
            return self.compile_var(*args) + ";"

        ce = self.compile_expression([head, *args])
        if head in ['include-lib']:
            return ce
        else:
            return ce + ";"


    def compile_var(self, var_name, var_type, var_value):
        assert is_atom(var_name)
        xtype = self.macro_expand(var_type)
        decl = self.compile_var_decl(var_name, xtype, var_value)
        return decl


    def compile_while(self, pred, body):
        cpred = self.compile_expression(pred)
        cbody = [self.compile_statement(s) for s in body]
        return f"while ({cpred})", cbody


    def compile_for(self, target, iter, body, orelse):
        assert orelse == []

        if is_atom(target):
            match iter:
                case ['range', stop]:
                    init = ['=', target, 0]
                    pred = ['<', target, stop]
                    step = ['+=', target, 1]
                case ['range', start, stop]:
                    init = ['=', target, start]
                    pred = ['<', target, stop]
                    step = ['+=', target, 1]
                case ['range', start, stop, step]:
                    init = ['=', target, start]
                    pred = ['<', target, stop]
                    assert step != 0
                    if step > 0:
                        step = ['+=', target, step]
                    else:
                        step = ['-=', target, abs(step)]
                case _:
                    assert False
        else:
            assert False


        cinit = self.compile_expression(init)
        cpred = self.compile_expression(pred)
        cstep = self.compile_expression(step)

        cbody = [self.compile_statement(s) for s in body]
        return f"for ({cinit}; {cpred}; {cstep})", cbody


    def compile_typedef(self, type_name, *body):
        assert False
        type_spec, rest = split_newline(body)
        assert rest == ()
        decl = "typedef " + self.compile_var_decl(type_name, type_spec) + ";"
        self.top_level.append(decl)


    def compile_struct(self, struct_name, *body):
        assert body[0] == 'ie/newline'
        assert len(body) > 1
        struct_spec = {}
        for member_spec in body[1:]:
            member_name, member_type, nl = member_spec
            assert nl == 'ie/newline'
            struct_spec[member_name] = member_type
        self.structs[struct_name] = struct_spec

        struct_decl = [f"struct {struct_name} {{"]
        for member_name, member_type in struct_spec.items():
            decl = self.compile_var_decl(member_name, member_type)
            struct_decl.append(f"    {decl};")
        struct_decl.append("};")
        self.top_level.append('\n'.join(struct_decl))


    def compile_globals(self, body):
        assert body[0] == 'ie/newline'
        body.pop(0)
        for elem in body:
            assert len(elem) == 4
            var_name, let, x, nl = elem
            var_name = self.mangle(var_name)
            assert let == ':='
            assert nl == 'ie/newline'
            neoteric, var_type, var_initial = x
            assert neoteric == 'ie/neoteric'
            # print(var_initial)
            # print(x)
            decl = self.compile_var_decl(var_name, var_type, var_initial)
            # print(decl)
            # print()
            self.global_vars[var_name] = decl
            self.top_level.append(decl + ";")


    def compile_define(self, name, body):
        cbody = self.compile_expression(body)
        decl = f"#define {name} {cbody}"
        self.top_level.append(decl)


    def compile_hash_if(self, *args):
        assert False
        lines = []
        pred, body = split_newline(args)
        #cpred = self.compile_expression(transform_infix(pred))
        cbody = [self.compile_statement(s) for s in body]

        lines.append(f"#if {cpred}")
        for s in body:
            x = self.compile_statement(s)
            lines.append(f"    {x}")
        lines.append("#endif")
        return lines


    def compile_cond(self, head, *clauses):
        pred, body = head
        cpred = self.compile_expression(pred)
        cbody = [self.compile_statement(s) for s in body]

        blocks = [cbody]

        for clause in clauses:
            clause_pred, clause_body = clause
            c_clause_pred = self.compile_expression(clause_pred)
            c_clause_body = [self.compile_statement(s) for s in clause_body]

            if c_clause_pred == 'else':
                s_pred = 'else'
            else:
                s_pred = f"else if ({c_clause_pred})"

            blocks.append([s_pred, c_clause_body])

        return f"if ({cpred})", *blocks


    def compile_enum(self, *args):
        first_line, enum_body = split_newline(args)
        assert len(first_line) == 1
        name = first_line[0]
        enum = []
        for x in enum_body:
            line, body = split_newline(x)
            assert len(line) == 1
            assert body == []
            enum.append(line[0])
        s = [f"enum {name} {{"]
        s.append(',\n'.join(f"    {x}" for x in enum))
        s.append('};')
        return '\n'.join(s)


    def compile_return_statement(self, *args):
        assert False
        return c


    def compile_print_macro(self, *args):
        assert len(args) == 1
        print_args = self.parse_format_string(args[0])
        return ['printf', *print_args]


    def compile_println_macro(self, *args):
        assert len(args) == 1
        print_args = self.parse_format_string(args[0], True)
        return ['printf', *print_args]


    def compile_fprint_macro(self, *args):
        file, fmt = args
        print_args = self.parse_format_string(fmt)
        print_args.insert(0, file)
        return ['printf', *print_args]


    def compile_fprintln_macro(self, *args):
        file, fmt = args
        print_args = self.parse_format_string(fmt, True)
        print_args.insert(0, file)
        return ['printf', *print_args]

    def compile_compare_macro(self, left, ops, comparators):
        if len(ops) == 1:
            r = [ops[0], left, comparators[0]]
            return r
        assert False

    def compile_aug_assign_macro(self, target, op, value):
        if op == '+':
            r = ['+=', target, value]
        else:
            assert False
        return r

    
    def parse_format_string(self, fmt, append_newline=False):
        assert fmt[0] == '"' and fmt[-1] == '"'
        fmt = fmt[1:-1]

        lhs, rhs = fmt.split("{",1)
        template = [lhs]
        vargs = []
        while rhs:
            try:
                lhs, rhs = rhs.split("{",1)
            except ValueError:
                lhs, rhs = rhs, ''
            a, text = lhs.split("}")
            t, fmt = a.rsplit(" ", 1)
            vargs.append(t)

            if fmt[0] == '=':
                template.append(f"{v}=")
                fmt = fmt[1:]

            template.append('%' + fmt)
            template.append(text)

        if append_newline:
            template.append('\\n')

        printf_format = '"' + ''.join(template) + '"'

        return [printf_format, *vargs]


    def macro_expand(self, x):
        if is_atom(x):
            return x

        if x == []:
            return []
        elif x == ['ie/infix']:
            return []

        head, *rest = x

        if head == 'print':
            return self.compile_print_macro(*rest)
        elif head == 'println':
            return self.compile_println_macro(*rest)
        elif head == 'fprint':
            return self.compile_fprint_macro(*rest)
        elif head == 'fprintln':
            return self.compile_fprintln_macro(*rest)
        elif head == 'compare':
            return self.compile_compare_macro(*rest)
        elif head == 'aug_assign':
            return self.compile_aug_assign_macro(*rest)

        while head in ['ie/prefix', 'ie/infix', 'ie/postfix', 'ie/neoteric']:
            if head == 'ie/prefix':
                head, *rest = rest
            elif head == 'ie/infix':
                assert False
                #nx = transform_infix(rest)
                if is_atom(nx):
                    return self.mangle(nx)
                head, *rest = nx
                if rest == []:
                    return head
            elif head == 'ie/postfix':
                head = rest[-1]
                rest = rest[:-1]
            elif head == 'ie/neoteric':
                assert len(rest) == 2
                cmd, args = rest

                if cmd == '*':
                    cmd = 'deref'

                if args[0] == 'ie/prefix':
                    aname = rest[0]
                    assert False
                    #index = transform_infix(rest[1][1:])
                    head, *rest = ['aref', aname, index]
                elif args[0] == 'ie/infix':
                    # print(1,[head, *rest])
                    nargs = self.macro_expand(args)
                    # print(2,nargs)
                    if ',' in args:
                        head, *rest = [cmd, *nargs]
                    else:
                        head, *rest = [cmd, nargs]

                    # if len(args) == 2:
                        # head, *rest = [cmd, nargs]
                    # else:
                        # head, *rest = [cmd, *nargs]
                    # print(3,[head, *rest])
                    # exit(1)
                elif args[0] == 'ie/postfix':
                    assert False
                else:
                    assert False
                # print(x)
                # print([head, *rest])
                # exit(1)

        nx = [head, *rest]
        # print("x:", x)
        # print("nx:", nx)
        return nx


    def compile_expression(self, x, depth=0):
        #print(f"{x=}")
        nx = self.macro_expand(x)
        # print(f"{nx=}")
        # print()

        if is_atom(nx):
            return self.mangle(nx)

        if nx == []:
            return ''

        # print(x)
        head, *rest = nx

        if head == 'compare':
            return self.compile_compare(*rest)
        elif head in ['break', 'continue']:
            assert rest == []
            return head

        cargs = [self.compile_expression(a, depth+1) for a in rest]

        if head in self.infix_symbols:
            # print(head, cargs)
            mhead = self.mangle(head)
            r =  f" {mhead} ".join(cargs)
            if depth:
                return "(" + r + ")"
            else:
                return r
        elif head == "inc":
            assert len(cargs) == 1
            return f"{cargs[0]} += 1"
        elif head == 'aref':
            if len(cargs) != 2:
                raise ValueError(f"{head=} {cargs=}")
            aname, aindex = cargs
            if is_atom(args[0]):
                return f"{aname}[{aindex}]"
            else:
                return f"({aname})[{aindex}]"
        elif head == 'deref':
            assert len(cargs) == 1
            target = cargs[0]
            if is_atom(target):
                return f"*{target}"
            else:
                return f"*({target})"
        elif head == "include-lib":
            return self.compile_lib(*args)
        elif head == 'not':
            assert len(cargs) == 1
            return f"!{cargs[0]}"
        else:
            return f"{head}({', '.join(cargs)})"


    def compile_params(self, spec):
        if spec[0] == 'ie/newline':
            spec = spec[1:]

        params = []
        for param in spec:
            n = len(param)
            if len(param) == 3:
                assert param.pop() == 'ie/newline'

            if n == 1:
                if param[0] == 'void':
                    params.append('void')
                else:
                    print(param)
                    assert False
            else:
                var_name, var_type = param
                params.append(self.compile_var_decl(var_name, var_type))
        return params


    def compile_var_decl(self, var_name, var_type, initial_value=None):
        is_struct = var_type == 'struct'

        if is_struct:
            if is_atom(initial_value):
                assert False
            head, *rest = initial_value
            assert False
            #iv = transform_infix(rest)
            struct_name, *struct_values = iv
            var_type += f" {struct_name}"

        lhs = ""
        rhs = ""

        if is_atom(var_type):
            while var_type[0] == '*':
                lhs = "*" + lhs
                var_type = var_type[1:]
        elif var_type[0] == 'array':
            _, alen, atype = var_type
            rhs = f"[{alen}]"
            var_type = atype
        else:
            var_type = ' '.join(var_type)

        decl = f"{var_type} {lhs}{var_name}{rhs}"

        if is_struct and initial_value:
            decl += " = {" + ', '.join(map(str, struct_values)) + "}"
        elif initial_value != None:
            ce = self.compile_expression(initial_value)
            decl += f" = {ce}"

        return decl


    def mangle(self, name):
        #print(f"{name=}")
        t = type(name)

        if t == bool:
            return str(name).lower()
        elif t != str:
            return str(name)

        if name == '':
            return ''
        elif name == '-':
            return '-'
        elif name == 'null':
            return 'NULL'
        elif name == 'and':
            return '&&'
        elif name == 'or':
            return '||'
        elif name[0] == '"':
            x = name.replace('\n', '\\n')
            return x
        elif name in self.infix_symbols:
            return name

        x = name
        if x[0] == ':':
            keyword = x[1:]
            if keyword not in self.keywords:
                self.keywords.append(keyword)
            x = 'keyword_' + keyword
        return x


    def render(self):
        lines = Rope()

        for e in self.top_level:
            lines.write_line(e)

        if self.top_level and self.top_level[-1] != '':
            lines.write_line("")

        func_decls = 0
        for name, spec in self.functions.items():
            if name == 'main':
                continue
            params, returns, body = spec
            if body == ():
                continue
            print_func_decl(lines, name, params, returns, ' ', ';')
            lines.write_line("")

            func_decls += 1

        if func_decls:
            lines.write_line("")

        if lines.last_line_isnt_empty():
            lines.write_line("")

        sep = None
        for name, spec in self.functions.items():
            params, returns, body = spec
            if body == ():
                continue
            if sep != None:
                lines.write_line(sep)
            print_func_decl(lines, name, params, returns, '\n', ' ')

            print_block(lines, body, 1)
            lines.write_line("")

            sep = ""

        return lines.render()


    def print(self):
        print(self.render())


def print_block(lines: Rope, body, depth: int) -> None:
    indent = "    " * depth

    lines.write_line("{")

    for s in body:
        if s != '':
            lines.write(indent)

        if isinstance(s, str):
            lines.write_line(s)
        else:
            head, sub, *chain = s
            lines.write(head + " ")
            print_block(lines, sub, depth+1)
            print_chain(lines, chain, depth)
            lines.write_line("")

    indent = "    " * (depth-1)
    lines.write(indent + "}")


def print_chain(lines: Rope, chain, depth: int) -> None:
    for link in chain:
        head, sub, *sub_chain = link
        lines.write(f" {head} ")
        print_block(lines, sub, depth+1)
        print_chain(lines, sub_chain, depth)


def is_atom(x):
    if type(x) is str:
        return True
    return not hasattr(x, '__iter__')

def print_func_decl(lines, name, params, returns, sep, end):
    if params:
        cparams = ', '.join(params)
    else:
        cparams = 'void'
    creturns = 'void' if returns == None else returns
    code = f"{creturns}{sep}{name}({cparams}){end}"
    *body, final = code.split('\n')

    for l in body:
        lines.write_line(l)

    lines.write(final)



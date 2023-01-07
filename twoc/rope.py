class Rope():
    def __init__(self):
        self.lines = [[]]
        pass

    def write(self, s):
        self.lines[-1].append(s)

    def write_line(self, line=""):
        self.lines[-1].append(line)
        self.lines.append([])

    def last_line(self):
        return ''.join(self.lines[-1])

    def last_line_isnt_empty(self):
        return self.last_line() != ''

    def render(self):
        return '\n'.join(''.join(line) for line in self.lines)


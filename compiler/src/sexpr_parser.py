NestedStringList = list["NestedStringList"] | str


class Parser:
    def __init__(self, sexpr: str):
        self.sexpr: str = sexpr
        self.index: int = 0

    def peek(self):
        if self.index >= len(self.sexpr):
            raise Exception("Invalid Peek")
        return self.sexpr[self.index]

    def consume(self):
        if self.index >= len(self.sexpr):
            raise Exception("Invalid Consume")
        self.index += 1

    def parse(self):
        c = self.peek()
        if c == "(":
            return self.parse_list()
        return self.parse_atom()

    def parse_list(self):
        ls: list[NestedStringList] = []
        c = self.peek()
        if c != "(":
            raise Exception("Expected an Opening Bracket")
        self.consume()
        c = self.peek()
        if c == ")":
            self.consume()
            return ls
        while True:
            c = self.peek()
            if c != "(" and not self.isAtom(c):
                raise Exception("Expected a List Or an Atom")

            if c == "(":
                next = self.parse_list()
                ls.append(next)
            if self.isAtom(c):
                next = self.parse_atom()
                ls.append(next)
            cc = self.peek()
            if cc != ")" and cc != " ":
                raise Exception("Expected a White Space Or a Closing Bracket")
            self.consume()
            if cc == ")":
                break

        return ls

    def parse_atom(self):
        c = self.peek()
        if not self.isAtom(c):
            raise Exception("Expected an Atom")
        self.consume()
        return c

    @staticmethod
    def isAtom(c: str):
        if (c < "0" or c > "9") and (c < "a" or c > "z"):
            return False
        return True

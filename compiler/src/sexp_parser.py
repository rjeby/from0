class Parser:
    def __init__(self, sexpr: str):
        self.sexpr: str = sexpr
        self.index: int = 0

    def peek(self):
        if self.index >= len(self.sexpr):
            raise Exception("Invalid SEXPR")
        return self.sexpr[self.index]

    def consume(self):
        if self.index >= len(self.sexpr):
            raise Exception("Invalid SEXPR")
        self.index += 1

    def hasReachedEOF(self):
        return self.index == len(self.sexpr)

    def parse(self):
        sexp = self.parse_exp()
        if not self.hasReachedEOF():
            raise Exception("Invalid SEXPR")
        return sexp

    def parse_exp(self) -> str:
        c = self.peek()
        if c == "(":
            return self.parse_list()
        return self.parse_atom()

    def parse_list(self):
        c = self.peek()
        if not c == "(":
            raise Exception("Invalid SEXPR")
        self.consume()
        self.parse_ws()
        op = self.parse_operator()
        self.parse_ws()
        lf = self.parse_exp()
        self.parse_ws()
        rg = self.parse_exp()
        self.parse_ws()
        c = self.peek()
        if not c == ")":
            raise Exception("Invalid SEXPR")
        self.consume()
        return f"[{op}, {lf}, {rg}]"

    def parse_atom(self):
        c = self.peek()
        if self.isALPHA(c):
            return self.parse_symbol()
        if self.isDEQUOTE(c):
            return self.parse_string()
        if c == "-" or self.isDIGIT(c):
            return self.parse_number()
        raise Exception("Invalid SEXPR")

    def parse_symbol(self):
        symbol: list[str] = ['"']
        c = self.peek()
        if not self.isALPHA(c):
            raise Exception("Invalid SEXPR")
        symbol.append(c)
        self.consume()
        while not self.hasReachedEOF():
            c = self.peek()
            if self.isALPHA(c) or self.isDIGIT(c) or c == "-" or c == "_":
                symbol.append(c)
                self.consume()
            else:
                symbol.append('"')
                return "".join(symbol)
        symbol.append('"')
        return "".join(symbol)

    def parse_number(self):
        number: list[str] = ['"']
        c = self.peek()
        if c == "-":
            number.append("-")
            self.consume()
            c = self.peek()

        if not self.isDIGIT(c):
            raise Exception("Invalid SEXPR")
        number.append(c)
        self.consume()
        while not self.hasReachedEOF():
            c = self.peek()
            if not self.isDIGIT(c):
                number.append('"')
                return "".join(number)
            number.append(c)
            self.consume()
        number.append('"')
        return "".join(number)

    def parse_string(self):
        string: list[str] = []
        c = self.peek()
        if not self.isDEQUOTE(c):
            raise Exception("Invalid SEXPR")
        string.append(c)
        self.consume()
        while not self.hasReachedEOF():
            c = self.peek()
            if c != " " and c != "!" and (c < "#" or c > "~"):
                break
            string.append(c)
            self.consume()
        if self.hasReachedEOF():
            raise Exception("Invalid SEXPR")
        c = self.peek()
        if not self.isDEQUOTE(c):
            raise Exception("Invalid SEXPR")
        string.append(c)
        self.consume()
        return "".join(string)

    def parse_ws(self):
        while not self.hasReachedEOF():
            c = self.peek()
            if (
                not self.isSP(c)
                and not self.isHTAB(c)
                and not self.isCR(c)
                and not self.isLF(c)
            ):
                return
            self.consume()

    def parse_operator(self):
        c = self.peek()
        if c != "+" and c != "-" and c != "*" and c != "/":
            raise Exception("Invalid SEXPR")
        self.consume()
        return f'"{c}"'

    @staticmethod
    def isAtom(c: str):
        if (c < "0" or c > "9") and (c < "a" or c > "z"):
            return False
        return True

    @staticmethod
    def isALPHA(c: str):
        return (c >= "a" and c <= "z") or (c >= "A" and c <= "Z")

    @staticmethod
    def isDIGIT(c: str):
        return c >= "0" and c <= "9"

    @staticmethod
    def isSP(c: str):
        return c == " "

    @staticmethod
    def isHTAB(c: str):
        return c == "\t"

    @staticmethod
    def isCR(c: str):
        return c == "\r"

    @staticmethod
    def isLF(c: str):
        return c == "\n"

    @staticmethod
    def isDEQUOTE(c: str):
        return c == '"'

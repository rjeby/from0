atom_type = str | list[int | str]
sexp_type = atom_type | list["sexp_type"]


class Parser:
    def __init__(self, sexpr: str):
        self.sexpr: str = sexpr
        self.index: int = 0

    def peek(self):
        if self.index >= len(self.sexpr):
            return None
        return self.sexpr[self.index]

    def consume(self):
        self.index += 1

    def parse(self):
        sexp: sexp_type = self.parse_exp()
        if self.peek():
            raise Exception("Invalid EOF")
        return sexp

    def parse_exp(self) -> sexp_type:
        c = self.peek()
        if not c or (
            c != "("
            and not self.is_DEQUOTE(c)
            and not self.is_DIGIT(c)
            and not self.is_ALPHA(c)
        ):
            raise Exception("Invalid EXP")
        if c == "(":
            return self.parse_list()
        return self.parse_atom()

    def parse_list(self):
        ls: list[sexp_type] = []
        c = self.peek()
        if not c or c != "(":
            raise Exception("Invalid List")
        self.consume()
        self.parse_ws()
        c = self.peek()
        if c and (
            c == "(" or self.is_DEQUOTE(c) or self.is_DIGIT(c) or self.is_ALPHA(c)
        ):
            exp = self.parse_exp()
            ls.append(exp)
            self.parse_ws()
            while self.peek():
                c = self.peek()
                assert c is not None
                if (
                    c == "("
                    or self.is_DEQUOTE(c)
                    or self.is_DIGIT(c)
                    or self.is_ALPHA(c)
                ):
                    exp = self.parse_exp()
                    ls.append(exp)
                    self.parse_ws()
                else:
                    break
        c = self.peek()
        if not c or c != ")":
            raise Exception("Invalid List")
        self.consume()
        return ls

    def parse_atom(self):
        c = self.peek()
        if not c or (
            not self.is_DEQUOTE(c) and not self.is_DIGIT(c) and not self.is_ALPHA(c)
        ):
            raise Exception("Invalid ATOM")
        if self.is_DEQUOTE(c):
            return self.parse_string()
        if self.is_DIGIT(c):
            return self.parse_number()
        return self.parse_symbol()

    def parse_symbol(self):
        symbol: list[str] = []
        c = self.peek()
        if not c or not self.is_ALPHA(c):
            raise Exception("Invalid SEXPR")
        symbol.append(c)
        self.consume()
        while self.peek():
            c = self.peek()
            assert c is not None
            if self.is_ALPHA(c) or self.is_DIGIT(c) or c == "-" or c == "_":
                symbol.append(c)
                self.consume()
            else:
                return "".join(symbol)
        return "".join(symbol)

    def parse_number(self) -> list[str | int]:
        c = self.peek()
        if not c or not self.is_DIGIT(c):
            raise Exception("Invalid SEXPR")
        number = int(c)
        self.consume()
        while self.peek():
            c = self.peek()
            assert c is not None
            if not self.is_DIGIT(c):
                return ["val", number]
            number = (number * 10) + int(c)
            self.consume()
        return ["val", number]

    def parse_string(self):
        string: list[str] = []
        c = self.peek()
        if not c or not self.is_DEQUOTE(c):
            raise Exception("Invalid SEXPR")
        string.append(c)
        self.consume()
        while self.peek():
            c = self.peek()
            assert c is not None
            if c != " " and c != "!" and (c < "#" or c > "~"):
                break
            string.append(c)
            self.consume()

        c = self.peek()
        if not c or not self.is_DEQUOTE(c):
            raise Exception("Invalid SEXPR")
        string.append(c)
        self.consume()
        return "".join(string)

    def parse_ws(self):
        while self.peek():
            c = self.peek()
            assert c is not None
            if (
                not self.is_SP(c)
                and not self.is_HTAB(c)
                and not self.is_CR(c)
                and not self.is_LF(c)
            ):
                return
            self.consume()

    @staticmethod
    def is_Atom(c: str):
        if (c < "0" or c > "9") and (c < "a" or c > "z"):
            return False
        return True

    @staticmethod
    def is_ALPHA(c: str):
        return (c >= "a" and c <= "z") or (c >= "A" and c <= "Z")

    @staticmethod
    def is_DIGIT(c: str):
        return c >= "0" and c <= "9"

    @staticmethod
    def is_SP(c: str):
        return c == " "

    @staticmethod
    def is_HTAB(c: str):
        return c == "\t"

    @staticmethod
    def is_CR(c: str):
        return c == "\r"

    @staticmethod
    def is_LF(c: str):
        return c == "\n"

    @staticmethod
    def is_DEQUOTE(c: str):
        return c == '"'

import sys
import locale
from src.plox.lexer import Lexer
from src.plox.parser import Parser
from src.plox.error import PloxError


class Plox:
    @staticmethod
    def run(code: str):
        try:
            tokens = Lexer(code).tokenize()
            parser = Parser(tokens)
            statements = parser.parse()
            for statement in statements:
                statement.resolve()
            for statement in statements:
                statement.execute()
        except Exception as e:
            print(e, file=sys.stderr)

    @staticmethod
    def run_script(path: str):
        system_encoding = locale.getpreferredencoding(False)
        with open(path, "r", encoding=system_encoding) as f:
            data = f.read()
            Plox.run(data)
        if PloxError.hadError:
            sys.exit(65)
        if PloxError.hadRuntimeError:
            sys.exit(70)

    @staticmethod
    def run_prompt():
        print('Welcome to Plox Interpreter (Type "exit" to exit):')
        reader = sys.stdin
        while True:
            print("> ", end="", flush=True)
            data = reader.readline()
            if data == "":
                print("")
                break
            Plox.run(data)

    @staticmethod
    def main():
        try:
            if len(sys.argv) > 2:
                print("Usage: jlox [script]")
                sys.exit(64)
            elif len(sys.argv) == 2:
                Plox.run_script(sys.argv[1])
            else:
                Plox.run_prompt()
        except Exception as e:
            print(e, file=sys.stderr)


if __name__ == "__main__":
    Plox.main()

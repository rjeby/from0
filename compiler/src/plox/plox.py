import sys
import locale


class Plox:

    hadError = False

    @staticmethod
    def run(code: str):
        return

    @staticmethod
    def run_script(path: str):
        system_encoding = locale.getpreferredencoding(False)
        with open(path, "rb", encoding=system_encoding) as f:
            data = f.read()
            Plox.run(data)
        if Plox.hadError:
            sys.exit(65)

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
    def report(line: int, message: str):
        print(f"[Line {line}] Error : {message}")

    @staticmethod
    def error(line: int, message: str):
        Plox.hadError = True
        Plox.report(line, message)

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

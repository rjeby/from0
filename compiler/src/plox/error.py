class PloxError:
    hadError = False

    @staticmethod
    def report(line: int, message: str):
        print(f"[Line {line}] Error : {message}")

    @staticmethod
    def error(line: int, message: str):
        PloxError.hadError = True
        PloxError.report(line, message)

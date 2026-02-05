import sys
import locale


def run_script(path: str):
    system_encoding = locale.getpreferredencoding(False)
    with open(path, "rb", encoding=system_encoding) as f:
        data = f.read()
        print(data)
        
def run_prompt():
    print('Welcome to Plox Interpreter (Type "exit" to exit):')
    while (True):
        data = input("--> ")
        if (data == "exit"):
            break

def main():
    try:
        if len(sys.argv) > 2:
            print("Usage: jlox [script]")
            sys.exit(64)
        elif len(sys.argv) == 2:
            run_script(sys.argv[1])
        else:
            run_prompt()
    except Exception as e:
        print(e, file=sys.stderr)



if __name__ == "__main__":
    main()
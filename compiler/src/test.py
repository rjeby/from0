from sexp_parser import Parser

test_suite: dict[str, object] = {
    # Numbers
    "0": ["val", 0],
    "7": ["val", 7],
    "123": ["val", 123],
    "(minus 42)": ["minus", ["val", 42]],
    # Symbols
    "x": "x",
    "abc": "abc",
    "foo_bar": "foo_bar",
    "Z": "Z",
    # Strings
    '"hello"': '"hello"',
    '"A B C!"': '"A B C!"',
    '"123!"': '"123!"',
    # Expressions with named operators
    "(plus 1 2)": ["plus", ["val", 1], ["val", 2]],
    "(minus x y)": ["minus", "x", "y"],
    "(times 3 4)": ["times", ["val", 3], ["val", 4]],
    "(divide a b)": ["divide", "a", "b"],
    "(plus 1 (times 2 3))": ["plus", ["val", 1], ["times", ["val", 2], ["val", 3]]],
    "(times (plus 1 2) (minus 4 3))": ["times", ["plus", ["val", 1], ["val", 2]], ["minus", ["val", 4], ["val", 3]]],
    "(divide (minus 10 2) (plus 1 1))": ["divide", ["minus", ["val", 10], ["val", 2]], ["plus", ["val", 1], ["val", 1]]],
    "(plus (times (minus 3 1) (divide 8 2)) 7)": ["plus", ["times", ["minus", ["val", 3], ["val", 1]], ["divide", ["val", 8], ["val", 2]]], ["val", 7]],
    # Deep nesting
    "(plus (plus (plus 1 2) (plus 3 4)) (plus 5 6))": ["plus", ["plus", ["plus", ["val", 1], ["val", 2]], ["plus", ["val", 3], ["val", 4]]], ["plus", ["val", 5], ["val", 6]]],
}


def test():
    for input_str, expected in test_suite.items():
        try:
            output = Parser(input_str).parse_exp()
            status = "SUCCESS" if output == expected else "FAILURE"
        except Exception as e:
            output = f"Exception: {e}"
            status = "FAILURE"

        print("-" * 50)
        print(f"INPUT   : {input_str}")
        print(f"EXPECTED: {expected}")
        print(f"OUTPUT  : {output}")
        print(f"STATUS  : {status}")
        print("-" * 50)

if __name__ == "__main__":
    test()
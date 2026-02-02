from sexp_parser import Parser

# Exhaustive test suite for arithmetic-expression S-expr grammar
test_suite: dict[str, str] = {
    # Atoms: numbers
    "0": '"0"',
    "7": '"7"',
    "123": '"123"',
    "-42": '"-42"',
    # Atoms: symbols
    "x": '"x"',
    "abc": '"abc"',
    "foo_bar": '"foo_bar"',
    "Z": '"Z"',
    # Atoms: strings
    '"hello"': '"hello"',
    '"A B C!"': '"A B C!"',
    '"123!"': '"123!"',
    # Atoms: booleans
    "true": '"true"',
    "false": '"false"',
    # Booleans in expressions
    "(+ true false)": '["+", "true", "false"]',
    "(+ 1 true)": '["+", "1", "true"]',
    "(+ false 0)": '["+", "false", "0"]',
    # Single operator lists
    "(+ 1 2)": '["+", "1", "2"]',
    "(- x y)": '["-", "x", "y"]',
    "(* 3 4)": '["*", "3", "4"]',
    "(/ a b)": '["/", "a", "b"]',
    # Nested operations
    "(+ 1 (* 2 3))": '["+", "1", ["*", "2", "3"]]',
    "(* (+ 1 2) (- 4 3))": '["*", ["+", "1", "2"], ["-", "4", "3"]]',
    "(/ (- 10 2) (+ 1 1))": '["/", ["-", "10", "2"], ["+", "1", "1"]]',
    # Atoms: booleans
    "true": '"true"',
    "false": '"false"',
    # Deeply nested
    "(+ (* (- 3 1) (/ 8 2)) 7)": '["+", ["*", ["-", "3", "1"], ["/", "8", "2"]], "7"]',
    # Whitespace variations
    "(+   1\t2)": '["+", "1", "2"]',
    "(+ 1\n2)": '["+", "1", "2"]',
    "(+ 1 \r\n 2)": '["+", "1", "2"]',
    # Edge cases
    "(+ -1 2)": '["+", "-1", "2"]',
    "(+ 0 0)": '["+", "0", "0"]',
    "(+ x 0)": '["+", "x", "0"]',
    '(+ "hello" 5)': '["+", "hello", "5"]',
    # Very deep nesting
    "(+ (+ (+ 1 2) (+ 3 4)) (+ 5 6))": '["+", ["+", ["+", "1", "2"], ["+", "3", "4"]], ["+", "5", "6"]]',
    # Boolean prefix edge cases (should be symbols)
    "truex": '"truex"',
    "falsey": '"falsey"',
    # Boolean-looking strings
    '"true"': '"true"',
    '"false"': '"false"',
}


def test():
    for input_str in test_suite:
        expected = test_suite[input_str]
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
from sexpr_parser import Parser
from sexpr_parser import NestedStringList

test_suite: dict[str, NestedStringList] = {
    "7": "7",
    "e": "e",
    "()": [],
    "(1 2 3)": ["1", "2", "3"],
    "((1 (2 (3 (4)))))": [["1", ["2", ["3", ["4"]]]]],
}


def test():
    for input in test_suite:
        expected = str(test_suite[input])
        output = str(Parser(input).parse())
        status = "SUCCESS" if output == expected else "FAILURE"
        print("-".join(["" for _ in range(25)]))
        print(f"INPUT: {input}\nEXPECTED: {expected}\nOUTPUT: {output}\nSTATUS: {status}")
        print("-".join(["" for _ in range(25)]))



if __name__ == "__main__":
    test()
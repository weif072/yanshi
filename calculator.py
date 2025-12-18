from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple


class CalcError(Exception):
    pass


@dataclass(frozen=True)
class Token:
    kind: str
    value: str


_TOKEN_RE = re.compile(
    r"\s*(?:(?P<NUMBER>(?:\d+(?:\.\d*)?|\.\d+))|(?P<OP>[+\-*/])|(?P<LPAREN>\()|(?P<RPAREN>\))|(?P<MISMATCH>.+))"
)


def tokenize(expr: str) -> List[Token]:
    tokens: List[Token] = []
    pos = 0
    while pos < len(expr):
        m = _TOKEN_RE.match(expr, pos)
        if not m:
            raise CalcError(f"无法解析输入：{expr!r}")
        pos = m.end()

        kind = m.lastgroup
        if kind is None:
            raise CalcError("内部错误：tokenizer")

        if kind == "NUMBER":
            tokens.append(Token("NUMBER", m.group(kind)))
        elif kind == "OP":
            tokens.append(Token("OP", m.group(kind)))
        elif kind == "LPAREN":
            tokens.append(Token("LPAREN", "("))
        elif kind == "RPAREN":
            tokens.append(Token("RPAREN", ")"))
        elif kind == "MISMATCH":
            bad = m.group(kind)
            raise CalcError(f"包含非法字符：{bad!r}")

    return tokens


_PRECEDENCE = {
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2,
    "u-": 3,  # unary minus
}

_ASSOC = {
    "+": "L",
    "-": "L",
    "*": "L",
    "/": "L",
    "u-": "R",
}


def _is_unary_minus(tokens: Sequence[Token], i: int) -> bool:
    t = tokens[i]
    if t.kind != "OP" or t.value != "-":
        return False
    if i == 0:
        return True
    prev = tokens[i - 1]
    return prev.kind in {"OP", "LPAREN"}


def to_rpn(tokens: Sequence[Token]) -> List[Token]:
    output: List[Token] = []
    stack: List[Token] = []

    i = 0
    while i < len(tokens):
        t = tokens[i]

        if t.kind == "NUMBER":
            output.append(t)
        elif t.kind == "OP":
            op = "u-" if _is_unary_minus(tokens, i) else t.value
            op_token = Token("OP", op)

            while stack:
                top = stack[-1]
                if top.kind != "OP":
                    break
                p_top = _PRECEDENCE[top.value]
                p_cur = _PRECEDENCE[op]
                if (p_top > p_cur) or (p_top == p_cur and _ASSOC[op] == "L"):
                    output.append(stack.pop())
                else:
                    break

            stack.append(op_token)
        elif t.kind == "LPAREN":
            stack.append(t)
        elif t.kind == "RPAREN":
            while stack and stack[-1].kind != "LPAREN":
                output.append(stack.pop())
            if not stack or stack[-1].kind != "LPAREN":
                raise CalcError("括号不匹配")
            stack.pop()  # pop LPAREN
        else:
            raise CalcError(f"未知 token：{t}")

        i += 1

    while stack:
        top = stack.pop()
        if top.kind in {"LPAREN", "RPAREN"}:
            raise CalcError("括号不匹配")
        output.append(top)

    return output


def eval_rpn(rpn: Sequence[Token]) -> float:
    st: List[float] = []

    def pop1() -> float:
        if not st:
            raise CalcError("表达式不完整")
        return st.pop()

    def pop2() -> Tuple[float, float]:
        b = pop1()
        a = pop1()
        return a, b

    for t in rpn:
        if t.kind == "NUMBER":
            st.append(float(t.value))
            continue

        if t.kind != "OP":
            raise CalcError("RPN 解析错误")

        if t.value == "u-":
            a = pop1()
            st.append(-a)
        elif t.value == "+":
            a, b = pop2()
            st.append(a + b)
        elif t.value == "-":
            a, b = pop2()
            st.append(a - b)
        elif t.value == "*":
            a, b = pop2()
            st.append(a * b)
        elif t.value == "/":
            a, b = pop2()
            if b == 0:
                raise CalcError("除数不能为 0")
            st.append(a / b)
        else:
            raise CalcError(f"不支持的运算符：{t.value}")

    if len(st) != 1:
        raise CalcError("表达式不完整")
    return st[0]


def calculate(expr: str) -> float:
    tokens = tokenize(expr)
    rpn = to_rpn(tokens)
    return eval_rpn(rpn)


def _fmt_number(x: float) -> str:
    # 处理像 2.0 这种输出，尽量展示为 2
    if x.is_integer():
        return str(int(x))
    return str(x)


def repl() -> None:
    print("简易计算器（支持 + - * / 和括号）")
    print("输入示例：1 + 2*(3-4) / -5")
    print("输入 q 退出\n")

    while True:
        try:
            s = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n退出")
            return

        if not s:
            continue
        if s.lower() in {"q", "quit", "exit"}:
            print("退出")
            return

        try:
            result = calculate(s)
            print(_fmt_number(result))
        except CalcError as e:
            print(f"错误：{e}")
        except Exception as e:
            print(f"未知错误：{e}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    import sys

    argv_list = list(sys.argv[1:] if argv is None else argv)

    if not argv_list:
        repl()
        return 0

    if argv_list[0] in {"-h", "--help"}:
        print("简易计算器（支持 + - * / 和括号；安全解析，不使用 eval）")
        print("\n用法：")
        print("  python calculator.py            # 进入交互模式")
        print("  python calculator.py <表达式>    # 直接计算")
        print("\n示例：")
        print('  python calculator.py "1 + 2*(3-4) / -5"')
        print('  python calculator.py "-(1+2)*3"')
        return 0

    expr = " ".join(argv_list).strip()
    if not expr:
        repl()
        return 0

    try:
        print(_fmt_number(calculate(expr)))
        return 0
    except CalcError as e:
        print(f"错误：{e}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

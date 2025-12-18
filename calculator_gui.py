from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from calculator import CalcError, calculate


class CalculatorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("简易计算器")
        self.root.resizable(False, False)

        # Layout
        main = ttk.Frame(root, padding=12)
        main.grid(row=0, column=0, sticky="nsew")

        ttk.Label(main, text="表达式：").grid(row=0, column=0, sticky="w")

        self.expr_var = tk.StringVar()
        self.expr_entry = ttk.Entry(main, textvariable=self.expr_var, width=36)
        self.expr_entry.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(4, 8))
        self.expr_entry.focus_set()

        keypad = ttk.Frame(main)
        keypad.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))

        self.result_var = tk.StringVar(value="")
        ttk.Label(main, text="结果：").grid(row=3, column=0, sticky="w")
        self.result_label = ttk.Label(main, textvariable=self.result_var)
        self.result_label.grid(row=4, column=0, columnspan=3, sticky="w", pady=(4, 10))

        self.calc_btn = ttk.Button(main, text="计算", command=self.on_calculate)
        self.calc_btn.grid(row=5, column=0, sticky="ew")

        self.clear_btn = ttk.Button(main, text="清空", command=self.on_clear)
        self.clear_btn.grid(row=5, column=1, sticky="ew", padx=(8, 0))

        self.quit_btn = ttk.Button(main, text="退出", command=root.destroy)
        self.quit_btn.grid(row=5, column=2, sticky="ew", padx=(8, 0))

        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.columnconfigure(2, weight=1)

        # Keypad
        buttons = [
            [("7", "7"), ("8", "8"), ("9", "9"), ("÷", "/")],
            [("4", "4"), ("5", "5"), ("6", "6"), ("×", "*")],
            [("1", "1"), ("2", "2"), ("3", "3"), ("−", "-")],
            [("0", "0"), ("(", "("), (")", ")"), ("+", "+")],
        ]

        for r, row in enumerate(buttons):
            for c, (label, value) in enumerate(row):
                btn = ttk.Button(keypad, text=label, command=lambda v=value: self.on_insert(v))
                btn.grid(row=r, column=c, sticky="ew", padx=2, pady=2)

        for c in range(4):
            keypad.columnconfigure(c, weight=1)

        # Bindings
        root.bind("<Return>", lambda _e: self.on_calculate())
        root.bind("<Escape>", lambda _e: self.on_clear())

    def on_insert(self, text: str) -> None:
        try:
            index = self.expr_entry.index(tk.INSERT)
            self.expr_entry.insert(index, text)
        finally:
            self.expr_entry.focus_set()

    def on_clear(self) -> None:
        self.expr_var.set("")
        self.result_var.set("")
        self.expr_entry.focus_set()

    def on_calculate(self) -> None:
        expr = self.expr_var.get().strip()
        if not expr:
            self.result_var.set("")
            return

        try:
            value = calculate(expr)
            if float(value).is_integer():
                self.result_var.set(str(int(value)))
            else:
                self.result_var.set(str(value))
        except CalcError as e:
            self.result_var.set(f"错误：{e}")
        except Exception as e:
            self.result_var.set(f"未知错误：{e}")


def main() -> int:
    root = tk.Tk()
    # 使用系统主题（Windows 上默认看起来比较顺眼）
    try:
        ttk.Style().theme_use("vista")
    except Exception:
        pass

    CalculatorApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# 简易计算器

一个很轻量的命令行计算器：支持 `+ - * /`、括号、以及一元负号（例如 `-5`、`1*-2`）。

## 运行

进入本目录后：

- 交互模式：

```bash
python calculator.py
```

- 界面模式（Tkinter 小窗口）：

```bash
python calculator_gui.py
```

- 直接计算一条表达式：

```bash
python calculator.py "1 + 2*(3-4) / -5"
```

- 以 `-` 开头的表达式也支持：

```bash
python calculator.py "-(1+2)*3"
```

## 说明

- 该脚本不会使用 `eval`，而是对表达式进行 tokenize + 逆波兰式（RPN）计算。
- 除数为 0 会报错。

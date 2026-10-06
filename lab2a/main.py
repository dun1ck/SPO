# -*- coding: utf-8 -*-
"""
Лабораторная работа №2: «Метрики сложности потока управления» (язык Groovy).
Метрика Джилба (CL, cl, CLI) и метрика Маккейба (Z(G)).
"""

import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


def analyze_groovy(code):
    """
    Простой парсер Groovy для расчёта метрик сложности:
    - CL: абсолютная сложность (число ветвлений: if, else if, циклы, case, ?:)
    - N_total: общее число исполняемых операторов
    - cl = CL / N_total: относительная сложность
    - CLI: максимальный уровень вложенности (для switch с n выходами: n-2)
    - Z(G) = CL + 1: цикломатическое число Маккейба
    """
    # 1. Удаление комментариев // и /* ... */
    clean_text = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    clean_text = re.sub(r'//.*', '', clean_text)

    cl = 0
    cli = 0
    total_ops = 0
    conditions = []

    scope_stack = []      # Стек типов блоков: 'class', 'method', 'cond', 'switch'
    switch_cases = 0      # Счётчик case в текущем switch

    lines = clean_text.splitlines()
    for line_no, raw_line in enumerate(lines, 1):
        # Удаляем строковые литералы, чтобы ключевые слова внутри строк не учитывались
        line = re.sub(r'("""|\'\'\'|".*?"|\'.*?\')', '""', raw_line).strip()
        if not line:
            continue

        # Закрытие блоков в начале строки (например, '} else {')
        leading_closes = len(re.match(r'^(\s*\})*', line).group(0).replace(' ', ''))
        for _ in range(leading_closes):
            if scope_stack:
                if scope_stack.pop() == 'switch':
                    switch_cases = 0

        # Поиск условных операторов и циклов
        found_type = None
        if re.search(r'\belse\s+if\b', line):
            found_type = 'else if'
        elif re.search(r'\bif\b', line):
            found_type = 'if'
        elif re.search(r'\bfor\s*\(', line):
            found_type = 'for'
        elif re.search(r'\bwhile\s*\(', line) and not re.search(r'\}\s*while', line):
            found_type = 'while'
        elif re.search(r'\bdo\s*\{', line) or line == 'do':
            found_type = 'do-while'
        elif re.search(r'\bcase\b', line):
            found_type = 'case'
        elif '?' in line and ':' in line and not ('?:' in line or '?.' in line):
            found_type = 'ternary ?:'

        pending_switch = bool(re.search(r'\bswitch\s*\(', line))

        # Уровень вложенности условий (число объемлющих 'cond')
        cond_depth = sum(1 for b in scope_stack if b == 'cond')

        if found_type:
            cl += 1
            if found_type == 'case':
                switch_cases += 1
                curr_depth = cond_depth + (switch_cases - 1)
            else:
                curr_depth = cond_depth + max(0, switch_cases - 1)

            cli = max(cli, curr_depth)
            conditions.append((line_no, found_type, curr_depth, raw_line.strip()))

        # Счётчик операторов (строки, не являющиеся только заголовками классов/методов или скобками)
        is_structure = re.match(r'^(class|interface|static\s+void|def\s+\w+\s*\(|[{}]+$|package|import)', line)
        if not is_structure:
            total_ops += 1

        # Открытие и закрытие блоков в остатке строки
        remaining = line[leading_closes:]
        for _ in range(remaining.count('{')):
            if pending_switch:
                scope_stack.append('switch')
                pending_switch = False
            elif found_type and found_type not in ('case', 'ternary ?:'):
                scope_stack.append('cond')
            elif re.search(r'\b(class|interface)\b', line):
                scope_stack.append('class')
            elif re.search(r'\b(def|void|static)\b.*\([^)]*\)\s*\{?', line):
                scope_stack.append('method')
            else:
                scope_stack.append('block')

        for _ in range(remaining.count('}')):
            if scope_stack:
                if scope_stack.pop() == 'switch':
                    switch_cases = 0

    rel_cl = cl / total_ops if total_ops else 0
    return {
        'CL': cl,
        'N_total': total_ops,
        'cl': rel_cl,
        'CLI': cli,
        'Z(G)': cl + 1,
        'conditions': conditions
    }


class SimpleMetricsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №2 — Метрики Джилба и Маккейба (Groovy)")
        self.root.geometry("960x640")

        # Верхняя панель управления
        top_frame = ttk.Frame(root, padding=6)
        top_frame.pack(fill=tk.X)

        ttk.Button(top_frame, text="📂 Выбрать файл...", command=self.open_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(top_frame, text="▶ Рассчитать метрики", command=self.calculate).pack(side=tk.LEFT, padx=4)
        ttk.Button(top_frame, text="Очистить", command=self.clear_all).pack(side=tk.LEFT, padx=4)

        self.lbl_file = ttk.Label(top_frame, text="Файл не выбран", font=("Segoe UI", 9, "italic"))
        self.lbl_file.pack(side=tk.LEFT, padx=10)

        # Разделитель на две части (исходный код слева, результат справа)
        main_pane = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # Левая часть: текстовый редактор кода
        left_frame = ttk.LabelFrame(main_pane, text=" Исходный код (Groovy) ", padding=4)
        main_pane.add(left_frame, weight=5)

        self.txt_code = tk.Text(left_frame, font=("Consolas", 10), wrap="none", undo=True)
        scroll_code_y = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.txt_code.yview)
        scroll_code_x = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=self.txt_code.xview)
        self.txt_code.configure(yscrollcommand=scroll_code_y.set, xscrollcommand=scroll_code_x.set)

        self.txt_code.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_code_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_code_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Правая часть: отображение результатов
        right_frame = ttk.LabelFrame(main_pane, text=" Результаты расчёта метрик ", padding=4)
        main_pane.add(right_frame, weight=5)

        self.txt_result = tk.Text(right_frame, font=("Consolas", 10), wrap="none")
        scroll_res_y = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.txt_result.yview)
        self.txt_result.configure(yscrollcommand=scroll_res_y.set)

        self.txt_result.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_res_y.pack(side=tk.RIGHT, fill=tk.Y)

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Выберите файл программы",
            filetypes=[("Groovy/Text", "*.groovy;*.txt;*.java"), ("Все файлы", "*.*")]
        )
        if path:
            self.load_path(path)

    def clear_all(self):
        self.txt_code.delete("1.0", tk.END)
        self.txt_result.delete("1.0", tk.END)
        self.lbl_file.config(text="Файл не выбран")

    def load_path(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.txt_code.delete("1.0", tk.END)
            self.txt_code.insert("1.0", content)
            self.lbl_file.config(text=os.path.basename(path))
            self.calculate()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")

    def calculate(self):
        code = self.txt_code.get("1.0", "end-1c")
        if not code.strip():
            messagebox.showinfo("Инфо", "Введите или откройте код для анализа.")
            return

        res = analyze_groovy(code)

        # Формирование отчёта
        lines = []
        lines.append("ИТОГОВЫЕ РЕЗУЛЬТАТЫ РАСЧЁТА")
        lines.append(f"Абсолютная сложность Джилба (CL):      {res['CL']}")
        lines.append(f"Общее количество операторов (N_total): {res['N_total']}")
        lines.append(f"Относительная сложность Джилба (cl):   {res['cl']:.4f} ({res['cl'] * 100:.2f}%)")
        lines.append(f"Максимальная вложенность (CLI):        {res['CLI']}")
        lines.append(f"Цикломатическое число Маккейба Z(G):   {res['Z(G)']}")
        lines.append("")
        lines.append("СПИСОК ОБНАРУЖЕННЫХ ВЕТВЛЕНИЙ (CL):")
        lines.append(f"{'№':>3} | {'Стр.':>4} | {'Влож.':>5} | {'Тип':<10} | {'Код'}")
        for i, (line_no, cond_type, depth, src) in enumerate(res['conditions'], 1):
            lines.append(f"{i:3d} | {line_no:4d} | {depth:5d} | {cond_type:<10s} | {src}")

        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert("1.0", "\n".join(lines))


def main():
    root = tk.Tk()
    app = SimpleMetricsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

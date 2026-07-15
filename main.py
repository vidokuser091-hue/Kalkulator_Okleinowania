#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kalkulator Okleinowania
Program do obliczania kosztów okleinowania profili
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import sys

from app.calculator import OkleinowanieCalculator
from app.ui import CalculatorUI


def main():
    root = tk.Tk()
    app = CalculatorUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Interfejs użytkownika kalkulatora okleinowania
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from app.calculator import OkleinowanieCalculator


class CalculatorUI:
    """Interfejs graficzny kalkulatora"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Kalkulator Okleinowania")
        self.root.geometry("1100x750")
        self.root.resizable(True, True)
        
        self.calculator = OkleinowanieCalculator()
        self.current_file = None
        self.item_to_profil = {}  # Mapowanie item_id -> nazwa profilu
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Stwórz komponenty UI"""
        # Frame główny
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ========== SEKCJA WCZYTYWANIA PLIKU ==========
        file_frame = ttk.LabelFrame(main_frame, text="Wczytaj plik", padding="10")
        file_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        self.file_label = ttk.Label(file_frame, text="Brak wczytanego pliku", foreground="gray")
        self.file_label.grid(row=0, column=0, sticky=tk.W, padx=5)
        
        ttk.Button(file_frame, text="Wybierz plik Excel", command=self._load_file).grid(row=0, column=1, padx=5)
        
        # ========== SEKCJA USTAWIEŃ ==========
        settings_frame = ttk.LabelFrame(main_frame, text="Ustawienia", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # Kwota okleinowania
        ttk.Label(settings_frame, text="Kwota okleinowania (zł/mb):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.kwota_var = tk.DoubleVar(value=100.0)
        ttk.Spinbox(settings_frame, from_=0, to=10000, textvariable=self.kwota_var, width=15).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Okleinowanie dwustronne
        ttk.Label(settings_frame, text="Typ okleinowania:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.dwustronne_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Dwustronne", variable=self.dwustronne_var, 
                       command=self._on_dwustronne_changed).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Współczynnik mnożenia
        ttk.Label(settings_frame, text="Współczynnik mnożenia (dwustronne):").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.wspolczynnik_var = tk.DoubleVar(value=0.5)
        self.wspolczynnik_spinbox = ttk.Spinbox(settings_frame, from_=0, to=10, textvariable=self.wspolczynnik_var, 
                                                 width=15, state=tk.DISABLED)
        self.wspolczynnik_spinbox.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # ========== SEKCJA PROFILI ==========
        profiles_frame = ttk.LabelFrame(main_frame, text="Profile do okleinowania", padding="10")
        profiles_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Przycisk zaznacz/odznacz wszystko
        button_frame = ttk.Frame(profiles_frame)
        button_frame.grid(row=0, column=0, columnspan=7, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(button_frame, text="✓ Zaznacz wszystko", command=self._select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✗ Odznacz wszystko", command=self._deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Label(button_frame, text="(Kliknij na checkbox aby wybrać profil)", foreground="gray", font=("Arial", 9, "italic")).pack(side=tk.LEFT, padx=20)
        
        # Tabelka z profilami
        columns = ("Wybór", "Profil", "Długość (mm)", "Ilość", "mb", "Cena (zł)")
        self.tree = ttk.Treeview(profiles_frame, columns=columns, height=15, show='headings')
        
        # Definiuj kolumny
        self.tree.column('Wybór', width=60, anchor=tk.CENTER)
        self.tree.column('Profil', width=280, anchor=tk.W)
        self.tree.column('Długość (mm)', width=110, anchor=tk.CENTER)
        self.tree.column('Ilość', width=70, anchor=tk.CENTER)
        self.tree.column('mb', width=80, anchor=tk.CENTER)
        self.tree.column('Cena (zł)', width=100, anchor=tk.CENTER)
        
        # Nagłówki
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.grid(row=1, column=0, columnspan=7, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(profiles_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=1, column=7, sticky=(tk.N, tk.S))
        self.tree.configure(yscroll=scrollbar.set)
        
        # Bind click do zaznaczania
        self.tree.bind('<Button-1>', self._on_tree_click)
        
        # ========== SEKCJA WYNIKÓW ==========
        results_frame = ttk.LabelFrame(main_frame, text="Podsumowanie", padding="10")
        results_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(results_frame, text="Cena całkowita:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.total_label = ttk.Label(results_frame, text="0.00 zł", font=("Arial", 14, "bold"), foreground="green")
        self.total_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Przycisk obliczenia
        ttk.Button(main_frame, text="Oblicz", command=self._calculate).grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky=tk.W)
        ttk.Button(main_frame, text="Wyczyść", command=self._clear).grid(row=4, column=2, columnspan=2, padx=5, pady=10, sticky=tk.W)
        
        # Skonfiguruj rozciąganie
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        profiles_frame.columnconfigure(0, weight=1)
        profiles_frame.rowconfigure(1, weight=1)
    
    def _load_file(self):
        """Wczytaj plik Excel"""
        filepath = filedialog.askopenfilename(
            title="Wybierz plik Excel",
            filetypes=[("Pliki Excel", "*.xlsx *.xls"), ("Wszystkie pliki", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            if self.calculator.load_from_excel(filepath):
                self.current_file = filepath
                self.file_label.config(text=f"Wczytano: {Path(filepath).name}", foreground="green")
                self._refresh_profiles_table()
            else:
                messagebox.showwarning("Brak danych", "Plik nie zawiera profili z oznaczeniem RAL.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać pliku:\n{str(e)}")
    
    def _refresh_profiles_table(self):
        """Odśwież tabelę profili"""
        # Wyczyść tabelę
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.item_to_profil = {}
        
        # Dodaj profile
        for profil in self.calculator.get_profiles():
            mb = profil.get_mb()
            checkbox_text = "☑" if profil.wybrany else "☐"
            item_id = self.tree.insert('', 'end', values=(
                checkbox_text,
                profil.nazwa,
                f"{profil.dlg_szt:.0f}",
                profil.ilosc,
                f"{mb:.2f}",
                "0.00"
            ))
            self.item_to_profil[item_id] = profil.nazwa
    
    def _on_tree_click(self, event):
        """Obsłuż klik na wiersz tabeli"""
        item = self.tree.identify('item', event.x, event.y)
        col = self.tree.identify_column(event.x, event.y)
        
        if not item:
            return
        
        # Tylko jeśli kliknięto na kolumnę "Wybór" (#1)
        if col == '#1':
            try:
                if item in self.item_to_profil:
                    profil_name = self.item_to_profil[item]
                    profil = self.calculator.get_profil_by_name(profil_name)
                    if profil:
                        # Przełącz stan
                        profil.wybrany = not profil.wybrany
                        print(f"✓ Profil '{profil_name}' - {'ZAZNACZONY (BĘDZIE OKLEJANY)' if profil.wybrany else 'ODZNACZONY (POMINIĘTY)'}")
                        self._refresh_profiles_table()
            except Exception as e:
                print(f"Błąd: {e}")
    
    def _select_all(self):
        """Zaznacz wszystkie profile"""
        self.calculator.toggle_all(True)
        self._refresh_profiles_table()
        print("✓ Wszystkie profile zaznaczone - BĘDĄ OKLEJANE")
    
    def _deselect_all(self):
        """Odznacz wszystkie profile"""
        self.calculator.toggle_all(False)
        self._refresh_profiles_table()
        print("✗ Wszystkie profile odznaczone - BĘDĄ POMINIĘTE")
    
    def _on_dwustronne_changed(self):
        """Zmień stan dostępności współczynnika"""
        if self.dwustronne_var.get():
            self.wspolczynnik_spinbox.config(state=tk.NORMAL)
        else:
            self.wspolczynnik_spinbox.config(state=tk.DISABLED)
    
    def _calculate(self):
        """Oblicz ceny"""
        if not self.calculator.get_profiles():
            messagebox.showwarning("Brak danych", "Najpierw wczytaj plik z profilami.")
            return
        
        try:
            kwota = self.kwota_var.get()
            dwustronne = self.dwustronne_var.get()
            wspolczynnik = self.wspolczynnik_var.get() if dwustronne else 1.0
            
            total, ceny_profili = self.calculator.calculate_total(kwota, dwustronne, wspolczynnik)
            
            # Aktualizuj tabelę z cenami
            for item in self.tree.get_children():
                row_values = list(self.tree.item(item, 'values'))
                if row_values:
                    profil_name = row_values[1]
                    if profil_name in ceny_profili:
                        row_values[5] = f"{ceny_profili[profil_name]:.2f}"
                        self.tree.item(item, values=row_values)
            
            # Aktualizuj cenę całkowitą
            self.total_label.config(text=f"{total:.2f} zł")
            
            # Pokaż info ile profili obliczono
            zaznaczonych = sum(1 for p in self.calculator.get_profiles() if p.wybrany)
            print(f"\n✅ OBLICZONO: {zaznaczonych} profili do okleinowania")
            print(f"💰 Cena całkowita: {total:.2f} zł\n")
        
        except ValueError:
            messagebox.showerror("Błąd", "Sprawdź czy wszystkie wartości są liczbami.")
    
    def _clear(self):
        """Wyczyść wszystkie dane"""
        self.kwota_var.set(100.0)
        self.dwustronne_var.set(False)
        self.wspolczynnik_var.set(0.5)
        self.total_label.config(text="0.00 zł")
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.file_label.config(text="Brak wczytanego pliku", foreground="gray")
        self.current_file = None
        self.calculator = OkleinowanieCalculator()
        self.item_to_profil = {}

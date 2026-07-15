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
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        self.calculator = OkleinowanieCalculator()
        self.current_file = None
        self.checkbox_buttons = {}  # Przechowuje przyciski checkboxów
        
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
        ttk.Label(button_frame, text="(Kliknij przycisk w kolumnie 'Wybór' aby zaznaczać/odznaczać)", foreground="gray", font=("Arial", 9, "italic")).pack(side=tk.LEFT, padx=20)
        
        # Frame z scrollbarem dla profili
        self.profiles_container = ttk.Frame(profiles_frame)
        self.profiles_container.grid(row=1, column=0, columnspan=7, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Canvas i scrollbar dla dynamicznych checkboxów
        self.canvas = tk.Canvas(self.profiles_container, height=300, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.profiles_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame wewnątrz canvas dla profili
        self.profiles_frame_inner = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.profiles_frame_inner, anchor="nw")
        
        # Bind mousewheel
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)
        
        profiles_frame.columnconfigure(0, weight=1)
        profiles_frame.rowconfigure(1, weight=1)
        
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
    
    def _on_mousewheel(self, event):
        """Obsługa scrollowania myszką"""
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
    
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
                self._refresh_profiles_list()
            else:
                messagebox.showwarning("Brak danych", "Plik nie zawiera profili z oznaczeniem RAL.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać pliku:\n{str(e)}")
    
    def _refresh_profiles_list(self):
        """Odśwież listę profili z checkboxami"""
        # Wyczyść poprzednie checkboxy
        for widget in self.profiles_frame_inner.winfo_children():
            widget.destroy()
        self.checkbox_buttons = {}
        
        # Nagłówek
        header_frame = ttk.Frame(self.profiles_frame_inner)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(header_frame, text="Wybór", font=("Arial", 10, "bold"), width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Profil", font=("Arial", 10, "bold"), width=35).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Długość (mm)", font=("Arial", 10, "bold"), width=12).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Ilość", font=("Arial", 10, "bold"), width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="mb", font=("Arial", 10, "bold"), width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(header_frame, text="Cena (zł)", font=("Arial", 10, "bold"), width=12).pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(self.profiles_frame_inner, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)
        
        # Dodaj profile
        for profil in self.calculator.get_profiles():
            self._add_profil_row(profil)
        
        # Update canvas scroll region
        self.profiles_frame_inner.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _add_profil_row(self, profil):
        """Dodaj wiersz z profilem i checkboxem"""
        row_frame = ttk.Frame(self.profiles_frame_inner)
        row_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Przycisk checkbox
        checkbox_btn = tk.Button(
            row_frame,
            text="☑" if profil.wybrany else "☐",
            width=3,
            font=("Arial", 14),
            bg="lightgreen" if profil.wybrany else "lightcoral",
            command=lambda p=profil: self._toggle_profil(p, checkbox_btn)
        )
        checkbox_btn.pack(side=tk.LEFT, padx=5)
        self.checkbox_buttons[profil.nazwa] = checkbox_btn
        
        # Profil
        ttk.Label(row_frame, text=profil.nazwa, width=35, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        
        # Długość
        ttk.Label(row_frame, text=f"{profil.dlg_szt:.0f}", width=12, anchor=tk.CENTER).pack(side=tk.LEFT, padx=5)
        
        # Ilość
        ttk.Label(row_frame, text=f"{profil.ilosc}", width=8, anchor=tk.CENTER).pack(side=tk.LEFT, padx=5)
        
        # mb
        ttk.Label(row_frame, text=f"{profil.get_mb():.2f}", width=10, anchor=tk.CENTER).pack(side=tk.LEFT, padx=5)
        
        # Cena (domyślnie 0)
        cena_label = ttk.Label(row_frame, text="0.00", width=12, anchor=tk.CENTER)
        cena_label.pack(side=tk.LEFT, padx=5)
        
        # Store reference do ceny
        row_frame.cena_label = cena_label
        row_frame.profil = profil
    
    def _toggle_profil(self, profil, button):
        """Przełącz stan profilu"""
        profil.wybrany = not profil.wybrany
        button.config(
            text="☑" if profil.wybrany else "☐",
            bg="lightgreen" if profil.wybrany else "lightcoral"
        )
        status = "ZAZNACZONY (BĘDZIE OKLEJANY)" if profil.wybrany else "ODZNACZONY (POMINIĘTY)"
        print(f"✓ Profil '{profil.nazwa}' - {status}")
    
    def _select_all(self):
        """Zaznacz wszystkie profile"""
        self.calculator.toggle_all(True)
        for profil in self.calculator.get_profiles():
            if profil.nazwa in self.checkbox_buttons:
                button = self.checkbox_buttons[profil.nazwa]
                button.config(text="☑", bg="lightgreen")
        print("✓ Wszystkie profile zaznaczone - BĘDĄ OKLEJANE")
    
    def _deselect_all(self):
        """Odznacz wszystkie profile"""
        self.calculator.toggle_all(False)
        for profil in self.calculator.get_profiles():
            if profil.nazwa in self.checkbox_buttons:
                button = self.checkbox_buttons[profil.nazwa]
                button.config(text="☐", bg="lightcoral")
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
            
            # Aktualizuj ceny w wierszach
            for row_frame in self.profiles_frame_inner.winfo_children():
                if hasattr(row_frame, 'profil'):
                    profil = row_frame.profil
                    if profil.nazwa in ceny_profili:
                        row_frame.cena_label.config(text=f"{ceny_profili[profil.nazwa]:.2f}")
            
            # Aktualizuj cenę całkowitą
            self.total_label.config(text=f"{total:.2f} zł")
            
            # Pokaż info
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
        self.file_label.config(text="Brak wczytanego pliku", foreground="gray")
        self.current_file = None
        self.calculator = OkleinowanieCalculator()
        self.checkbox_buttons = {}
        for widget in self.profiles_frame_inner.winfo_children():
            widget.destroy()

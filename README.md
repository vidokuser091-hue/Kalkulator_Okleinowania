# Kalkulator Okleinowania

Program do obliczania kosztów okleinowania profili na podstawie pliku Excel.

## Funkcje

- Wczytywanie profili z pliku `.xlsx`
- Filtrowanie profili zawierających oznaczenie RAL
- Grupowanie profili o tej samej nazwie ale różnych długościach
- Obliczanie metrażu bieżącego (mb)
- Możliwość wyboru okleinowania jednostronnego/dwustronnego
- Indywidualny dobór współczynnika mnożenia
- Zaznaczanie/odznaczanie poszczególnych profili
- Przycisk "zaznacz/odznacz wszystko"
- Automatyczne dodawanie opłaty za profile poniżej 300 zł

## Wymagania

- Python 3.7+
- openpyxl

## Instalacja

```bash
pip install openpyxl
```

## Uruchomienie

```bash
python main.py
```

## Format pliku Excel

Plik Excel musi zawierać kolumny:
- **Nazwa profilu** (musi zawierać kod RAL, np. "Profil_RAL_1005")
- **DLG_SZT** (długość w mm)
- **ILOSC** (ilość sztuk)

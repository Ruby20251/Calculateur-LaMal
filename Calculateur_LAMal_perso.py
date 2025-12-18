#Auteur : Ruben ten Cate
#Projet : Calculateur LAMal
#Version : v5.0 du 17/12/2025

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import re
from utils import (
    normalise_codepostal,
    franchise_label,
    fr_to_int_label,
    age_from_birth_year,
    classe_age_from_age,
    ANNEE_REF,
    FRANCHISES_ENFANT,
    FRANCHISES_ADULTE,
)

#Chemin de l'icône avec os.path
script_dir = os.path.dirname(__file__)
icon_path = os.path.join(script_dir, "assets", "letter_r.ico")

class CalculateurLaMalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculateur LaMal - Top offres") #Pour avoir l'icône R
        self.iconbitmap(icon_path)
        self.geometry("1100x760")
        self.resizable(True, True)

        self.df_postal = None
        self.df_primes = None
        self.primes_cols = []
        self.postal_col = None
        self.region_col = None
        # detected logical columns in primes
        self.col_prime = None
        self.col_assurance = None
        self.col_modele = None
        self.col_franchise = None
        self.col_accident = None
        self.col_classe = None
        self.col_region = None
        self.col_canton = None

        self.create_widgets()

#-----------------------Application Tkinter--------------------------------

    def create_widgets(self):
        frm_top = ttk.Frame(self, padding=10)
        frm_top.pack(fill="x")

        # Fichiers CSV (Code postal / Primes)
        ttk.Label(frm_top, text="Fichier Code_Postal_Region (.csv)").grid(row=0, column=0, sticky="w")
        self.entry_postal = ttk.Entry(frm_top, width=60)
        self.entry_postal.grid(row=0, column=1, padx=5, sticky="w")
        ttk.Button(frm_top, text="Ouvrir", command=self.open_postal_file).grid(row=0, column=2)

        ttk.Label(frm_top, text="Fichier Primes (.csv)").grid(row=1, column=0, sticky="w")
        self.entry_primes = ttk.Entry(frm_top, width=60)
        self.entry_primes.grid(row=1, column=1, padx=5, sticky="w")
        ttk.Button(frm_top, text="Ouvrir", command=self.open_primes_file).grid(row=1, column=2)

        frm_inputs = ttk.LabelFrame(self, text="Entrées utilisateur", padding=10)
        frm_inputs.pack(fill="x", padx=10, pady=8)

        # Année de naissance (YYYY)
        ttk.Label(frm_inputs, text="Année de naissance (YYYY)").grid(row=0, column=0, sticky="w")
        self.var_birth_year = tk.StringVar()
        ent_birth_year = ttk.Entry(frm_inputs, textvariable=self.var_birth_year, width=8)
        ent_birth_year.grid(row=0, column=1, sticky="w")
        ent_birth_year.bind("<FocusOut>", lambda e: self.update_franchise_options())
        self.var_birth_year.trace_add("write", lambda *args: self.update_franchise_options())

        # Code postal
        ttk.Label(frm_inputs, text="Code postal").grid(row=1, column=0, sticky="w")
        self.var_postal = tk.StringVar()
        ttk.Entry(frm_inputs, textvariable=self.var_postal, width=20).grid(row=1, column=1, sticky="w")

        # Canton
        ttk.Label(frm_inputs, text="Canton").grid(row=2, column=0, sticky="w")
        self.var_canton = tk.StringVar()
        cantons = ["AG", "AI", "AR", "BE", "BL", "BS", "FR", "GE", "GL", "GR", "JU", "LU", "NE", "NW", "OW", "SG", "SH", "SO", "SZ", "TG", "TI", "UR", "VD", "VS", "ZG", "ZH"]
        ttk.Combobox(frm_inputs, textvariable=self.var_canton, values=cantons, width=10, state="readonly").grid(row=2, column=1, sticky="w")

        # Accident
        ttk.Label(frm_inputs, text="Accident (Avec / Sans)").grid(row=3, column=0, sticky="w")
        self.var_accident = tk.StringVar(value="Sans")
        ttk.Combobox(frm_inputs, textvariable=self.var_accident, values=["Avec", "Sans"], width=12).grid(row=3, column=1, sticky="w")

        # Franchise
        ttk.Label(frm_inputs, text="Franchise").grid(row=4, column=0, sticky="w")
        self.var_franchise = tk.StringVar()
        self.combo_franchise = ttk.Combobox(frm_inputs, textvariable=self.var_franchise, values=[], width=15, state="readonly")
        self.combo_franchise.grid(row=4, column=1, sticky="w")

        # Mode prime actuelle
        ttk.Label(frm_inputs, text="Mode prime actuelle").grid(row=0, column=2, sticky="w")
        self.var_mode_prime = tk.StringVar(value="manual")
        rb_manual = ttk.Radiobutton(frm_inputs, text="Saisir la prime", variable=self.var_mode_prime, value="manual", command=self.toggle_prime_mode)
        rb_manual.grid(row=0, column=3, sticky="w")
        rb_insurer = ttk.Radiobutton(frm_inputs, text="Ma caisse et mon modèle", variable=self.var_mode_prime, value="by_insurer", command=self.toggle_prime_mode)
        rb_insurer.grid(row=1, column=3, sticky="w")

        # Prime actuelle manual
        ttk.Label(frm_inputs, text="Prime actuelle (CHF / mois)").grid(row=2, column=2, sticky="w")
        self.var_prime_actuelle = tk.StringVar()
        self.entry_prime_actuelle = ttk.Entry(frm_inputs, textvariable=self.var_prime_actuelle, width=18)
        self.entry_prime_actuelle.grid(row=2, column=3, sticky="w")

        # Assureur et modèle selection
        ttk.Label(frm_inputs, text="Caisse actuelle").grid(row=3, column=2, sticky="w")
        self.var_assureur_actuel = tk.StringVar()
        self.combo_assureur = ttk.Combobox(frm_inputs, textvariable=self.var_assureur_actuel, values=[], width=40, state="disabled")
        self.combo_assureur.grid(row=3, column=3, sticky="w")
        self.combo_assureur.bind("<<ComboboxSelected>>", lambda e: self.populate_models_for_assureur())

        ttk.Label(frm_inputs, text="Modèle actuel").grid(row=4, column=2, sticky="w")
        self.var_modele_actuel = tk.StringVar()
        self.combo_modele_assureur = ttk.Combobox(frm_inputs, textvariable=self.var_modele_actuel, values=[], width=40, state="disabled")
        self.combo_modele_assureur.grid(row=4, column=3, sticky="w")

        #Bouton Calculer

        ttk.Button(frm_inputs, text="Calculer", command=self.calculer).grid(row=6, column=2, columnspan=2, pady=8, sticky="E")

        # Résultats
        frm_res = ttk.LabelFrame(self, text="Résultat", padding=10)
        frm_res.pack(fill="both", expand=True, padx=10, pady=8)

        ttk.Label(frm_res, text="Offre la moins chère").pack(anchor="w")
        self.txt_result = tk.Text(frm_res, height=6, wrap="word")
        self.txt_result.pack(fill="x", padx=5, pady=5)

        ttk.Label(frm_res, text="Top 5 offres (assurance | modèle | prime CHF/mois | économie)").pack(anchor="w", pady=(6,0))
        cols = ("Assurance", "Modèle", "Prime", "Économie")
        self.tree = ttk.Treeview(frm_res, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c)
            width = 260 if c == "Économie" else 260
            self.tree.column(c, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
    
#---------------------------------------------------------------------------------------

    def read_csv_flexible(self, path):
        try:
            df = pd.read_csv(path, sep=';', encoding='utf-8')
        except Exception:
            try:
                df = pd.read_csv(path, sep=';', encoding='latin-1')
            except Exception as e:
                raise Exception(f"Impossible de lire le fichier CSV (attendu séparateur ';' et encodage utf-8/latin-1): {e}")

        if df.shape[1] == 1:
            col0_name = str(df.columns[0])
            if ';' in col0_name:
                header_names = [h.strip() for h in col0_name.split(';')]
                df2 = df.iloc[:, 0].astype(str).str.split(';', expand=True)
                if df2.shape[1] >= len(header_names):
                    df2.columns = header_names
                    return df2
            first_cell = ''
            try:
                first_cell = '' if pd.isna(df.iloc[0, 0]) else str(df.iloc[0, 0])
            except Exception:
                first_cell = ''
            if ';' in first_cell:
                df2 = df.iloc[:, 0].astype(str).str.split(';', expand=True)
                header_names = [h.strip() for h in df2.iloc[0].tolist()]
                df2.columns = header_names
                df2 = df2.drop(index=0).reset_index(drop=True)
                return df2

        return df

    # Column detection
    def _normalize_col(self, col_name):
        s = str(col_name).lower()
        s = s.replace("\u00A0", " ").replace("\xa0", " ")
        return re.sub(r'[^0-9a-z]', '', s)

    def detect_primes_columns(self):
        # Détection stricte des colonnes attendues
        cols = self.primes_cols
        if not cols:
            return
        norm_map = {c: self._normalize_col(c) for c in cols}
        def find_exact(expected_name):
            key = re.sub(r'[^0-9a-z]', '', expected_name.lower())
            for c, n in norm_map.items():
                if n == key:
                    return c
            return None

        self.col_assurance = find_exact('Assurance')
        self.col_canton = find_exact('Canton')
        self.col_region = find_exact('Region')
        self.col_classe = find_exact("Classe d'age") or find_exact('Classe d age')
        self.col_accident = find_exact('Accident')
        self.col_franchise = find_exact('Franchise')
        self.col_modele = find_exact('Modele assurance') or find_exact('Modele')
        self.col_prime = find_exact('Prime')

    def detect_postal_columns(self):
        # Détection stricte des colonnes postales
        if self.df_postal is None:
            return
        cols = list(self.df_postal.columns)
        norm_map = {c: self._normalize_col(c) for c in cols}
        def find_exact(expected_name):
            key = re.sub(r'[^0-9a-z]', '', expected_name.lower())
            for c, n in norm_map.items():
                if n == key:
                    return c
            return None

        self.postal_col = find_exact('Code postal') or (cols[0] if cols else None)
        self.region_col = find_exact('Region') or (cols[-1] if cols else None)
        # Normaliser les colonnes
        if self.postal_col:
            self.df_postal[self.postal_col] = self.df_postal[self.postal_col].apply(normalise_codepostal)
        if self.region_col:
            self.df_postal[self.region_col] = self.df_postal[self.region_col].astype(str).str.strip()

    def open_postal_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        self.entry_postal.delete(0, tk.END)
        self.entry_postal.insert(0, path)
        try:
            df = self.read_csv_flexible(path)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lire le fichier postal CSV: {e}")
            return

        # In strict mode we expect a semicolon-separated file with multiple columns.
        if df.shape[1] == 1:
            messagebox.showerror("Erreur", "Le fichier postal semble ne pas être un CSV séparé par ';'. Veuillez fournir un fichier CSV avec des colonnes (Code postal;Commune;Region).")
            return

        self.df_postal = df
        self.detect_postal_columns()

    def open_primes_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        self.entry_primes.delete(0, tk.END)
        self.entry_primes.insert(0, path)
        try:
            df = self.read_csv_flexible(path)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lire le fichier primes CSV: {e}")
            return

        if df.shape[1] == 1:
            messagebox.showerror("Erreur", "Le fichier 'Primes' semble ne pas être un CSV séparé par ';'. Veuillez fournir un fichier CSV avec des colonnes.")
            return

        # Charger données et détecter colonnes
        self.df_primes = df
        self.primes_cols = self.df_primes.columns.tolist()
        self.detect_primes_columns()

        # Préparer les colonnes dérivées
        if self.col_franchise:
            self.df_primes["Franchise_int"] = self.df_primes[self.col_franchise].apply(fr_to_int_label)
        if self.col_assurance:
            assureurs = sorted(self.df_primes[self.col_assurance].dropna().unique().tolist())
            self.combo_assureur['values'] = assureurs
        if self.col_accident:
            vals = sorted(self.df_primes[self.col_accident].dropna().unique().tolist())
            if any("avec" in str(v).lower() for v in vals):
                self.var_accident.set("Avec")
            elif any("sans" in str(v).lower() for v in vals):
                self.var_accident.set("Sans")
        self.update_franchise_options()

    # -----------------------
    # UI helpers
    # -----------------------
    def toggle_prime_mode(self):
        mode = self.var_mode_prime.get()
        if mode == "manual":
            self.entry_prime_actuelle.config(state="normal")
            self.combo_assureur.config(state="disabled")
            self.combo_modele_assureur.config(state="disabled")
        else:
            self.entry_prime_actuelle.config(state="disabled")
            self.combo_assureur.config(state="readonly")
            self.combo_modele_assureur.config(state="readonly")

    def populate_models_for_assureur(self):
        if self.df_primes is None or not self.col_assurance or not self.col_modele:
            self.combo_modele_assureur['values'] = []
            return
        assureur = self.var_assureur_actuel.get().strip()
        if not assureur:
            self.combo_modele_assureur['values'] = []
            return
        df_tmp = self.df_primes[self.df_primes[self.col_assurance] == assureur]
        models = sorted(df_tmp[self.col_modele].dropna().unique().tolist())
        self.combo_modele_assureur['values'] = models
        if models:
            self.combo_modele_assureur.set(models[0])

    def update_franchise_options(self):
        # Récupère la chaîne saisie par l'utilisateur pour l'année de naissance (ex: "1999")
        year_str = self.var_birth_year.get().strip()

        # Tente de convertir la chaîne en entier et vérifie qu'elle est plausible
        try:
            birth_year = int(year_str)
            # On considère invalide toute année avant 1900 ou après l'année de référence
            if birth_year < 1900 or birth_year > ANNEE_REF:
                raise ValueError
        except Exception:
            # Si la conversion échoue ou l'année est invalide :
            # - vider la liste des valeurs de la combobox (aucune option disponible)
            # - réinitialiser la valeur sélectionnée (champ vide)
            # - et sortir de la fonction
            self.combo_franchise['values'] = []
            self.var_franchise.set("")
            return

        # Calculer l'âge que la personne aura pendant l'année de référence
        age = ANNEE_REF - birth_year

        # Choisir la liste de franchises selon que la personne est enfant ou adulte
        vals = FRANCHISES_ENFANT if age <= 18 else FRANCHISES_ADULTE

        # Convertir les valeurs en chaînes (ex: 300 -> "300") pour les afficher dans la combobox
        vals_str = [str(x) for x in vals]

        # Appliquer ces valeurs à la combobox (ce sont les options que l'utilisateur verra)
        self.combo_franchise['values'] = vals_str

        # Mettre la combobox en mode readonly pour empêcher la saisie libre
        # (l'utilisateur doit choisir parmi les options fournies)
        try:
            self.combo_franchise.config(state="readonly")
        except Exception:
            # Si la configuration échoue pour une raison quelconque, on ignore l'erreur
            pass

        # NE PAS forcer de valeur par défaut : si la valeur actuelle est vide ou invalide,
        # on laisse la combobox vide pour que l'utilisateur sélectionne lui-même.
        if not self.var_franchise.get() or self.var_franchise.get() not in vals_str:
            self.var_franchise.set("")

    # -----------------------
    # Calcul principal
    # -----------------------
    def calculer(self):
        if self.df_primes is None or self.df_postal is None:
            messagebox.showerror("Erreur", "Veuillez ouvrir les fichiers CSV 'Code_Postal_Region' et 'Primes'. Utilisez les boutons en haut.")
            return
        if self.df_primes.shape[1] == 1:
            messagebox.showerror("Erreur", "Le fichier 'Primes' semble ne pas être un CSV séparé par ';'. Veuillez fournir un fichier CSV avec des colonnes.")
            return

        col_region = self.col_region
        col_classe = self.col_classe
        col_accident = self.col_accident
        col_franchise = self.col_franchise
        col_modele = self.col_modele
        col_assurance = self.col_assurance
        col_canton = self.col_canton
        col_prime = self.col_prime

        if not col_prime:
            messagebox.showerror("Erreur", "Impossible de détecter la colonne 'Prime'. Vérifiez votre fichier.")
            return

        # lecture année de naissance -> âge
        birth_year_str = self.var_birth_year.get().strip()
        age = age_from_birth_year(birth_year_str)
        if age is None:
            messagebox.showerror("Erreur", "Année de naissance invalide. Entrez une année valide (ex: 1999).")
            return
        classe_age = classe_age_from_age(age)

        # code postal -> région
        code_postal = normalise_codepostal(self.var_postal.get().strip())
        df_match_postal = self.df_postal[self.df_postal[self.postal_col] == code_postal]
        if df_match_postal.empty:
            # diagnostic info to help the user/debug
            try:
                sample_vals = self.df_postal[self.postal_col].astype(str).head(20).tolist()
            except Exception:
                sample_vals = []
            sample_preview = ", ".join(sample_vals[:10]) + ("..." if len(sample_vals) > 10 else "")
            messagebox.showerror("Erreur", f"Code postal '{self.var_postal.get().strip()}' (normalisé = '{code_postal}') non trouvé dans {self.postal_col}. Exemple de valeurs présentes: {sample_preview}\nVérifiez le fichier chargé et le format du code postal (espaces, '.0', zéros initiaux).")
            return
        region_trouvee = str(df_match_postal.iloc[0][self.region_col]).strip()

        # Validation accident
        canton = self.var_canton.get().strip().upper()
        accident_input = self.var_accident.get().strip().lower()
        acc_val = None
        if col_accident:
            unique_acc = self.df_primes[col_accident].dropna().unique().tolist()
            acc_val = next((str(v) for v in unique_acc if accident_input in str(v).lower()), None)
            if acc_val is None:
                messagebox.showerror("Erreur", f"Valeur 'Accident' non reconnue. Valeurs possibles: {unique_acc[:6]}")
                return

        # Validation franchise
        fr = self.var_franchise.get().strip()
        try:
            fr_int = int(float(fr))
        except Exception:
            messagebox.showerror("Erreur", "Franchise invalide.")
            return
        valid_franchises = FRANCHISES_ENFANT if age <= 18 else FRANCHISES_ADULTE
        if fr_int not in valid_franchises:
            messagebox.showerror("Erreur", f"Franchise non autorisée. Valeurs autorisées: {valid_franchises}")
            return
        fr_label = franchise_label(fr_int)

        # Récupérer prime actuelle
        prime_actuelle = None
        prime_actuelle_source = None
        if self.var_mode_prime.get() == "manual":
            pa = self.var_prime_actuelle.get().strip()
            if pa:
                try:
                    prime_actuelle = float(pa)
                    prime_actuelle_source = "Saisie manuelle"
                except Exception:
                    messagebox.showwarning("Avertissement", "Prime actuelle invalide, ignorée.")
        else:
            # Prime depuis caisse + modèle sélectionnés
            assureur_sel = self.var_assureur_actuel.get().strip()
            modele_sel = self.var_modele_actuel.get().strip()
            if not assureur_sel or not modele_sel:
                messagebox.showerror("Erreur", "Veuillez sélectionner votre caisse et votre modèle actuels.")
                return
            df_tmp = self.df_primes.copy()
            if col_region:
                df_tmp = df_tmp[df_tmp[col_region].astype(str).str.strip() == str(region_trouvee)]
            if col_classe:
                df_tmp = df_tmp[df_tmp[col_classe].astype(str).str.replace("\u00A0", " ").str.strip() == classe_age]
            if col_canton and canton:
                df_tmp = df_tmp[df_tmp[col_canton].astype(str).str.upper() == canton]
            if acc_val is not None:
                df_tmp = df_tmp[df_tmp[col_accident] == acc_val]
            if "Franchise_int" in df_tmp.columns:
                df_tmp = df_tmp[df_tmp["Franchise_int"] == fr_int]
            elif col_franchise:
                df_tmp = df_tmp[df_tmp[col_franchise] == fr_label]
            if col_assurance:
                df_tmp = df_tmp[df_tmp[col_assurance] == assureur_sel]
            if col_modele:
                df_tmp = df_tmp[df_tmp[col_modele] == modele_sel]
            col_annee = next((c for c in self.df_primes.columns.tolist() if c.lower().startswith("ann")), None)
            if col_annee:
                df_tmp = df_tmp[df_tmp[col_annee] == ANNEE_REF]
            if not df_tmp.empty:
                prime_actuelle = float(df_tmp[col_prime].mean())
                prime_actuelle_source = f"Caisse+modèle ({assureur_sel} / {modele_sel})"
            else:
                messagebox.showwarning("Avertissement", "Aucune prime trouvée pour votre caisse/modèle avec les filtres sélectionnés.")


        # filtrage principal
        df_filtered = self.df_primes.copy()
        if col_region:
            df_filtered = df_filtered[df_filtered[col_region].astype(str).str.strip() == str(region_trouvee)]
        if col_classe:
            df_filtered = df_filtered[df_filtered[col_classe].astype(str).str.replace("\u00A0", " ").str.strip() == classe_age]
        if col_canton and canton:
            df_filtered = df_filtered[df_filtered[col_canton].astype(str).str.upper() == canton]
        if acc_val is not None:
            df_filtered = df_filtered[df_filtered[col_accident] == acc_val]
        if "Franchise_int" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["Franchise_int"] == fr_int]
        elif col_franchise:
            df_filtered = df_filtered[df_filtered[col_franchise] == fr_label]
        col_annee = next((c for c in self.df_primes.columns.tolist() if c.lower().startswith("ann")), None)
        if col_annee:
            df_filtered = df_filtered[df_filtered[col_annee] == ANNEE_REF]

        if df_filtered.empty:
            messagebox.showinfo("Résultat", "Aucun tarif disponible pour la combinaison demandée.")
            self.txt_result.delete("1.0", tk.END)
            for i in self.tree.get_children():
                self.tree.delete(i)
            return

        # groupby assurance+modele si disponibles
        group_cols = []
        if col_assurance:
            group_cols.append(col_assurance)
        if col_modele:
            group_cols.append(col_modele)

        # Default to mean aggregation when grouping by assurance+modele
        agg_func = 'mean'
        if group_cols:
            df_grouped = df_filtered.groupby(group_cols, as_index=False)[col_prime].agg(agg_func)
            df_grouped = df_grouped.sort_values(col_prime).reset_index(drop=True)
            best = df_grouped.iloc[0]
            assurance_best = best[col_assurance] if col_assurance else ""
            modele_best = best[col_modele] if col_modele else ""
            prime_best = float(best[col_prime])
        else:
            row = df_filtered.loc[df_filtered[col_prime].idxmin()]
            assurance_best = row[col_assurance] if col_assurance else ""
            modele_best = row[col_modele] if col_modele else ""
            prime_best = float(row[col_prime])

        # afficher résultat
        self.txt_result.delete("1.0", tk.END)
        res_lines = []
        if assurance_best:
            res_lines.append(f"Assurance: {assurance_best}")
        if modele_best:
            res_lines.append(f"Modèle: {modele_best}")
        res_lines.append(f"Prime associée: {prime_best:.2f} CHF / mois")
        if prime_actuelle is not None:
            if prime_actuelle_source:
                res_lines.append(f"Prime actuelle utilisée: {prime_actuelle:.2f} CHF / mois  ({prime_actuelle_source})")
            else:
                res_lines.append(f"Prime actuelle utilisée: {prime_actuelle:.2f} CHF / mois")
            econ_m = prime_actuelle - prime_best
            econ_y = econ_m * 12
            res_lines.append(f"Économie vs votre prime actuelle: {econ_m:.2f} CHF / mois  |  {econ_y:.2f} CHF / an")
        self.txt_result.insert("1.0", "\n".join(res_lines))

        # remplir top5 avec colonne économie
        for i in self.tree.get_children():
            self.tree.delete(i)

        def format_economie(p_model):
            if prime_actuelle is None:
                return ""
            econ_m = prime_actuelle - p_model
            econ_y = econ_m * 12
            return f"{econ_m:.2f} CHF / mois ({econ_y:.2f} CHF / an)"

        if group_cols:
            top5 = df_grouped.head(5)
            for idx, r in top5.iterrows():
                a = r[col_assurance] if col_assurance else ""
                m = r[col_modele] if col_modele else ""
                p = float(r[col_prime])
                econ = format_economie(p)
                self.tree.insert("", "end", values=(a, m, f"{p:.2f}", econ))
        else:
            top5 = df_filtered.sort_values(col_prime).head(5)
            for idx, r in top5.iterrows():
                a = r[col_assurance] if col_assurance else ""
                m = r[col_modele] if col_modele else ""
                p = float(r[col_prime])
                econ = format_economie(p)
                self.tree.insert("", "end", values=(a, m, f"{p:.2f}", econ))

# -----------------------
# Lancer l'application
# -----------------------
if __name__ == "__main__":
    app = CalculateurLaMalApp()
    app.mainloop()
# Calculateur LAMal (Assurance maladie suisse)

**Auteur :** Ruben ten Cate
**Version :** v5.0 (17.12.2025)

## 📌 Description

Le **Calculateur LAMal** est une application desktop développée en **Python avec Tkinter**. Elle permet de comparer les primes d’assurance maladie obligatoire (LAMal) en Suisse et d’identifier :

* l’offre **la moins chère** selon le profil de l’utilisateur
* le **Top 5 des meilleures offres**
* les **économies potentielles** par rapport à la prime actuelle

L’application se base sur des fichiers **CSV officiels ou personnalisés** contenant les primes et les correspondances **code postal → région**.

---

## 🖥️ Fonctionnalités principales

* Interface graphique simple (Tkinter)
* Chargement flexible de fichiers CSV (`;`, UTF-8 ou Latin-1)
* Détection automatique des colonnes (assurance, franchise, région, prime, etc.)
* Calcul selon :

  * âge (enfant / adulte)
  * code postal → région
  * canton
  * franchise
  * accident (avec / sans)
* Deux modes pour la prime actuelle :

  * saisie manuelle
  * sélection de la caisse + modèle existants
* Affichage :

  * meilleure offre
  * Top 5 des offres
  * économies mensuelles et annuelles

---

## 📂 Structure du projet

```
Calculateur_LAMal/
│
├── Calculateur_LAMal_perso.py   # Fichier principal de l'application
├── utils.py                    # Fonctions utilitaires (âge, franchises, normalisation)
├── assets/
│   └── letter_r.ico            # Icône de l'application
└── README.md                   # Documentation
```

---

## 📊 Fichiers CSV requis

Les deux fichiers .csv a charger dans le programme se trouve dans ce répertoire GitHub

Les données contenus dans ce fichier sont extraites des données de l'OFSP en Suisse

---

## 🧮 Logique de calcul

1. L’utilisateur saisit :

   * année de naissance
   * code postal
   * canton
   * accident (avec / sans)
   * franchise
2. L’âge est calculé automatiquement à partir de l’année de référence (`ANNEE_REF`).
3. La région est déterminée via le fichier postal.
4. Les primes sont filtrées selon :

   * région
   * classe d’âge
   * canton
   * accident
   * franchise
   * année (si présente)
5. Les primes sont regroupées par **assurance + modèle**.
6. La prime la plus basse est sélectionnée.
7. Les économies sont calculées si une prime actuelle est fournie.

---

## ⚙️ Dépendances

Bibliothèques Python nécessaires :

```bash
pip install pandas
```

Les bibliothèques suivantes sont incluses par défaut avec Python :

* tkinter
* os
* re

---

## ▶️ Lancer l’application

Depuis le dossier du projet :

```bash
python Calculateur_LAMal_perso.py
```

---

## ❗ Remarques importantes

* Les fichiers CSV doivent être **cohérents et bien formatés**.
* Les franchises autorisées sont automatiquement limitées selon l’âge.
* L’application est prévue pour un **usage personnel ou pédagogique**.

---

## 📈 Améliorations possibles

* Export des résultats en PDF ou CSV
* Recherche automatique des fichiers officiels
* Version exécutable (.exe)
* Interface plus moderne (customTkinter)

---

## 📜 Licence

Projet personnel – libre d’utilisation à des fins éducatives.


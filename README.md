# Assignment 1 - IA & ML (ENSI II2) : Systèmes experts & algorithmes de recherche

Application CLI en Python 3.8+ avec deux modules :
1. **Systèmes experts** : base de faits/règles, chaînage avant et arrière avec trace des étapes, choix/changement de l'objectif sans relancer, ajout/modification/suppression de faits et règles, sauvegarde/chargement JSON.
2. **Algorithmes de recherche** : graphe orienté pondéré construit par l'utilisateur, heuristiques h(n),
   - non informés : BFS, DFS, UCS, DLS, IDS
   - informés : Greedy, A*, Hill Climbing
   - affichage étape par étape (visités + frontière), chemin, coût, cas "aucun chemin", comparaison des performances, dessin matplotlib avec chemin en rouge.

## Prérequis
- Python 3.8+
- (optionnel) `pip install matplotlib` pour le dessin du graphe

## Exécution
```bash
python main.py
```
Tests : `python -m unittest test_main.py -v`

## Structure
- `main.py` : tout le code (module 1, module 2, menu principal)
- `test_main.py` : tests unitaires
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assignment 1 - IA & ML (ENSI II2)
Module 1 : Systèmes experts (chaînage avant / arrière)
Module 2 : Algorithmes de recherche (BFS, DFS, UCS, DLS, IDS, Greedy, A*, Hill Climbing)
Interface : CLI (+ dessin matplotlib optionnel du graphe)
"""
import heapq
import itertools
import json
import math
import time
from collections import deque
from functools import partial

INF = float("inf")


# ======================================================================
#  Utilitaires de saisie
# ======================================================================
def saisir(msg):
    return input(msg).strip()


def saisir_choix(msg, valides):
    while True:
        c = saisir(msg)
        if c in valides:
            return c
        print("  Choix invalide.")


def saisir_nombre(msg):
    while True:
        try:
            x = float(saisir(msg).replace(",", "."))
            return int(x) if x.is_integer() else x
        except ValueError:
            print("  Nombre invalide.")


def parse_conditions(s):
    s = s.replace(" ET ", ",").replace(" et ", ",")
    return [c.strip() for c in s.split(",") if c.strip()]


def pause_entree():
    input("   [Entrée pour continuer]")


# ======================================================================
#  MODULE 1 : SYSTÈMES EXPERTS
# ======================================================================
def fmt_rule(i, r):
    return f"R{i + 1}: SI {' ET '.join(r['if'])} ALORS {r['then']}"


class ExpertSystem:
    """Base de faits (ensemble) + base de règles (liste de {'if': [...], 'then': x})."""

    def __init__(self):
        self.charger_defaut()

    def charger_defaut(self):
        self.facts = {"fievre", "toux", "fatigue", "hydratation"}
        self.rules = [
            {"if": ["fievre", "toux"], "then": "grippe_possible"},
            {"if": ["grippe_possible", "fatigue"], "then": "grippe"},
            {"if": ["grippe"], "then": "repos"},
            {"if": ["mal_gorge", "fievre"], "then": "angine"},
            {"if": ["grippe", "courbatures"], "then": "grippe_forte"},
            {"if": ["repos", "hydratation"], "then": "guerison"},
        ]

    # ---------- affichage ----------
    def afficher(self):
        print("\nBase de faits :", ", ".join(sorted(self.facts)) or "(vide)")
        print("Base de règles :")
        if not self.rules:
            print("  (aucune)")
        for i, r in enumerate(self.rules):
            print("  " + fmt_rule(i, r))

    def univers(self):
        s = set(self.facts)
        for r in self.rules:
            s.update(r["if"])
            s.add(r["then"])
        return sorted(s)

    # ---------- chaînage avant ----------
    def chainage_avant(self, but, pause=lambda: None):
        faits = set(self.facts)
        utilisees = set()
        n = 0
        print(f"\n[Chaînage avant] but = {but}")
        print(f"Faits initiaux : {sorted(faits)}")
        if but in faits:
            print(f"✔ '{but}' est déjà dans la base de faits.")
            return True
        progres = True
        while progres:
            progres = False
            for i, r in enumerate(self.rules):
                if i in utilisees or not all(c in faits for c in r["if"]):
                    continue
                utilisees.add(i)
                if r["then"] in faits:
                    continue
                faits.add(r["then"])
                n += 1
                progres = True
                print(f"Étape {n}: {fmt_rule(i, r)}  =>  +'{r['then']}'")
                print(f"         faits : {sorted(faits)}")
                pause()
                if but in faits:
                    print(f"✔ But '{but}' démontré en {n} étape(s).")
                    return True
                break
        print(f"✘ But '{but}' non démontré (point fixe atteint, plus aucune règle applicable).")
        return False

    # ---------- chaînage arrière ----------
    def chainage_arriere(self, but, pause=lambda: None):
        faits = set(self.facts)
        print(f"\n[Chaînage arrière] but = {but}")

        def prouver(g, prof, pile):
            pad = "  " * prof
            if g in faits:
                print(f"{pad}✔ '{g}' est dans la base de faits")
                return True
            if g in pile:
                print(f"{pad}✘ cycle détecté sur '{g}'")
                return False
            candidates = [(i, r) for i, r in enumerate(self.rules) if r["then"] == g]
            if not candidates:
                print(f"{pad}✘ '{g}' : ni fait, ni règle qui le conclut")
                return False
            for i, r in candidates:
                print(f"{pad}? sous-but '{g}' : essai de {fmt_rule(i, r)}")
                pause()
                ok = True
                for c in r["if"]:
                    if not prouver(c, prof + 1, pile | {g}):
                        ok = False
                        break
                if ok:
                    print(f"{pad}✔ '{g}' prouvé grâce à R{i + 1}")
                    faits.add(g)
                    return True
            print(f"{pad}✘ '{g}' non prouvable")
            return False

        res = prouver(but, 0, frozenset())
        print(f"{'✔ But démontré.' if res else '✘ But non démontré.'}")
        return res

    # ---------- sauvegarde ----------
    def sauvegarder(self, fichier):
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump({"facts": sorted(self.facts), "rules": self.rules}, f, ensure_ascii=False, indent=2)

    def charger(self, fichier):
        with open(fichier, encoding="utf-8") as f:
            d = json.load(f)
        self.facts = set(d["facts"])
        self.rules = d["rules"]


def menu_gerer_base(es):
    while True:
        print("\n--- Gérer la base ---")
        print("a. Ajouter un fait        b. Supprimer un fait")
        print("c. Ajouter une règle      d. Supprimer une règle")
        print("e. Modifier une règle     0. Retour")
        c = saisir_choix("Choix : ", list("abcde0"))
        if c == "0":
            return
        if c == "a":
            f = saisir("Nouveau fait : ")
            if f:
                es.facts.add(f)
        elif c == "b":
            f = saisir("Fait à supprimer : ")
            if f in es.facts:
                es.facts.discard(f)
            else:
                print("  Fait introuvable.")
        elif c == "c":
            conds = parse_conditions(saisir("Conditions (séparées par des virgules) : "))
            concl = saisir("Conclusion : ")
            if conds and concl:
                es.rules.append({"if": conds, "then": concl})
            else:
                print("  Règle invalide.")
        elif c in "de":
            es.afficher()
            if not es.rules:
                continue
            n = saisir_nombre("Numéro de la règle : ")
            if not (1 <= n <= len(es.rules)):
                print("  Numéro invalide.")
                continue
            if c == "d":
                del es.rules[n - 1]
            else:
                r = es.rules[n - 1]
                conds = saisir(f"Conditions [{', '.join(r['if'])}] : ")
                concl = saisir(f"Conclusion [{r['then']}] : ")
                if conds:
                    r["if"] = parse_conditions(conds)
                if concl:
                    r["then"] = concl


def menu_expert(es):
    but, methode, pas = None, "avant", True
    while True:
        print("\n===== Systèmes experts =====")
        print(f"(but : {but or 'non défini'} | méthode : chaînage {methode} | pas-à-pas : {'oui' if pas else 'non'})")
        print("1. Afficher faits et règles")
        print("2. Choisir l'objectif")
        print("3. Choisir la méthode de chaînage")
        print("4. Lancer le raisonnement")
        print("5. Activer/désactiver le mode pas-à-pas")
        print("6. Gérer la base (ajout/modif/suppression)")
        print("7. Sauvegarder la base   8. Charger une base   9. Base par défaut")
        print("0. Retour")
        c = saisir_choix("Choix : ", list("0123456789"))
        if c == "0":
            return
        elif c == "1":
            es.afficher()
        elif c == "2":
            u = es.univers()
            for i, x in enumerate(u, 1):
                print(f"  {i}. {x}")
            s = saisir("Numéro ou nom du fait à démontrer : ")
            if s.isdigit() and 1 <= int(s) <= len(u):
                s = u[int(s) - 1]
            if s:
                but = s
                if but in es.facts:
                    print(f"  ℹ '{but}' est déjà présent dans la base de faits.")
                else:
                    print(f"  '{but}' n'est pas dans la base de faits.")
        elif c == "3":
            print("1. Chaînage avant   2. Chaînage arrière")
            methode = "avant" if saisir_choix("Choix : ", ["1", "2"]) == "1" else "arrière"
        elif c == "4":
            if not but:
                print("  Choisissez d'abord un objectif (option 2).")
                continue
            p = pause_entree if pas else (lambda: None)
            if methode == "avant":
                es.chainage_avant(but, p)
            else:
                es.chainage_arriere(but, p)
        elif c == "5":
            pas = not pas
        elif c == "6":
            menu_gerer_base(es)
        elif c == "7":
            fn = saisir("Fichier [base_connaissances.json] : ") or "base_connaissances.json"
            es.sauvegarder(fn)
            print("  Sauvegardé.")
        elif c == "8":
            fn = saisir("Fichier [base_connaissances.json] : ") or "base_connaissances.json"
            try:
                es.charger(fn)
                print("  Chargé.")
            except (OSError, ValueError, KeyError) as e:
                print(f"  Erreur de chargement : {e}")
        elif c == "9":
            es.charger_defaut()
            print("  Base par défaut rechargée.")


# ======================================================================
#  MODULE 2 : ALGORITHMES DE RECHERCHE
# ======================================================================
class Graph:
    """Graphe orienté pondéré : adj[u][v] = coût ; h[u] = heuristique."""

    def __init__(self):
        self.adj, self.h = {}, {}
        self.start = self.goal = None

    @staticmethod
    def exemple():
        g = Graph()
        for u, v, c in [("S", "A", 1), ("S", "B", 4), ("A", "B", 2), ("A", "C", 5), ("A", "D", 12),
                        ("B", "C", 2), ("C", "D", 3), ("C", "G", 8), ("D", "G", 3)]:
            g.add_edge(u, v, c)
        g.h = {"S": 9, "A": 8, "B": 6, "C": 5, "D": 2, "G": 0}
        g.start, g.goal = "S", "G"
        return g

    def add_vertex(self, v):
        self.adj.setdefault(v, {})

    def add_edge(self, u, v, c):
        self.add_vertex(u)
        self.add_vertex(v)
        self.adj[u][v] = c

    def remove_vertex(self, v):
        self.adj.pop(v, None)
        for u in self.adj:
            self.adj[u].pop(v, None)
        self.h.pop(v, None)
        if self.start == v:
            self.start = None
        if self.goal == v:
            self.goal = None

    def remove_edge(self, u, v):
        return self.adj.get(u, {}).pop(v, None) is not None

    def cout(self, path):
        return sum(self.adj[a][b] for a, b in zip(path, path[1:]))

    def afficher(self):
        print("\nGraphe orienté pondéré :")
        if not self.adj:
            print("  (vide)")
        for u, nb in self.adj.items():
            tags = ""
            if u == self.start:
                tags += " [INITIAL]"
            if u == self.goal:
                tags += " [OBJECTIF]"
            h = f" h={self.h[u]}" if u in self.h else ""
            arcs = ", ".join(f"--{c}--> {v}" for v, c in nb.items()) or "(aucun arc sortant)"
            print(f"  {u}{h}{tags} : {arcs}")

    def sauvegarder(self, fichier):
        d = {"edges": [[u, v, c] for u, nb in self.adj.items() for v, c in nb.items()],
             "vertices": list(self.adj), "h": self.h, "start": self.start, "goal": self.goal}
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

    def charger(self, fichier):
        with open(fichier, encoding="utf-8") as f:
            d = json.load(f)
        self.adj, self.h = {}, d.get("h", {})
        for v in d.get("vertices", []):
            self.add_vertex(v)
        for u, v, c in d["edges"]:
            self.add_edge(u, v, c)
        self.start, self.goal = d.get("start"), d.get("goal")


def dessiner(g, path=None):
    """Dessin matplotlib (optionnel) : départ vert, objectif rouge, chemin en rouge."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib non installé (pip install matplotlib) -> affichage texte uniquement.")
        return
    nodes = list(g.adj)
    if not nodes:
        print("  Graphe vide.")
        return
    n = len(nodes)
    pos = {v: (math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n)) for i, v in enumerate(nodes)}
    pe = set(zip(path, path[1:])) if path else set()
    fig, ax = plt.subplots(figsize=(7, 7))
    for u in nodes:
        for v, c in g.adj[u].items():
            (x1, y1), (x2, y2) = pos[u], pos[v]
            col = "red" if (u, v) in pe else "gray"
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="->", color=col, lw=2.5 if col == "red" else 1, shrinkA=20, shrinkB=20))
            ax.text((x1 + x2) / 2, (y1 + y2) / 2, str(c), color=col, fontsize=9)
    for v, (x, y) in pos.items():
        couleur = "lightgreen" if v == g.start else "salmon" if v == g.goal else "lightblue"
        ax.scatter(x, y, s=1000, c=couleur, edgecolors="black", zorder=3)
        ax.text(x, y, v + (f"\nh={g.h[v]}" if v in g.h else ""), ha="center", va="center", zorder=4, fontsize=9)
    ax.set_title("Graphe" + (" - chemin : " + " -> ".join(path) if path else ""))
    ax.axis("off")
    plt.show()


class Tracer:
    """Affiche (ou non) les étapes de l'exploration."""

    def __init__(self, verbose=True, pas_a_pas=False):
        self.verbose, self.pas, self.k, self.visited, self.expansions = verbose, pas_a_pas, 0, [], 0

    def nouvelle_ronde(self):
        self.visited = []

    def step(self, u, frontier):
        self.k += 1
        self.expansions += 1
        self.visited.append(u)
        if self.verbose:
            print(f"Étape {self.k:>2} | exploration de {u}")
            print(f"          visités   : {self.visited}")
            print(f"          frontière : {frontier}")
            if self.pas:
                pause_entree()


def chemin(parent, t):
    p = []
    while t is not None:
        p.append(t)
        t = parent[t]
    return p[::-1]


# ---------- recherche non informée ----------
def bfs(g, s, t, tr):
    parent, fr = {s: None}, deque([s])
    while fr:
        u = fr.popleft()
        if u != t:
            for v in g.adj[u]:
                if v not in parent:
                    parent[v] = u
                    fr.append(v)
        tr.step(u, list(fr))
        if u == t:
            return chemin(parent, t)
    return None


def dfs(g, s, t, tr):
    stack, vis = [(s, [s])], set()
    while stack:
        u, p = stack.pop()
        if u in vis:
            continue
        vis.add(u)
        if u != t:
            for v in reversed(list(g.adj[u])):
                if v not in vis:
                    stack.append((v, p + [v]))
        tr.step(u, [x for x, _ in reversed(stack)])
        if u == t:
            return p
    return None


def best_first(g, s, t, tr, prio, reopen):
    """Générique : UCS (g), Greedy (h), A* (g+h)."""
    cnt = itertools.count()
    best, parent, closed = {s: 0}, {s: None}, set()
    heap = [(prio(s, 0), next(cnt), s, 0)]
    while heap:
        f, _, u, gc = heapq.heappop(heap)
        if gc > best.get(u, INF) or (u in closed and not reopen):
            continue
        closed.add(u)
        if u != t:
            for v, c in g.adj[u].items():
                ng = gc + c
                meilleur = (ng < best.get(v, INF)) if reopen else (v not in best)
                if meilleur:
                    best[v], parent[v] = ng, u
                    heapq.heappush(heap, (prio(v, ng), next(cnt), v, ng))
        front = [f"{n}({round(p, 2)})" for p, _, n, c in sorted(heap) if c <= best.get(n, INF)]
        tr.step(u, front)
        if u == t:
            return chemin(parent, t)
    return None


def ucs(g, s, t, tr):
    return best_first(g, s, t, tr, lambda n, gc: gc, True)


def greedy(g, s, t, tr):
    return best_first(g, s, t, tr, lambda n, gc: g.h.get(n, 0), False)


def astar(g, s, t, tr):
    return best_first(g, s, t, tr, lambda n, gc: gc + g.h.get(n, 0), True)


def dls_core(g, s, t, limit, tr):
    stack, cutoff = [(s, [s])], False
    while stack:
        u, p = stack.pop()
        if u != t and len(p) - 1 < limit:
            for v in reversed(list(g.adj[u])):
                if v not in p:
                    stack.append((v, p + [v]))
        elif u != t and g.adj[u]:
            cutoff = True
        tr.step(u, [x for x, _ in reversed(stack)])
        if u == t:
            return p, False
    return None, cutoff


def dls(g, s, t, tr, limit=3):
    return dls_core(g, s, t, limit, tr)[0]


def ids(g, s, t, tr):
    for lim in range(len(g.adj) + 1):
        if tr.verbose:
            print(f"--- Itération : limite de profondeur = {lim} ---")
        tr.nouvelle_ronde()
        p, cut = dls_core(g, s, t, lim, tr)
        if p:
            return p
        if not cut:
            return None
    return None


# ---------- recherche informée (en plus de Greedy et A*) ----------
def hill_climbing(g, s, t, tr):
    u, p = s, [s]
    while True:
        nb = [v for v in g.adj[u] if v not in p]
        tr.step(u, sorted(nb, key=lambda v: g.h.get(v, 0)))
        if u == t:
            return p
        if not nb:
            print("  (Hill Climbing : bloqué, aucun voisin)") if tr.verbose else None
            return None
        b = min(nb, key=lambda v: g.h.get(v, 0))
        if g.h.get(b, 0) >= g.h.get(u, 0):
            print("  (Hill Climbing : minimum local atteint)") if tr.verbose else None
            return None
        u = b
        p.append(u)


NON_INFORMES = {"1": ("BFS - largeur d'abord", bfs), "2": ("DFS - profondeur d'abord", dfs),
                "3": ("UCS - coût uniforme", ucs), "4": ("DLS - profondeur limitée", dls),
                "5": ("IDS - approfondissement itératif", ids)}
INFORMES = {"1": ("Greedy - meilleur d'abord", greedy), "2": ("A*", astar),
            "3": ("Hill Climbing", hill_climbing)}


def executer(g, fn, verbose=True, pas=False):
    tr = Tracer(verbose, pas)
    t0 = time.perf_counter()
    p = fn(g, g.start, g.goal, tr)
    dt = time.perf_counter() - t0
    return {"path": p, "cost": g.cout(p) if p else None, "exp": tr.expansions, "time": dt}


def verifier(g, informe):
    if not g.start or g.start not in g.adj or not g.goal or g.goal not in g.adj:
        print("  Définissez un état initial et un état objectif valides.")
        return False
    if informe:
        manquants = [v for v in g.adj if v not in g.h]
        if manquants:
            print(f"  ⚠ Heuristique manquante pour {manquants} (valeur 0 utilisée).")
    return True


def lancer_recherche(g):
    print("\n1. Recherche non informée (aveugle)\n2. Recherche informée (heuristique)")
    informe = saisir_choix("Type : ", ["1", "2"]) == "2"
    table = INFORMES if informe else NON_INFORMES
    for k, (nom, _) in table.items():
        print(f"  {k}. {nom}")
    k = saisir_choix("Algorithme : ", list(table))
    nom, fn = table[k]
    if not verifier(g, informe):
        return
    if fn is dls:
        fn = partial(dls, limit=int(saisir_nombre("Limite de profondeur : ")))
    pas = saisir_choix("Mode pas-à-pas ? (o/n) : ", ["o", "n"]) == "o"
    print(f"\n=== {nom} ===\nÉtat initial : {g.start} | État objectif : {g.goal}")
    r = executer(g, fn, True, pas)
    if r["path"]:
        print(f"\n✔ Chemin trouvé : {' -> '.join(r['path'])}")
        print(f"  Coût total : {r['cost']} | Nœuds explorés : {r['exp']}")
    else:
        print("\n✘ Aucun chemin n'a été trouvé.")
    if saisir_choix("Afficher le graphe (matplotlib) avec le chemin ? (o/n) : ", ["o", "n"]) == "o":
        dessiner(g, r["path"])


def comparer(g):
    if not verifier(g, True):
        return
    print(f"\n{'Algorithme':<34}{'Chemin':<26}{'Coût':<8}{'Explorés':<10}{'Temps (ms)'}")
    for table in (NON_INFORMES, INFORMES):
        for nom, fn in table.values():
            if fn is dls:
                fn = partial(dls, limit=len(g.adj))
            r = executer(g, fn, False)
            ch = " ".join(r["path"]) if r["path"] else "aucun"
            print(f"{nom:<34}{ch:<26}{str(r['cost']):<8}{r['exp']:<10}{r['time'] * 1000:.3f}")


def menu_construire(g):
    while True:
        print("\n--- Construction du graphe ---")
        print("a. Ajouter un sommet     b. Ajouter un arc (avec coût)")
        print("c. Définir h(n)          d. Définir l'état initial   e. Définir l'état objectif")
        print("f. Supprimer un sommet   g. Supprimer un arc")
        print("h. Charger l'exemple     i. Vider le graphe          0. Retour")
        c = saisir_choix("Choix : ", list("abcdefghi0"))
        if c == "0":
            return
        if c == "a":
            v = saisir("Nom du sommet : ")
            if v:
                g.add_vertex(v)
        elif c == "b":
            u, v = saisir("Origine : "), saisir("Destination : ")
            if not u or not v:
                continue
            cout = saisir_nombre("Coût : ")
            if cout < 0:
                print("  Coût négatif refusé.")
                continue
            g.add_edge(u, v, cout)
        elif c == "c":
            v = saisir("Sommet : ")
            if v in g.adj:
                g.h[v] = saisir_nombre(f"h({v}) = ")
            else:
                print("  Sommet inconnu.")
        elif c in "de":
            v = saisir("Sommet : ")
            if v in g.adj:
                if c == "d":
                    g.start = v
                else:
                    g.goal = v
            else:
                print("  Sommet inconnu.")
        elif c == "f":
            g.remove_vertex(saisir("Sommet à supprimer : "))
        elif c == "g":
            if not g.remove_edge(saisir("Origine : "), saisir("Destination : ")):
                print("  Arc introuvable.")
        elif c == "h":
            g.__dict__.update(Graph.exemple().__dict__)
        elif c == "i":
            g.__dict__.update(Graph().__dict__)
        g.afficher()


def menu_recherche(g):
    while True:
        print("\n===== Algorithmes de recherche =====")
        print("1. Construire / modifier le graphe")
        print("2. Afficher le graphe (texte + graphique)")
        print("3. Lancer une recherche")
        print("4. Comparer les performances de tous les algorithmes")
        print("5. Sauvegarder le graphe   6. Charger un graphe")
        print("0. Retour")
        c = saisir_choix("Choix : ", list("0123456"))
        if c == "0":
            return
        elif c == "1":
            g.afficher()
            menu_construire(g)
        elif c == "2":
            g.afficher()
            if saisir_choix("Dessin matplotlib ? (o/n) : ", ["o", "n"]) == "o":
                dessiner(g)
        elif c == "3":
            lancer_recherche(g)
        elif c == "4":
            comparer(g)
        elif c == "5":
            fn = saisir("Fichier [graphe.json] : ") or "graphe.json"
            g.sauvegarder(fn)
            print("  Sauvegardé.")
        elif c == "6":
            fn = saisir("Fichier [graphe.json] : ") or "graphe.json"
            try:
                g.charger(fn)
                print("  Chargé.")
            except (OSError, ValueError, KeyError) as e:
                print(f"  Erreur de chargement : {e}")


# ======================================================================
#  MENU PRINCIPAL
# ======================================================================
def main():
    es, g = ExpertSystem(), Graph.exemple()
    try:
        while True:
            print("\n===== Menu principal =====")
            print("1. Systèmes experts\n2. Algorithmes de recherche\n3. Quitter")
            c = saisir_choix("Choix : ", ["1", "2", "3"])
            if c == "1":
                menu_expert(es)
            elif c == "2":
                menu_recherche(g)
            else:
                print("Au revoir !")
                break
    except (KeyboardInterrupt, EOFError):
        print("\nAu revoir !")


if __name__ == "__main__":
    main()
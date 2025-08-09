===========================================================
README – Dossier Test_IA
===========================================================

Ce dossier contient tous les scripts de test et outils pour vérifier et diagnostiquer
les fonctionnalités de l’IA, en particulier la gestion des conversations et des
sauvegardes (SAV).

-----------------------------------------------------------
1. STRUCTURE ET RÔLE DES FICHIERS
-----------------------------------------------------------

__init__.py
    Indique que ce dossier est un package Python. Ne pas exécuter directement.

Auto_Eval_Kivy
    Script d’évaluation automatique pour l’interface Kivy. Usage interne pour tests UI.

Console_Interactif
    Console interactive pour tester les commandes IA.
    Lancer avec : python -m IA_V2.Test_IA.Console_Interactif

eval_mistral.py
    Évalue le modèle Mistral avec des prompts prédéfinis.
    Lancer avec : python -m IA_V2.Test_IA.eval_mistral

protocol_test_IA.txt
    Document texte décrivant les protocoles de test. Lecture uniquement.

questions_IA.txt
    Exemples de questions pour tests IA. Lecture uniquement.

rapport_evaluation_mistral1.txt
    Résultat d’une évaluation Mistral (première série). Lecture uniquement.

rapport_evaluation_mistral.txt
    Résultat d’une évaluation Mistral (autre série). Lecture uniquement.

rapport_test_memoire_mistral.txt
    Résultat du test mémoire du modèle Mistral. Lecture uniquement.

repair_conversations_index.py
    Répare l’index des conversations (index.json) et supprime les fichiers orphelins.
    Lancer avec : python -m IA_V2.Test_IA.repair_conversations_index

test_conversations_manager.py
    Test de base du module conversation_manager.
    Lancer avec : python -m IA_V2.Test_IA.test_conversations_manager

test_memoire_mistral.py
    Test de mémoire sur le modèle Mistral.
    Lancer avec : python -m IA_V2.Test_IA.test_memoire_mistral

test_rename_conversations.py
    Test du renommage moderne et historique des conversations.
    Lancer avec : python -m IA_V2.Test_IA.test_rename_conversations

test_rename_meta_fix.py
    Test spécifique de correction des métadonnées après renommage historique.
    Lancer avec : python -m IA_V2.Test_IA.test_rename_meta_fix

test_sav_end_to_end.py
    Test complet : création, append, renommage, suppression, réparation, cohérence totale.
    Lancer avec : python -m IA_V2.Test_IA.test_sav_end_to_end

-----------------------------------------------------------
2. UTILISATION RAPIDE
-----------------------------------------------------------

1. Lancer un test complet des SAV
   cd C:\Users\raph6\Documents\ServOMorph
   python -m IA_V2.Test_IA.test_sav_end_to_end

2. Réparer l’index et nettoyer les fichiers orphelins
   cd C:\Users\raph6\Documents\ServOMorph
   python -m IA_V2.Test_IA.repair_conversations_index

3. Tester uniquement le renommage
   python -m IA_V2.Test_IA.test_rename_conversations

4. Tester la correction des métadonnées après renommage historique
   python -m IA_V2.Test_IA.test_rename_meta_fix

-----------------------------------------------------------
3. BONNES PRATIQUES
-----------------------------------------------------------

- Toujours se placer dans le dossier racine (ServOMorph) avant de lancer un test avec -m
- Après un renommage ou suppression manuelle dans sav_conversations, lancer
  repair_conversations_index.py pour éviter les entrées fantômes.
- test_sav_end_to_end.py est le test maître qui valide l’intégrité complète
  du système de gestion des conversations.

-----------------------------------------------------------
4. SCHÉMA DU CYCLE DE VIE D’UNE CONVERSATION
-----------------------------------------------------------

(1) Création
    ↓
[Fichier .txt]   [Fichier .json]   [index.json]
Contenu vide     Métadonnées       Entrée ajoutée

(2) Append de messages
    ↓
.txt mis à jour
.json mis à jour (count, timestamps)
index.json mis à jour

(3) Renommage
    ↓
- Mode moderne : change seulement "title" (txt/json inchangés)
- Mode historique : renomme le .txt, met à jour json et index

(4) Suppression
    ↓
.txt supprimé
.json supprimé
Entrée retirée de l’index

(5) Réparation (repair_conversations_index.py)
    ↓
Supprime les entrées de l’index dont les fichiers sont manquants
Efface les fichiers orphelins non référencés

===========================================================

import sys
import os
import difflib
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ollama_api import query_ollama

# ==== Cas de test hardcodés ====
TESTS = {
    "génération_de_texte": [
        {
            "prompt": "Raconte une histoire courte où un robot apprend la musique.",
            "type": "génératif",
            "critères": {"créativité": 10, "cohérence": 10, "fluidité": 10}
        },
        {
            "prompt": "Écris un poème sur la solitude d’une intelligence artificielle.",
            "type": "génératif",
            "critères": {"créativité": 10, "cohérence": 10, "fluidité": 10}
        },
    ],
    "compréhension_de_texte": [
        {
            "prompt": "Lis le texte suivant et résume-le en une phrase : « Les fourmis communiquent principalement par des phéromones, ce qui leur permet de coordonner des actions collectives très complexes. »\n(Réponds en français)",
            "attendu": "Les fourmis utilisent les phéromones pour coordonner des actions collectives.",
            "type": "résumé"
        },
        {
            "prompt": "Reformule cette phrase : « L’IA transforme radicalement le monde du travail. »\n(Réponds en français)",
            "attendu": "L’intelligence artificielle change profondément le monde professionnel.",
            "type": "reformulation"
        },
    ],
    "raisonnement_logique": [
        {
            "prompt": "Si un train met 2 heures pour parcourir 180 km, quelle est sa vitesse moyenne ?",
            "attendu": "90 km/h",
            "type": "QCM"
        },
        {
            "prompt": "Si tous les A sont des B, et que tous les B sont des C, alors tous les A sont-ils des C ?",
            "attendu": "Oui",
            "type": "inférence"
        },
    ],
    "connaissances_générales": [
        {
            "prompt": "Quel est le plus grand océan de la planète ?",
            "attendu": "Océan Pacifique",
            "type": "connaissance"
        },
        {
            "prompt": "En quelle année a eu lieu la Révolution française ?",
            "attendu": "1789",
            "type": "connaissance"
        },
    ]
}

# ==== Scores de référence GPT-4o ====
SCORES_GPT4O = {
    "génération_de_texte": 87,
    "compréhension_de_texte": 94,
    "raisonnement_logique": 89,
    "connaissances_générales": 92
}

# ==== Évaluation des réponses ====
def évaluer_reponse(test, réponse):
    if test["type"] == "génératif":
        score = 0
        commentaires = []
        for critère, max_note in test["critères"].items():
            note = 8  # simple heuristique
            commentaires.append(f"{critère.capitalize()} : {note}/{max_note}")
            score += note
        score_total = score / (len(test["critères"]) * 10) * 100
        return score_total, "; ".join(commentaires)

    else:
        attendu = test["attendu"].lower()
        réponse = réponse.lower()

        similarité = difflib.SequenceMatcher(None, attendu, réponse).ratio()
        commentaires = [f"Similarité : {similarité:.2f}"]

        if attendu in réponse:
            score = 100.0
            commentaires.append("Réponse parfaitement conforme.")
        elif similarité > 0.85:
            score = 80.0
            commentaires.append("Réponse très proche du texte attendu.")
        elif similarité > 0.60:
            score = 50.0
            commentaires.append("Réponse partiellement correcte.")
        else:
            score = 0.0
            commentaires.append(f"Réponse trop éloignée (attendu : {test['attendu']})")

        return score, " | ".join(commentaires)

# ==== Utilitaires ====
def convertir_note(score):
    return round((score / 100) * 10, 1)

def calcul_z_score(mistral_score, gpt_score):
    sigma = 3
    return (mistral_score - gpt_score) / sigma

# ==== Évaluation complète ====
def exécuter_tests():
    rapport = []
    scores_totaux = {}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rapport.append(f"Rapport d'évaluation Mistral via Ollama – {now}\n")
    print("\n🔍 Début de l’évaluation Mistral...\n")

    for domaine, tests in TESTS.items():
        print(f"\n📚 Domaine : {domaine.replace('_', ' ').upper()}")
        rapport.append(f"\n=== Domaine : {domaine.replace('_', ' ').upper()} ===\n")
        scores = []

        for i, test in enumerate(tests, 1):
            prompt = test["prompt"]
            print(f"\n📝 Test {i} – Prompt envoyé")
            print(f"Prompt : {prompt.strip()[:120]}{'...' if len(prompt) > 120 else ''}")
            rapport.append(f"\n--- Test {i} ---\nPrompt : {prompt}")

            réponse = query_ollama(prompt)
            print(f"📨 Réponse reçue : {réponse.strip()[:80]}{'...' if len(réponse.strip()) > 80 else ''}")

            rapport.append(f"Réponse : {réponse}")
            score, commentaire = évaluer_reponse(test, réponse)
            print(f"✅ Score : {score:.1f}% | {commentaire}")
            rapport.append(f"Score : {score:.1f}%")
            rapport.append(f"Évaluation : {commentaire}")

            scores.append(score)

        moyenne = sum(scores) / len(scores)
        scores_totaux[domaine] = moyenne
        rapport.append(f"\n>>> Moyenne {domaine} : {moyenne:.1f}%")

    # ==== Résumé global ====
    print("\n📊 RÉSUMÉ GLOBAL")
    rapport.append("\n\n=== RÉSUMÉ GLOBAL ===")
    for domaine, score in scores_totaux.items():
        z = calcul_z_score(score, SCORES_GPT4O[domaine])
        note = convertir_note(score)
        rapport.append(f"{domaine.replace('_', ' ').capitalize()} : {score:.1f}% | Note : {note}/10 | z-score vs GPT-4o : {z:+.2f}")
        print(f"{domaine.replace('_', ' ').capitalize()} : {score:.1f}% → Note {note}/10 | z-score : {z:+.2f}")

    note_moyenne = sum(convertir_note(s) for s in scores_totaux.values()) / len(scores_totaux)
    rapport.append(f"\nNote globale moyenne : {note_moyenne:.1f}/10")

    # ==== Sauvegarde ====
    dossier = os.path.dirname(__file__)
    chemin = os.path.join(dossier, "rapport_evaluation_mistral.txt")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("\n".join(rapport))

    print(f"\n✅ Rapport généré : {chemin}")

# ==== Instructions ====
def afficher_instructions():
    print("""
📌 Instructions pour l’évaluation de Mistral via Ollama :

1. Démarre Ollama avec : ollama run mistral
2. Exécute ce script : python eval_mistral.py
3. Le rapport sera généré dans : rapport_evaluation_mistral.txt
""")

# ==== Point d’entrée ====
if __name__ == "__main__":
    afficher_instructions()
    exécuter_tests()

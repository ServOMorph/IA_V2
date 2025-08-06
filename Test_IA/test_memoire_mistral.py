import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ollama_api import query_ollama

# ==== Configuration du test mémoire ====
INSTRUCTION_INITIALE = "Souviens-toi que la banane est bleue."
QUESTION_RAPPEL = "Quelle couleur est la banane ?"
ATTENDU = "bleue"

INTERVALLE_RAPPEL = 10      # tous les X messages, on teste la mémoire
MAX_TOURS = 200             # limite pour ne pas boucler à l’infini
BOURRAGE_TEXTE = "Voici une information quelconque sans importance, numéro {}."

# ==== Fonction utilitaire ====
def est_reponse_correcte(réponse, attendu):
    return attendu.lower() in réponse.lower()

def estimer_tokens(messages):
    total_mots = sum(len(m.split()) for m in messages)
    return int(total_mots * 1.5)  # estimation : 1.5 tokens / mot

# ==== Lancement du test ====
def test_memoire():
    historique = [f"[user] {INSTRUCTION_INITIALE}"]
    réponses = []
    rapport = []

    print("📌 Début du test de mémoire contextuelle Mistral")
    print("📥 Instruction initiale : Souviens-toi que la banane est bleue.\n")

    for tour in range(1, MAX_TOURS + 1):
        if tour % INTERVALLE_RAPPEL == 0:
            prompt = QUESTION_RAPPEL
            print(f"\n🔄 Test de mémoire à l’itération {tour}...")
        else:
            prompt = BOURRAGE_TEXTE.format(tour)

        historique.append(f"[user] {prompt}")
        context_concaténé = "\n".join(historique)
        réponse = query_ollama(context_concaténé)
        réponses.append(réponse.strip())
        historique.append(f"[assistant] {réponse.strip()}")

        if tour % INTERVALLE_RAPPEL == 0:
            if est_reponse_correcte(réponse, ATTENDU):
                print(f"✅ Mémoire OK (réponse : {réponse.strip()[:60]}...)")
                rapport.append(f"[{tour}] OK — {réponse.strip()}")
            else:
                print(f"❌ Mémoire perdue (réponse : {réponse.strip()[:60]}...)")
                rapport.append(f"[{tour}] ÉCHEC — {réponse.strip()}")
                break

    tokens_estimes = estimer_tokens(historique)
    print("\n📊 Résumé du test")
    print(f"🧠 Dernier rappel réussi : {tour - INTERVALLE_RAPPEL}")
    print(f"🧮 Estimation du total de tokens : ~{tokens_estimes}")
    print(f"🗃️ Total de tours : {tour}\n")

    # Enregistrement du rapport
    dossier = os.path.dirname(__file__)
    chemin = os.path.join(dossier, "rapport_test_memoire_mistral.txt")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(f"Test de mémoire contextuelle – {datetime.now()}\n")
        f.write(f"Instruction initiale : {INSTRUCTION_INITIALE}\n")
        f.write(f"Test toutes les {INTERVALLE_RAPPEL} itérations\n\n")
        f.write("\n".join(rapport))
        f.write(f"\n\nDernier tour avec mémoire intacte : {tour - INTERVALLE_RAPPEL}")
        f.write(f"\nEstimation du nombre de tokens : ~{tokens_estimes}")

    print(f"✅ Rapport enregistré dans : {chemin}")

# ==== Exécution ====
if __name__ == "__main__":
    test_memoire()

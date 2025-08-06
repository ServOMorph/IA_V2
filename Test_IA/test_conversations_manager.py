import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from conversations_manager import (
    creer_nouvelle_conversation,
    enregistrer_echange,
    lire_conversation,
    lister_conversations,
    renommer_conversation,
    supprimer_conversation
)

# Étape 1 – Création
nom_fichier = creer_nouvelle_conversation()
print(f"🆕 Nouveau fichier créé : {nom_fichier}")

# Étape 2 – Enregistrement d’un échange
enregistrer_echange(nom_fichier, "Quelle est la capitale de la France ?", "La capitale est Paris.")
enregistrer_echange(nom_fichier, "Et celle de l’Espagne ?", "Madrid.")

# Étape 3 – Lecture
contenu = lire_conversation(nom_fichier)
print("📄 Contenu du fichier :")
print(contenu)

# Étape 4 – Liste
print("📂 Liste des conversations disponibles :")
print(lister_conversations())

# Étape 5 – Renommage
nom_renomme = "test_renomme.txt"
renommer_conversation(nom_fichier, nom_renomme)
print(f"🔁 Fichier renommé : {nom_fichier} → {nom_renomme}")

# Étape 6 – Suppression
supprimer_conversation(nom_renomme)
print(f"🗑 Fichier supprimé : {nom_renomme}")

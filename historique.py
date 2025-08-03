def enregistrer_echange(prompt, reponse, fichier='historique.txt'):
    with open(fichier, 'a', encoding='utf-8') as f:
        f.write(f"Utilisateur : {prompt.strip()}\n")
        f.write(f"IA         : {reponse.strip()}\n\n")

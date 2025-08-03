Détails des fichiers
lancement_Mistral_Ollama.bat

    But : lancer l'IA Mistral via Ollama en local.

questions_IA.txt

    But : répertorier des questions simples pour tester l'IA.

structure.md

    But : document de référence pour comprendre la structure du projet.

    Contenu :

        Description de chaque fichier.

        À mettre à jour à chaque nouvelle étape du développement.

main.py

    But : point d'entrée principal de l'application Kivy.

    Contenu :

        Initialise la taille et la position de la fenêtre via config.py.

        Lance l’interface ChatInterface depuis interface.py.

        Redirige les impressions dans debug.log.

        Supprime les logs Kivy dans la console.

interface.py

    But : définit l’interface utilisateur graphique avec Kivy.

    Contenu :

        Champ de saisie texte, bouton envoyer et bouton quitter.

        Appel à l'API via ollama_api.py.

        Ajout automatique à l’historique (historique.txt).

        Impression des échanges utilisateur/IA dans debug.log.

        Affichage des erreurs critiques dans la console.

ollama_api.py

    But : gérer les requêtes HTTP vers le serveur local d’Ollama.

    Contenu :

        Fonction query_ollama(prompt) : envoie un prompt et retourne la réponse.

        Impression de la réponse dans debug.log.

        Impression des erreurs API dans la console (stderr).

config.py

    But : centraliser la configuration de l’application.

    Contenu :

        URL et modèle de l’API Ollama.

        Dimensions et positionnement de la fenêtre.

historique.py

    But : enregistrer chaque échange (utilisateur / IA) dans un fichier texte.

    Contenu :

        Fonction enregistrer_echange(prompt, reponse) : écrit dans historique.txt.

debug.log

    But : journalisation des impressions de debug de l'application.

    Contenu :

        Entrées utilisateur, réponses IA, logs d'exécution utiles.

        Écrasé à chaque lancement de l’application.

instructions_chatgpt.txt

    But : consigner les règles de fonctionnement que ChatGPT doit suivre lors des échanges.

    Contenu :

        Ne pas utiliser Canvas.

        Afficher les fichiers modifiés entièrement dans le chat.

        Ne rien tronquer.

        Attendre validation utilisateur avant chaque étape.

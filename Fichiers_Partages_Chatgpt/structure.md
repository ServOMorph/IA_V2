Détails des fichiers

📁 racine du projet

lancement_Mistral_Ollama.bat

    But : lancer l'IA Mistral via Ollama en local.
    Emplacement : ./lancement_Mistral_Ollama.bat

main.py

    But : point d'entrée principal de l'application Kivy.
    Contenu :
        - Initialise la taille et la position de la fenêtre via config.py.
        - Lance l’interface ChatInterface depuis interface.py.
        - Redirige les impressions dans debug.log.
        - Supprime les logs Kivy dans la console.
    Emplacement : ./main.py

interface.py

    But : définit l’interface utilisateur graphique avec Kivy.
    Contenu :
        - Champ de saisie texte, bouton envoyer et bouton quitter.
        - Appel à l'API via ollama_api.py.
        - Ajout automatique à l’historique (historique.txt).
        - Impression des échanges utilisateur/IA dans debug.log.
        - Affichage des erreurs critiques dans la console.
    Emplacement : ./interface.py

ollama_api.py

    But : gérer les requêtes HTTP vers le serveur local d’Ollama.
    Contenu :
        - Fonction query_ollama(prompt) : envoie un prompt et retourne la réponse.
        - Impression de la réponse dans debug.log.
        - Impression des erreurs API dans la console (stderr).
    Emplacement : ./ollama_api.py

config.py

    But : centraliser la configuration de l’application.
    Contenu :
        - URL et modèle de l’API Ollama.
        - Dimensions et positionnement de la fenêtre.
    Emplacement : ./config.py

historique.py

    But : enregistrer chaque échange (utilisateur / IA) dans un fichier texte.
    Contenu :
        - Fonction enregistrer_echange(prompt, reponse) : écrit dans historique.txt.
    Emplacement : ./historique.py

debug.log

    But : journalisation des impressions de debug de l'application.
    Contenu :
        - Entrées utilisateur, réponses IA, logs d'exécution utiles.
        - Écrasé à chaque lancement de l’application.
    Emplacement : ./debug.log

instructions_chatgpt.txt

    But : consigner les règles de fonctionnement que ChatGPT doit suivre lors des échanges.
    Contenu :
        - Ne pas utiliser Canvas.
        - Afficher les fichiers modifiés entièrement dans le chat.
        - Ne rien tronquer.
        - Attendre validation utilisateur avant chaque étape.
    Emplacement : ./instructions_chatgpt.txt


📁 Test_IA

questions_IA.txt

    But : répertorier des questions classées par type (simples, complexes, robustesse, etc.)
           afin d’exécuter un protocole de test ou des benchmarks, manuellement ou automatiquement.
    Emplacement : ./Test_IA/questions_IA.txt

protocole_test_IA.txt

    But : définir un protocole structuré pour tester les performances et la robustesse de l’IA locale.
    Contenu :
        - Description des types de tests (temps de réponse, qualité, robustesse, etc.).
        - Méthodologie, structure des fichiers associés, conseils d’utilisation.
        - Format de rapport attendu (CSV, notes manuelles, logs…).
    Emplacement : ./Test_IA/protocole_test_IA.txt


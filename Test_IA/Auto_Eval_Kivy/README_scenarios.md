📜 Guide de création et modification d'un scénario Auto_Eval_Kivy

🎯 Objectif
Ce document explique comment écrire et modifier un scénario pour piloter automatiquement l’IA ServOMorph via l’interface Kivy.

Un scénario est un fichier JSON qui décrit pas à pas :
1. Ce que l’utilisateur doit envoyer.
2. Ce que le driver doit attendre comme réponse.
3. Les moments où il doit attendre ou arrêter l’application.

──────────────────────────────
📂 Emplacement par défaut
──────────────────────────────
Le scénario principal est ici :
IA_V2\Test_IA\Auto_Eval_Kivy\scenario_example.json

Mais tu peux créer d'autres scénarios dans un dossier "scenarios/" si tu veux les séparer.

──────────────────────────────
⚙️ Format général
──────────────────────────────
Le fichier est un tableau JSON, chaque élément est une étape :
[
  {
    "action": "send_user",
    "text": "Bonjour, peux-tu dire 'pong' ?",
    "delay_ms": 200
  },
  {
    "action": "expect_reply",
    "regex": "pong",
    "timeout_ms": 5000
  },
  {
    "action": "stop"
  }
]

──────────────────────────────
🔹 Actions disponibles
──────────────────────────────

1. "send_user"
Envoie un message comme si l’utilisateur le tapait dans l’UI.
{
  "action": "send_user",
  "text": "Quel temps fait-il aujourd'hui ?",
  "delay_ms": 200
}
- text : contenu du message.
- delay_ms : délai avant envoi (facultatif).

💡 Avec le driver séquentiel, la prochaine étape ne démarre qu’après la fin de la réponse IA.

──────────────────────────────

2. "wait"
Attente forcée avant l’étape suivante.
{
  "action": "wait",
  "ms": 3000
}
- ms : durée en millisecondes.

──────────────────────────────

3. "expect_reply"
Attend qu’une réponse de l’IA contienne un motif (regex).
{
  "action": "expect_reply",
  "regex": "pong|météo",
  "timeout_ms": 10000
}
- regex : motif à rechercher (insensible à la casse).
- timeout_ms : durée max avant de passer à l’étape suivante.

──────────────────────────────

4. "stop"
Arrête l’application.
{
  "action": "stop"
}

──────────────────────────────
🛠 Conseils pratiques
──────────────────────────────
- Toujours tester le scénario avec un backend IA actif (Ollama, API, etc.).
- Éviter les réponses tronquées : privilégier le mode séquentiel.
- Utiliser des regex simples et robustes.

──────────────────────────────
🚀 Exécution d’un scénario
──────────────────────────────
Depuis la racine du projet :
python -m Test_IA.Auto_Eval_Kivy.eval_kivy_driver

Le driver lit par défaut "scenario_example.json".
Pour un autre scénario, modifier DEFAULT_SCENARIO_PATH dans eval_config.py.

──────────────────────────────
📊 Analyse après exécution
──────────────────────────────
Les résultats sont dans :
IA_V2\Test_IA\Auto_Eval_Kivy\outputs\YYYYMMDD_HHMMSS\
- transcript.txt : conversation lisible.
- transcript.jsonl : conversation + métadonnées.
- session.log : logs techniques et erreurs.

Pour analyser rapidement :
python -m Test_IA.Auto_Eval_Kivy.analyze_last_run

@echo off
REM ================================================
REM Lancement de la console interactive ServOMorph IA
REM ================================================
title Console interactive ServOMorph IA
echo.
echo [INFO] Lancement de la console interactive...
echo.

REM Activation éventuelle de l'environnement virtuel (décommente si utilisé)
REM call venv\Scripts\activate

REM Lancer Ollama si nécessaire (décommente si tu veux lancer automatiquement)
REM start "" lancement_Mistral_Ollama.bat
REM timeout /t 3 >nul

REM Exécution du script console
python Test_IA\Console_Interactif\console_chat.py

echo.
pause

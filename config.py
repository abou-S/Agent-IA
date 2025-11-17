import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")

"""# Catégories et feuilles correspondantes dans Google Sheets
CATEGORY_TO_SHEET = {
    "probleme_technique": "Problème technique",
    "demande_administrative": "Demande administrative",
    "probleme_acces_auth": "Problème d’accès / authentification",
    "support_utilisateur": "Support utilisateur",
    "bug_service": "Bug / dysfonctionnement"
}"""

CATEGORY_TO_SHEET = {
    "probleme_technique": "Problème technique informatique",
    "demande_administrative": "Demande administrative",
    "probleme_acces_auth": "Problème d’accès / authentification",
    "support_utilisateur": "Demande de support utilisateur",
    # Il n'y a pas de feuille dédiée pour les bugs, 
    # donc on les range aussi dans "Problème technique informatique"
    "bug_service": "Problème technique informatique",
}



URGENCY_LEVELS = ["Anodine", "Faible", "Modérée", "Élevée", "Critique"]



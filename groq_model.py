import time
from groq import Groq, RateLimitError
from config import GROQ_API_KEY, URGENCY_LEVELS, CATEGORY_TO_SHEET

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
Tu es un agent de tri de tickets support.

À partir du sujet et du contenu d'un email, tu dois :

1) Classer le ticket dans UNE SEULE catégorie parmi :
   - probleme_technique : problème matériel ou logiciel, panne, lenteur, erreur système
   - demande_administrative : paperasse, contrat, facture, RH, demandes d'information
   - probleme_acces_auth : mot de passe oublié, compte bloqué, échec de connexion
   - support_utilisateur : accompagnement, aide à l'utilisation, question sur une fonctionnalité
   - bug_service : dysfonctionnement d'une fonctionnalité, bug reproductible sur un service déjà en place

2) Attribuer un niveau d'urgence parmi :
   - Anodine
   - Faible
   - Modérée
   - Élevée
   - Critique

Règles d'urgence :
- Critique : impact majeur, service bloqué pour plusieurs utilisateurs, production à l'arrêt, sécurité ou données critiques en jeu.
- Élevée : forte gêne, un utilisateur ou équipe bloquée sur une tâche importante, délai serré.
- Modérée : gêne notable mais contournable, impact limité dans le temps.
- Faible : problème mineur, simple inconfort.
- Anodine : demande d'information simple, pas de blocage, pas d'impact.

3) Produire une synthèse courte (1 à 3 phrases max) en français.

Tu dois répondre STRICTEMENT au format JSON :

{
  "categorie": "...",
  "urgence": "...",
  "synthese": "..."
}
"""

def analyze_ticket(subject: str, body: str) -> dict:
    """
    Envoie le contenu au modèle Groq et renvoie un dict :
    {
      "categorie": str,
      "urgence": str,
      "synthese": str
    }
    """
    user_content = f"Sujet: {subject}\n\nContenu:\n{body}"

    """response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # ou autre modèle dispo chez Groq
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        temperature=0.1,
        max_tokens=128
        #max_tokens=256

    )"""

    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                temperature=0,
                max_tokens=128
            )
            break

        except RateLimitError as e:
            print("➡️ Rate limit, retry dans 10 secondes...")
            time.sleep(10)

    content = response.choices[0].message.content

    import json
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # fallback si le modèle renvoie du texte avec du JSON dedans
        import re
        match = re.search(r'\{.*\}', content, re.S)
        if not match:
            raise ValueError(f"Réponse modèle invalide : {content}")
        data = json.loads(match.group(0))

    categorie = data.get("categorie")
    urgence = data.get("urgence")
    synthese = data.get("synthese", "").strip()

    # Petites sécurités
    if categorie not in CATEGORY_TO_SHEET:
        categorie = "support_utilisateur"  # fallback
    if urgence not in URGENCY_LEVELS:
        urgence = "Modérée"

    return {
        "categorie": categorie,
        "urgence": urgence,
        "synthese": synthese
    }

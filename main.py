import json
import os
import time

from gmail_client import get_all_emails
from groq_model import analyze_ticket
from sheets_client import append_ticket_row
from groq import RateLimitError

PROCESSED_FILE = "processed_emails.json"


def load_processed_ids() -> set:
    """Charge les IDs déjà traités depuis processed_emails.json."""
    if not os.path.exists(PROCESSED_FILE):
        return set()

    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # data peut être une liste ou un dict, on gère les deux cas
        if isinstance(data, list):
            return set(data)
        elif isinstance(data, dict) and "ids" in data:
            return set(data["ids"])
        else:
            return set()
    except Exception:
        # Si fichier corrompu, on repart de zéro
        return set()


def save_processed_ids(processed_ids: set):
    """Sauvegarde les IDs traités dans processed_emails.json."""
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(processed_ids)), f, ensure_ascii=False, indent=2)


def process_all_tickets(limit=None):
    # 1. Charger les IDs déjà traités
    processed_ids = load_processed_ids()
    print(f"📂 Nombre d'emails déjà traités : {len(processed_ids)}")

    # 2. Lire les emails de l'INBOX
    emails = get_all_emails(label_ids=["INBOX"], limit=limit)
    print(f"📨 Nombre d'emails récupérés depuis Gmail (INBOX) : {len(emails)}")

    # 3. Filtrer pour ne garder que ceux non encore traités
    emails_to_process = [e for e in emails if e["id"] not in processed_ids]
    print(f"🧾 Nombre d'emails à traiter cette fois-ci : {len(emails_to_process)}")

    processed_this_run = 0
    skipped = 0

    for i, email_obj in enumerate(emails_to_process, start=1):
        msg_id = email_obj["id"]
        subject = email_obj["subject"]
        body = email_obj["body"]

        try:
            # 1. Analyse via Groq
            analysis = analyze_ticket(subject, body)
            categorie = analysis["categorie"]
            urgence = analysis["urgence"]
            synthese = analysis["synthese"]

            print(f"Catégorie prédite pour '{subject}': {categorie}")

            # 2. Écriture dans Google Sheets
            append_ticket_row(
                category_key=categorie,
                sujet=subject,
                urgence=urgence,
                synthese=synthese
            )

            # 3. Marquer cet email comme traité
            processed_ids.add(msg_id)
            processed_this_run += 1

            print(
                f"[OK] {processed_this_run}/{len(emails_to_process)} — "
                f"'{subject}' -> {categorie} ({urgence})"
            )

        except RateLimitError:
            print("⏳ Rate limit Groq, pause 20 secondes puis reprise…")
            time.sleep(20)
            skipped += 1
            continue

        except Exception as e:
            print(f"❌ Erreur sur l'email #{i} ('{subject}') : {e}")
            skipped += 1
            continue

    # 4. Sauvegarder la liste à jour des IDs traités
    save_processed_ids(processed_ids)

    print(
        f"\n✅ Traitement terminé : {processed_this_run} emails traités cette exécution, "
        f"{skipped} ignorés, total désormais {len(processed_ids)} emails marqués comme traités."
    )


if __name__ == "__main__":
    # Pour traiter tous les mails non encore traités de l'INBOX :
    process_all_tickets()
    # Pour tester sur un petit batch de nouveaux mails :
    # process_all_tickets(limit=10)

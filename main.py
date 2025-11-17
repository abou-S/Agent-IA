

from gmail_client import get_all_emails
from groq_model import analyze_ticket
from sheets_client import append_ticket_row


from gmail_client import get_all_emails
from groq_model import analyze_ticket
from sheets_client import append_ticket_row


def process_all_tickets(limit=None):
    emails = get_all_emails(limit=limit)
    print(f"📨 Nombre d'emails récupérés depuis Gmail : {len(emails)}")

    processed = 0
    skipped = 0

    for i, email_obj in enumerate(emails, start=1):
        subject = email_obj["subject"]
        body = email_obj["body"]

        try:
            # 1. Analyse via Groq
            analysis = analyze_ticket(subject, body)
            categorie = analysis["categorie"]
            urgence = analysis["urgence"]
            synthese = analysis["synthese"]

            # 2. Écriture dans Google Sheets
            append_ticket_row(
                category_key=categorie,
                sujet=subject,
                urgence=urgence,
                synthese=synthese
            )

            processed += 1
            print(f"[OK] {processed}/{len(emails)} — '{subject}' -> {categorie} ({urgence})")

        except RateLimitError as e:
            print("⏳ Rate limit Groq, pause 20 secondes puis reprise…")
            time.sleep(20)
            skipped += 1
            continue

        except Exception as e:
            print(f"❌ Erreur sur l'email #{i} ('{subject}') : {e}")
            skipped += 1
            continue

    print(f"\n✅ Traitement terminé : {processed} emails traités, {skipped} ignorés.")


if __name__ == "__main__":
    # ⚠️ ICI : si tu veux VRAIMENT traiter tous les mails, enlève le limit
    # process_all_tickets(limit=5)   # seulement 5 pour tester
    process_all_tickets()            # tous les mails récupérés


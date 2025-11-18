from gmail_client import get_all_emails

def main():
    # On lit 5 mails, sans filtrer par label (tous labels)
    emails = get_all_emails(label_ids=["INBOX"],limit=None)

    print(f"Nombre d'emails récupérés : {len(emails)}\n")

    for i, email_obj in enumerate(emails, start=1):
        print("=" * 60)
        print(f"Email #{i}")
        print(f"Sujet : {email_obj['subject']}")
        print("--- Début du corps ---")
        print(email_obj["body"][:800])  # on affiche un peu plus large
        print("--- Fin du corps (tronqué) ---\n")

if __name__ == "__main__":
    main()

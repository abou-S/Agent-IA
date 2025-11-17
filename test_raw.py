from gmail_client import get_gmail_service

service = get_gmail_service()

def show_raw(limit=3):
    result = service.users().messages().list(
        userId="me",
        maxResults=limit
    ).execute()

    ids = result.get("messages", [])
    for i, msg in enumerate(ids, start=1):
        m = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="raw"
        ).execute()

        print("=" * 60)
        print(f"EMAIL #{i} - RAW BASE64")
        print(m["raw"][:500])
        print()

if __name__ == "__main__":
    show_raw()

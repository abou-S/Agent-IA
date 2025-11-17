import os
from typing import List, Dict, Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    """
    Initialise le service Gmail via OAuth2.
    Utilise credentials.json (client OAuth) et token.json (token utilisateur).
    """
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service


def _get_header(msg: Dict, name: str) -> str:
    """
    Récupère une valeur d'en-tête (Subject, From, To, etc.) en mode case-insensitive.
    """
    headers = msg.get("payload", {}).get("headers", [])
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def _get_message_subject(msg: Dict) -> str:
    return _get_header(msg, "Subject")


def _decode_body_data(data: str) -> str:
    """
    Décodage base64url → texte.
    """
    from base64 import urlsafe_b64decode

    if not data:
        return ""
    decoded_bytes = urlsafe_b64decode(data.encode("utf-8"))
    try:
        return decoded_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return decoded_bytes.decode("latin-1", errors="ignore")


def _extract_text_from_payload(payload: Dict) -> Dict[str, Optional[str]]:
    """
    Parcourt récursivement le payload pour récupérer :
    - text/plain
    - text/html

    Retourne un dict:
    {
      "plain": str | None,
      "html": str | None
    }
    """
    text_plain = []
    text_html = []

    def walk(part):
        mime_type = part.get("mimeType", "")
        body = part.get("body", {})
        data = body.get("data")

        # Si cette part a des sous-parts, on descend
        if "parts" in part:
            for sub in part["parts"]:
                walk(sub)
            return

        if not data:
            return

        text = _decode_body_data(data)
        if mime_type.startswith("text/plain"):
            text_plain.append(text)
        elif mime_type.startswith("text/html"):
            text_html.append(text)

    # Si le corps direct contient déjà des données
    if payload.get("body", {}).get("data"):
        mime_type = payload.get("mimeType", "")
        text = _decode_body_data(payload["body"]["data"])
        if mime_type.startswith("text/plain"):
            text_plain.append(text)
        elif mime_type.startswith("text/html"):
            text_html.append(text)

    # Sinon, on parcourt les parts
    for part in payload.get("parts", []):
        walk(part)

    plain = "\n".join(text_plain).strip() if text_plain else None
    html = "\n".join(text_html).strip() if text_html else None

    return {"plain": plain, "html": html}


def _get_message_body(msg: Dict) -> str:
    """
    Récupère le corps en texte brut.
    - priorité : text/plain
    - fallback : text/html nettoyé
    """
    payload = msg.get("payload", {}) or {}

    texts = _extract_text_from_payload(payload)
    plain = texts["plain"]
    html = texts["html"]

    if plain:
        return plain

    if html:
        # On nettoie le HTML si possible
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text(separator="\n")
        except Exception:
            return html

    return ""


def get_all_emails(
    label_ids: Optional[List[str]] = None,
    limit: Optional[int] = None,
    query: Optional[str] = None
) -> List[Dict]:
    """
    Récupère les emails via l'API Gmail.

    Retourne une liste de dict :
    [
      {
        "id": str,
        "subject": str,
        "body": str
      }
    ]

    - label_ids : liste de labels Gmail (ex: ["INBOX"]), None = tous labels
    - limit : nombre max de mails
    - query : filtre de recherche Gmail (ex: "from:ticketsdata5@gmail.com")
    """
    service = get_gmail_service()

    all_messages_meta = []
    page_token = None

    while True:
        kwargs = {
            "userId": "me",
            "maxResults": 100,
        }
        if label_ids:
            kwargs["labelIds"] = label_ids
        if query:
            kwargs["q"] = query
        if page_token:
            kwargs["pageToken"] = page_token

        response = service.users().messages().list(**kwargs).execute()
        messages = response.get("messages", [])
        all_messages_meta.extend(messages)

        page_token = response.get("nextPageToken")
        if not page_token:
            break

        if limit and len(all_messages_meta) >= limit:
            break

    if limit:
        all_messages_meta = all_messages_meta[:limit]

    emails = []

    for msg_meta in all_messages_meta:
        msg_id = msg_meta["id"]
        msg = service.users().messages().get(
            userId="me",
            id=msg_id,
            format="full"
        ).execute()

        subject = _get_message_subject(msg)
        body = _get_message_body(msg)

        emails.append({
            "id": msg_id,
            "subject": subject,
            "body": body
        })

    return emails

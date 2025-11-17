from groq_model import analyze_ticket

subject = "Erreur de connexion"
body = """
Bonjour, je n'arrive plus à accéder à mon compte.
L'authentification échoue depuis ce matin.
Pouvez-vous m'aider ?
"""

result = analyze_ticket(subject, body)
print(result)
from groq_model import analyze_ticket

subject = "Erreur de connexion"
body = """
Bonjour, je n'arrive plus à accéder à mon compte.
L'authentification échoue depuis ce matin.
Pouvez-vous m'aider ?
"""

result = analyze_ticket(subject, body)
print(result)

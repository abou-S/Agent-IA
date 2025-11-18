from sheets_client import append_ticket_row

# Test support_utilisateur
append_ticket_row(
    category_key="support_utilisateur",
    sujet="[TEST] Aide pour utiliser le tableau de bord",
    urgence="Modérée",
    synthese="L'utilisateur demande une explication sur l'utilisation du tableau de bord."
)

# Test bug_service
append_ticket_row(
    category_key="bug_service",
    sujet="[TEST] Bug sur le formulaire de paiement",
    urgence="Élevée",
    synthese="Erreur 500 à chaque validation du formulaire de paiement."
)

print("✅ Lignes de test envoyées.")

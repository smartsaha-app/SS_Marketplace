from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Payments(models.Model):
    STATUS_CHOICES = [
        ("awaiting_payment", "Awaiting Payment"),   # Créé mais pas encore payé
        ("funds_secured", "Funds Secured"),         # Argent bloqué dans l'escrow
        ("completed", "Completed"),                 # Paiement libéré au vendeur
        ("cancelled", "Cancelled"),                 # Annulé / remboursé
        ("failed", "Failed"),                       # Paiement échoué
    ]

    # Liens vers les utilisateurs
    buyer = models.ForeignKey(User, related_name="payments_as_buyer", on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name="payments_as_seller", on_delete=models.CASCADE)

    # Liens vers la proposition (bid) qui contient déjà post_id
    bid = models.ForeignKey('marketplace.Bid', on_delete=models.CASCADE, related_name='payments')

    # Montants et frais
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.ForeignKey('marketplace.Currency', on_delete=models.CASCADE, related_name='payments')
    platform_fee = models.DecimalField(max_digits=20, decimal_places=2, default=0)  # commission

    # Stripe
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.CharField(max_length=50, default="card")  # pour l’instant uniquement carte

    # Statuts
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="awaiting_payment")
    buyer_confirmation = models.BooleanField(default=False)  # confirme la livraison
    seller_confirmation = models.BooleanField(default=False)  # optionnel
    refunded_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    failure_reason = models.TextField(blank=True, null=True)
    dispute_id = models.CharField(max_length=255, blank=True, null=True)

    # Infos supplémentaires
    metadata = models.JSONField(blank=True, null=True)

    # Dates
    transaction_date = models.DateTimeField(auto_now_add=True)  # date initiale
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} - {self.amount} {self.currency.iso_code} - {self.status}"

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-transaction_date']

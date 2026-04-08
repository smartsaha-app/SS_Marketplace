# from django.db import models
# from django.core.exceptions import ValidationError
# from django.utils import timezone

# from marketplace.models import Post, Bid


# class Payment(models.Model):

#     class PaymentMethod(models.TextChoices):
#         MVOLA = 'MVOLA', 'MVola'
#         ORANGE_MONEY = 'ORANGE_MONEY', 'Orange Money'
#         AIRTEL_MONEY = 'AIRTEL_MONEY', 'Airtel Money'

#     class PaymentStatus(models.TextChoices):
#         PENDING = 'PENDING', 'En attente'
#         SUCCESS = 'SUCCESS', 'Succès'
#         FAILED = 'FAILED', 'Échoué'
#         CANCELLED = 'CANCELLED', 'Annulé'

#     # =========================
#     # Relations
#     # =========================
#     post = models.ForeignKey(
#         Post,
#         on_delete=models.CASCADE,
#         related_name='payments'
#     )

#     bid = models.OneToOneField(
#         Bid,
#         on_delete=models.CASCADE,
#         related_name='payment'
#     )

#     # =========================
#     # Paiement
#     # =========================
#     payment_method = models.CharField(
#         max_length=20,
#         choices=PaymentMethod.choices
#     )

#     payment_number = models.CharField(
#         max_length=30,
#         help_text="Numéro utilisé pour le paiement"
#     )

#     transaction_reference = models.CharField(
#         max_length=100,
#         unique=True
#     )

#     status = models.CharField(
#         max_length=15,
#         choices=PaymentStatus.choices,
#         default=PaymentStatus.PENDING
#     )

#     payment_date = models.DateTimeField(
#         null=True,
#         blank=True
#     )

#     # =========================
#     # Timestamps
#     # =========================
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     # =========================
#     # Propriétés dérivées
#     # =========================
#     @property
#     def amount(self):
#         return self.bid.price

#     @property
#     def currency(self):
#         return self.post.currency

#     # =========================
#     # Validation
#     # =========================
#     def clean(self):
#         if self.bid.post != self.post:
#             raise ValidationError(
#                 "L'enchère ne correspond pas au post."
#             )

#     def mark_as_success(self):
#         self.status = self.PaymentStatus.SUCCESS
#         self.payment_date = timezone.now()
#         self.save(update_fields=['status', 'payment_date'])

#     def __str__(self):
#         return (
#             f"Paiement {self.amount} {self.currency.iso_code} "
#             f"- {self.get_status_display()}"
#         )

#     class Meta:
#         verbose_name = "Paiement"
#         verbose_name_plural = "Paiements"
#         ordering = ['-created_at']

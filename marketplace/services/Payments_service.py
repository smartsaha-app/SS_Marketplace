import stripe
from django.conf import settings
from marketplace.models import Payments
from marketplace.models.Bid_models import Bid_status

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:

    @staticmethod
    def create_payment(buyer, seller, bid, amount, currency, platform_fee=0, metadata=None):
        """Crée le Payment et génère un PaymentIntent Stripe"""
        payment = Payments.objects.create(
            buyer=buyer,
            seller=seller,
            bid=bid,
            amount=amount,
            currency=currency,
            platform_fee=platform_fee,
            metadata=metadata or {}
        )

        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # centimes
            currency=currency.iso_code.lower(),
            capture_method='manual',  # blocage escrow
            metadata={
                'payment_id': payment.id,
                'buyer_id': buyer.id,
                'seller_id': seller.id,
                'bid_id': bid.id
            }
        )

        payment.stripe_payment_intent_id = intent.id
        payment.save()

        return payment, intent.client_secret

    @staticmethod
    def secure_payment(payment: Payments):
        """
        Marque le paiement comme sécurisé après que le buyer ait entré
        sa carte et que Stripe ait autorisé le paiement.
        """
        if payment.status != "awaiting_payment":
            raise ValueError("Paiement déjà sécurisé ou capturé")

        # Ici tu pourrais vérifier le PaymentIntent Stripe si nécessaire
        # stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)

        payment.status = "funds_secured"
        payment.save()
        return payment

    @staticmethod
    def capture_payment(payment: Payments):
        """Libère l’argent vers le vendeur"""
        if payment.status != 'funds_secured':
            raise ValueError("Paiement non sécurisé ou déjà capturé")
        stripe.PaymentIntent.capture(payment.stripe_payment_intent_id)
        # stripe.PaymentIntent.capture(
        #     payment.stripe_payment_intent_id,
        #     stripe_account=payment.seller.stripe_account_id 
        # )
        payment.status = 'completed'
        paid_status, _ = Bid_status.objects.get_or_create(name="payée")
        payment.bid.changer_statut(paid_status)
        payment.save()
        return payment

    @staticmethod
    def confirm_by_buyer(payment: Payments):
        payment.buyer_confirmation = True
        if payment.seller_confirmation:
            # Si vendeur déjà confirmé → capture
            payment = PaymentService.capture_payment(payment)
        payment.save()
        return payment

    @staticmethod
    def confirm_by_seller(payment: Payments):
        payment.seller_confirmation = True
        if payment.buyer_confirmation:
            payment = PaymentService.capture_payment(payment)
        payment.save()
        return payment

from random import choice

class VanillaPayService:
    """
    Service pour vérifier un paiement Vanilla Pay.
    Ici en mode mock : renvoie SUCCESS ou FAILED aléatoirement.
    """
    @staticmethod
    def verify_payment(*, method, phone, amount, reference):
        # Simule succès ou échec
        status = choice(["SUCCESS", "FAILED"])
        return {
            "status": status,
            "reference": reference,
            "amount": amount,
            "method": method
        }

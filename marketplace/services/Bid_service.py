from django.utils import timezone
from marketplace.models import Bid, Bid_status, BidStatusRelation, Message
from marketplace.models.Post_models import Post_status, PostStatusRelation
from marketplace.serializers.Bid_serialisers import BidSerializer


def update_bid(bid: Bid, data: dict) -> Bid:
    """
    Met à jour une enchère si elle est encore au statut 'proposée'
    """
    if bid.get_status_bid().name.lower() != "proposée":
        raise ValueError("Seules les enchères au statut 'proposée' peuvent être modifiées.")

    # Mise à jour des champs autorisés
    price = data.get("price")
    message = data.get("message")

    if price is not None:
        if float(price) <= 0:
            raise ValueError("Le prix doit être supérieur à zéro.")
        bid.price = price

    if message is not None:
        bid.message = message

    bid.updated_at = timezone.now()
    bid.save()

    return bid


def cancel_bid(bid: Bid, user=None, comment="Annulation par l'utilisateur") -> Bid:
    """
    Annule une enchère : ajoute un statut 'annulée' dans l'historique
    """
    current_status = bid.get_status_bid()
    if current_status.name.lower() in ["acceptée", "annulée"]:
        raise ValueError(f"L'enchère ne peut pas être annulée car elle est déjà au statut '{current_status.name}'.")

    try:
        cancelled_status = Bid_status.objects.get(name__iexact="annulée")
    except Bid_status.DoesNotExist:
        raise ValueError("Le statut 'annulée' n'existe pas dans la base.")

    BidStatusRelation.objects.create(
        bid=bid,
        status=cancelled_status,
        changed_by=user,
        comment=comment
    )

    return bid


def accept_bid(bid: Bid, user=None, comment="Enchère acceptée") -> Bid:
    """
    Accepte une enchère : modifie son statut à 'acceptée'
    """
    current_status = bid.get_status_bid()
    if current_status.name.lower() != "proposée":
        raise ValueError("Seules les enchères proposées peuvent être acceptées.")

    try:
        accepted_status = Bid_status.objects.get(name__iexact="acceptée")
    except Bid_status.DoesNotExist:
        raise ValueError("Le statut 'acceptée' n'existe pas.")

    BidStatusRelation.objects.create(
        bid=bid,
        status=accepted_status,
        changed_by=user,
        comment=comment
    )

    return bid


def reject_bid(bid, owner, continue_negotiation: bool, message: str = ""):
    """
    Refuse une enchère :
    - Si continue_negotiation = True → statut 'refusée' (la négociation peut continuer)
    - Si continue_negotiation = False → statut 'arrêtée' (fin définitive de la négociation)
    - Ajoute un message facultatif à l'utilisateur si fourni
    """
    # Vérifie que l'utilisateur est propriétaire du post
    if bid.post.user != owner:
        raise ValueError("Vous n'êtes pas autorisé à rejeter cette enchère.")

    # Statuts possibles
    refused_status = Bid_status.objects.get(name="refusée")
    stopped_status = Bid_status.objects.get(name="arrêtée")  # à créer si pas déjà en DB

    # Détermine le statut à appliquer
    status_to_apply = refused_status if continue_negotiation else stopped_status

    # Crée la relation de statut
    BidStatusRelation.objects.create(
        bid=bid,
        status=status_to_apply,
        changed_by=owner,
        comment="Refus manuel via API"
    )

    # Ajoute un message si fourni
    if message:
        Message.objects.create(
            post=bid.post,
            sender=owner,
            receiver=bid.user,
            bid=bid,
            content=message,
            timestamp=timezone.now()
        )

def accept_bid(bid, owner):
    # Vérifie que le statut actuel est "proposée"
    current_status = bid.get_status_bid()
    if current_status.name.lower() != "proposée":
        raise ValueError(f"Impossible d'accepter une enchère avec le statut '{current_status.name}'.")

    # Change le statut de l'enchère acceptée
    accepted_status = Bid_status.objects.get(name="acceptée")
    BidStatusRelation.objects.create(bid=bid, status=accepted_status, changed_by=owner)

    # Met éventuellement le post en 'vendu'
    post = bid.post
    sold_status = Post_status.objects.get(name="vendu")
    PostStatusRelation.objects.create(post=post, status=sold_status, changed_by=owner)

    # 🚨 Refuser toutes les autres enchères du même post
    refused_status = Bid_status.objects.get(name="refusée")
    other_bids = post.bids.exclude(id=bid.id)  # toutes sauf celle acceptée
    for other_bid in other_bids:
        # Vérifie que l'enchère n'est pas déjà refusée ou acceptée
        if other_bid.get_status_bid().name.lower() == "proposée":
            BidStatusRelation.objects.create(
                bid=other_bid,
                status=refused_status,
                changed_by=owner
            )

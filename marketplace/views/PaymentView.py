# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.utils import timezone

# from marketplace.models.Bid_models import Bid_status
# from marketplace.models.Payments_models import Payment
# from marketplace.serializers.Payments_serializers import PaymentCreateSerializer, PaymentSerializer
# from marketplace.services.vanilla_pay import VanillaPayService
# from rest_framework.generics import ListAPIView
# from rest_framework.permissions import IsAuthenticated
# from django.db.models import Q


# class PaymentCreateVerifyView(APIView):
#     """
#     Crée un paiement et vérifie via Vanilla Pay (mock pour l'instant)
#     """

#     def post(self, request):
#         serializer = PaymentCreateSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         # Crée le paiement en PENDING automatiquement
#         payment = serializer.save()

#         # Vérification Vanilla Pay
#         result = VanillaPayService.verify_payment(
#             method=payment.payment_method,
#             phone=payment.payment_number,
#             amount=payment.amount,
#             reference=payment.transaction_reference
#         )

#         if result.get("status") == "SUCCESS":
#             payment.mark_as_success()
#             paid_status, _ = Bid_status.objects.get_or_create(name="payée")
#             payment.bid.changer_statut(paid_status)

#             return Response({
#                 "message": "Paiement confirmé",
#                 "payment": PaymentSerializer(payment).data
#             }, status=status.HTTP_200_OK)

#         # Sinon échoué
#         payment.status = Payment.PaymentStatus.FAILED
#         payment.save(update_fields=['status'])

#         return Response({
#             "message": "Paiement non valide",
#             "payment": PaymentSerializer(payment).data
#         }, status=status.HTTP_400_BAD_REQUEST)


# class MyPaymentsView(ListAPIView):
#     """
#     Récupère TOUS les paiements liés à l'utilisateur connecté :
#     - Paiements reçus (post.owner)
#     - Paiements effectués (bid.user)
#     """
#     serializer_class = PaymentSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user

#         return (
#             Payment.objects
#             .filter(
#                 Q(post__user=user) | Q(bid__user=user)
#             )
#             .select_related(
#                 "post",
#                 "bid",
#                 "bid__user",
#                 "post__currency"
#             )
#             .order_by("-created_at")
#         )


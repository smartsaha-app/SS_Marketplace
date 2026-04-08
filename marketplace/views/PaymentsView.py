from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from django.db.models import Q
from marketplace.models import Payments, Bid, Currency
from marketplace.serializers import PaymentSerializer, PaymentListSerializer
from marketplace.services import PaymentService

class CreatePaymentView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def post(self, request, *args, **kwargs):
        buyer = request.user
        bid_id = request.data.get('bid_id')

        try:
            bid = Bid.objects.select_related(
                "post",
                "post__user",
                "post__type_post",
                "user"
            ).get(id=bid_id)
        except Bid.DoesNotExist:
            return Response(
                {"message": "Bid introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        post = bid.post
        post_type = post.type_post.type.lower().strip()

        # 🔥 Déterminer seller
        if post_type == "selling":
            seller = post.user

        elif post_type == "buying":
            seller = bid.user

        else:
            return Response(
                {"message": "Type de post invalide."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔐 Sécurité
        if buyer == seller:
            return Response(
                {"message": "Vous ne pouvez pas vous payer vous-même."},
                status=status.HTTP_400_BAD_REQUEST
            )

        amount = bid.price
        currency = bid.currency

        payment, client_secret = PaymentService.create_payment(
            buyer=buyer,
            seller=seller,
            bid=bid,
            amount=amount,
            currency=currency
        )

        return Response({
            "payment_id": payment.id,
            "client_secret": client_secret
        }, status=status.HTTP_201_CREATED)



class PaymentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentListSerializer

    def get_queryset(self):
        user = self.request.user
        return Payments.objects.filter(
            Q(buyer=user) | Q(seller=user)
        )



class ConfirmPaymentBuyerView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()

    def post(self, request, *args, **kwargs):
        payment = self.get_object()
        if payment.buyer != request.user:
            return Response({'detail': 'Non autorisé'}, status=status.HTTP_403_FORBIDDEN)
        payment = PaymentService.confirm_by_buyer(payment)
        serializer = self.get_serializer(payment)
        return Response(serializer.data)


class ConfirmPaymentSellerView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()

    def post(self, request, *args, **kwargs):
        payment = self.get_object()
        if payment.seller != request.user:
            return Response({'detail': 'Non autorisé'}, status=status.HTTP_403_FORBIDDEN)
        payment = PaymentService.confirm_by_seller(payment)
        serializer = self.get_serializer(payment)
        return Response(serializer.data)

class SecurePaymentView(APIView):
    def post(self, request, pk):
        try:
            payment = Payments.objects.get(pk=pk)
            # Ici tu peux appeler ton service pour mettre le status à funds_secured
            payment.status = 'funds_secured'
            payment.save()
            return Response({"status": payment.status}, status=status.HTTP_200_OK)
        except Payments.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
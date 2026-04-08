# from rest_framework import serializers

# from marketplace.models.Payments_models import Payment
# from marketplace.serializers.Bid_serialisers import BidSerializer
# from marketplace.serializers.Post_serializers import PostSerializer


# class PaymentSerializer(serializers.ModelSerializer):
#     amount = serializers.ReadOnlyField()
#     currency = serializers.ReadOnlyField(source='currency.iso_code')

#     post = PostSerializer(read_only=True)
#     bid = BidSerializer(read_only=True)

#     class Meta:
#         model = Payment
#         fields = [
#             'id',
#             'post',
#             'bid',
#             'payment_method',
#             'payment_number',
#             'transaction_reference',
#             'status',
#             'payment_date',
#             'amount',
#             'currency',
#             'created_at',
#             'updated_at',
#         ]


# class PaymentCreateSerializer(serializers.ModelSerializer):
#     status = serializers.ChoiceField(
#         choices=Payment.PaymentStatus.choices, default=Payment.PaymentStatus.PENDING
#     )

#     class Meta:
#         model = Payment
#         fields = [
#             'post',
#             'bid',
#             'payment_method',
#             'payment_number',
#             'transaction_reference',
#             'status', 
#         ]


#     def validate(self, data):
#         bid = data['bid']
#         post = data['post']

#         if bid.post != post:
#             raise serializers.ValidationError(
#                 "Cette enchère n'appartient pas à ce post."
#             )

#         if hasattr(bid, 'payment'):
#             raise serializers.ValidationError(
#                 "Cette enchère a déjà un paiement."
#             )

#         return data

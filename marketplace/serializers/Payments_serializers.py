from rest_framework import serializers
from marketplace.models import Payments
from marketplace.serializers.Bid_serialisers import BidSerializer

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = '__all__'
        read_only_fields = ('status', 'stripe_payment_intent_id', 'transaction_date', 'created_at', 'updated_at')

class PaymentListSerializer(serializers.ModelSerializer):
    buyer = serializers.StringRelatedField()
    seller = serializers.StringRelatedField()
    # bid = serializers.StringRelatedField()
    bid = BidSerializer(read_only=True)
    currency = serializers.ReadOnlyField(source='currency.iso_code')
    amount = serializers.ReadOnlyField()

    class Meta:
        model = Payments
        fields = ('id', 'buyer', 'seller', 'bid', 'amount', 'currency', 'status', 'buyer_confirmation', 'seller_confirmation', 'transaction_date')

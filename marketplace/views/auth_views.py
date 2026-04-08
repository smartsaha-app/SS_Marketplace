import stripe
from django.conf import settings
from django.shortcuts import render
from rest_framework import generics, status, viewsets, permissions, serializers
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from marketplace.models.User_models import User
from marketplace.services.Notification_service import NotificationService

stripe.api_key = settings.STRIPE_SECRET_KEY

from marketplace.serializers import (
    UserSerializer,
)


class RegisterRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    id_categorie_user_id = serializers.IntegerField()
    password = serializers.CharField(write_only=True)


@swagger_auto_schema(
    request_body=RegisterRequestSerializer,
    responses={
        201: openapi.Response('Utilisateur créé avec succès'),
        400: 'Requête invalide'
    }
)

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_verified=False, is_active=False)

        # Créer un compte Stripe Express pour cet utilisateur
        stripe_account = stripe.Account.create(
            type="express",
            email=user.email,
            capabilities={"card_payments": {"requested": True}, "transfers": {"requested": True}},
        )

        # Enregistrer l'ID Stripe dans le modèle User
        user.stripe_account_id = stripe_account.id
        user.save()

        # Créer le lien d'onboarding Stripe
        account_link = stripe.AccountLink.create(
            account=stripe_account.id,
            refresh_url=f"{settings.FRONTEND_URL}/onboarding/refresh",
            return_url=f"{settings.FRONTEND_URL}/dashboard",
            type="account_onboarding",
        )

        # Notification aux admins
        message = (
            f"Nouvel utilisateur inscrit : {user.username} ({user.email})\n"
            f"Compte Stripe créé avec ID: {stripe_account.id}\n"
            f"Activer le compte pour lui permettre d'accéder au dashboard.\n\n"
            f"Accéder directement à la gestion de l’utilisateur : "
            f"https://sales.smart-saha.com//admin/users/{user.id}"
        )

        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            NotificationService.create_notification(
                user=admin,
                message=message,
                notification_type="user_registration",
                reference_id=user.id
            )

        headers = self.get_success_headers(serializer.data)

        # On renvoie aussi le lien Stripe pour que l'utilisateur complète son onboarding
        return Response(
            {
                "user": serializer.data,
                "stripe_onboarding_url": account_link.url
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

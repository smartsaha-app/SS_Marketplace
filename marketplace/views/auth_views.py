from django.shortcuts import render
from rest_framework import generics, status, viewsets, permissions, serializers
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from marketplace.models.User_models import User
from marketplace.services.Notification_service import NotificationService


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

        message = (
            f"Un nouvel utilisateur vient de s’inscrire sur la plateforme SmartSaha.\n\n"
            f"Nom d’utilisateur : {user.username}\n"
            f"Adresse email : {user.email}\n\n"
            f"Afin de garantir la sécurité et le bon fonctionnement de la plateforme, "
            f"merci de vérifier les informations de cet utilisateur et d’activer son compte.\n\n"
            f"L’activation est nécessaire pour lui permettre d’accéder à son dashboard "
            f"et de bénéficier pleinement des fonctionnalités de la marketplace "
            f"(publication d’annonces, participation aux enchères, messagerie, etc.).\n\n"
            f"Accéder directement à la gestion de l’utilisateur :\n"
            f"https://sales.smart-saha.com//admin/users/{user.id}\n\n"
            f"—\n"
            f"SmartSaha Marketplace\n"
            f"Système de notification automatique"
        )

        # Notification admin
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            NotificationService.create_notification(
                user=admin,
                message=message,
                notification_type="user_registration",
                reference_id=user.id
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

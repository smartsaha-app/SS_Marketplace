from django.shortcuts import render
from rest_framework import generics, status, viewsets, permissions, serializers
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from marketplace.models.Post_models import Post_status
from marketplace.serializers.User_serializers import CustomTokenObtainSerializer
from django.db.models import Q


from marketplace.models import (
      Chat, Message, Review, Favorite, Report, Notification, User
)
from marketplace.serializers import (
    ChatSerializer,
    MessageSerializer,
    ReviewSerializer,
    FavoriteSerializer,
    ReportSerializer,
    NotificationSerializer,
)
from marketplace.services.Post_service import changer_statut_post



class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Chats où l'utilisateur est propriétaire du post ou a envoyé un message
        return Chat.objects.filter(
            Q(id_post__user=user) | Q(message__id_user=user)
        ).distinct()

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        message = serializer.save(id_user=self.request.user)

        # Vérifier si le message est du propriétaire du post
        post = message.id_chat.id_post
        if message.id_user == post.user:
            # Changer le statut du post en "négociation"
            negotiation_status = Post_status.objects.get(name="négociation")
            try:
                changer_statut_post(
                    post_id=post.id,
                    statut_id=negotiation_status.id,
                    changed_by=self.request.user,
                    comment="Propriétaire a répondu, post en négociation"
                )
            except ValueError:
                pass


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Vérifie si l'utilisateur a une relation id_categorie_user
        id_categorie_user_data = None
        if hasattr(user, "id_categorie_user") and user.id_categorie_user:
            id_categorie_user_data = {
                "id": user.id_categorie_user.id,
                "categorie": user.id_categorie_user.categorie
            }
        
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "justificatif_url": getattr(user, "justificatif_url", None),
            "id_categorie_user": id_categorie_user_data,
            "id_categorie_user_id": getattr(user, "id_categorie_user_id", None),
            "password": "",  # ne jamais renvoyer le mot de passe réel pour la sécurité
        })

class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        # Appelle la méthode post parent pour générer les tokens
        response = super().post(request, *args, **kwargs)
        
        # La réponse contient le refresh token et access token dans response.data
        refresh_token = response.data.get('refresh')
        access_token = response.data.get('access')
        
        if refresh_token:
            # Supprime le refresh token du corps de la réponse JSON
            response.data.pop('refresh')

            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age=7*24*60*60,
                path='/api/token/refresh/',
            )
        
        # Réinjecte le data JSON sans refresh token dans la réponse
        response.data = {'access': access_token}

        return response

# class CustomTokenObtainPairView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         refresh_token = serializer.validated_data.get("refresh")
#         access_token = serializer.validated_data.get("access")

#         response = Response(
#             {"access": access_token},
#             status=200
#         )

#         if refresh_token:
#             response.set_cookie(
#                 key="refresh_token",
#                 value=refresh_token,
#                 httponly=True,
#                 secure=True,
#                 samesite="Strict",
#                 max_age=7*24*60*60,
#                 path="/api/token/refresh/",
#             )

#         return response

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({'error': 'No refresh token provided.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            return Response({'access': access_token})
        except Exception as e:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)


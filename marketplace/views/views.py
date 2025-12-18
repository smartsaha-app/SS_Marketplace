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
from rest_framework import status
from marketplace.models import Post_status
from django.db.models import Avg

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
        # Si Swagger ou user non authentifié
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Chat.objects.none()

        user = self.request.user
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

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_as_read(self, request):
        chat_id = request.data.get('chat_id')

        Message.objects.filter(
            id_chat_id=chat_id,
            is_read=False
        ).exclude(id_user=request.user).update(is_read=True)

        return Response({'status': 'ok'})


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(id_user_from=self.request.user)

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def user_reviews(self, request, user_id=None):
        user_id = int(user_id)  
        reviews = Review.objects.filter(id_user_to_id=user_id)
        average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

        serializer = ReviewSerializer(reviews, many=True)

        return Response({
            "average_rating": round(average_rating, 2),
            "reviews": serializer.data
        })

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            id_user=self.request.user,
            status="pending"
        )

    @action(detail=False, methods=["post"])
    def approve(self, request):
        """
        Approuver tous les reports d'un post et supprimer le post associé.
        """
        post_id = request.data.get("post_id")
        if not post_id:
            return Response({"error": "post_id requis"}, status=400)

        reports = Report.objects.filter(id_post__id=post_id)
        if not reports.exists():
            return Response({"error": "Aucun report trouvé pour ce post"}, status=404)

        # Marquer tous les reports comme approuvés
        reports.update(status="approved")

        # Supprimer le post
        post = reports.first().id_post
        try:
            deleted_status = Post_status.objects.get(name="supprimé")
            changer_statut_post(
                post_id=post.id,
                statut_id=deleted_status.id,
                changed_by=request.user,
                comment="Post supprimé via approbation de tous les reports"
            )
            post.is_active = False
            post.save()
        except Post_status.DoesNotExist:
            return Response({"error": "Le statut 'supprimé' n'existe pas"}, status=400)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        return Response({"detail": "Tous les reports approuvés et le post supprimé."}, status=200)


    
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retourne uniquement les notifications de l'utilisateur connecté
        user = self.request.user
        return Notification.objects.filter(id_user=user).order_by('-created_at')

    def perform_create(self, serializer):
        # Associer automatiquement la notification à l'utilisateur
        serializer.save(id_user=self.request.user)


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


from django.shortcuts import render
from rest_framework import generics, status, viewsets, permissions, serializers
from rest_framework.permissions import SAFE_METHODS
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from marketplace.models import (
    User, CategorieUser
)
from marketplace.serializers import (
    UserSerializer, CategorieUserSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # Seulement l’admin peut vérifier

    @action(detail=True, methods=['post'], url_path='verify')
    def verify_user(self, request, pk=None):
        user = self.get_object()
        user.is_verified = True
        user.is_active = True  
        user.save()
        return Response({"message": f"Utilisateur {user.username} vérifié avec succès."}, status=status.HTTP_200_OK)

class CategorieUserViewSet(viewsets.ModelViewSet):
    queryset = CategorieUser.objects.all()
    serializer_class = CategorieUserSerializer
    permission_classes = [permissions.IsAuthenticated]  # default

    def get_permissions(self):
        # Permettre l'accès public à list et retrieve
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]

        # Pour les autres actions, garder IsAuthenticated
        return [permission() for permission in self.permission_classes]

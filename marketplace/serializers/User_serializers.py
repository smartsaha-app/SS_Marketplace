from rest_framework import serializers
from marketplace.models import User, CategorieUser
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.contrib.auth import get_user_model

User = get_user_model()
class CustomTokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if not username or not password:
            raise AuthenticationFailed("Veuillez fournir nom d'utilisateur et mot de passe.")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise AuthenticationFailed("Nom d'utilisateur ou mot de passe incorrect.")

        # Vérifie le mot de passe manuellement
        if not user.check_password(password):
            raise AuthenticationFailed("Nom d'utilisateur ou mot de passe incorrect.")

        # Vérifie si le compte est actif
        if not user.is_active:
            raise PermissionDenied("Votre compte est actuellement inactif.")

        attrs["user"] = user
        return attrs


class CategorieUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorieUser
        fields = ['id', 'categorie']

class UserSerializer(serializers.ModelSerializer):
    id_categorie_user = CategorieUserSerializer(read_only=True)
    id_categorie_user_id = serializers.PrimaryKeyRelatedField(
        queryset=CategorieUser.objects.all(), source='id_categorie_user', write_only=True
    )
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'justificatif_url',
            'id_categorie_user',
            'id_categorie_user_id',
            'password',
            'is_verified',   
            'is_active',
            'avatar_url',
            'date_joined'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)  # hash sécurisé
        user.save()
        return user

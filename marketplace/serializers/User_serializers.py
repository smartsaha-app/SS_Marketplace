from rest_framework import serializers
from marketplace.models import User, CategorieUser
from django.contrib.auth import authenticate

class CustomTokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError("Veuillez fournir votre nom d'utilisateur et mot de passe.")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Nom d'utilisateur ou mot de passe incorrect.")
        
        if not user.is_active:
            raise serializers.ValidationError("Votre compte n'est pas actif. Veuillez contacter les administrateurs.")
        
        # Si tu as un champ is_verified ou autre
        if hasattr(user, 'is_verified') and not user.is_verified:
            raise serializers.ValidationError("Votre compte n'est pas encore vérifié.")

        attrs['user'] = user
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
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)  # hash sécurisé
        user.save()
        return user

from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.utils import timezone
import logging

from marketplace.models import Post, Bid, Bid_status, BidStatusRelation, Post_status, Currency, CategoriePost, \
    PostStatusRelation
from marketplace.serializers import (
    PostSerializer, PostDetailSerializer, BidSerializer,
    BidDetailSerializer, PlaceBidSerializer
)
from marketplace.models import IsOwnerOrReadOnly
from marketplace.serializers.Post_serializers import CurrencySerializer, CategoriePostSerializer, PostStatusSerializer
from rest_framework.decorators import api_view  # Import api_view
from marketplace.services.Post_service import changer_statut_post

logger = logging.getLogger(__name__)  # Ajout d’un logger

class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des annonces (posts)
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_permissions(self):
        """
        Permissions dynamiques selon l'action
        """
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
    
        if self.action == 'place_bid':
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        """Retourne le serializer approprié selon l'action"""
        if self.action == 'retrieve':
            return PostDetailSerializer
        elif self.action == 'place_bid':
            return PlaceBidSerializer
        return PostSerializer

    def get_queryset(self):
        """Filtre les posts selon les paramètres de requête"""
        queryset = Post.objects.select_related(
            'user', 'categorie_post', 'type_post', 'product', 'currency'
        ).prefetch_related(
            'bids', 'labels', 'status'
        )

        status_filter = self.request.query_params.get('status')
        category_filter = self.request.query_params.get('category_post')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if status_filter:
            queryset = queryset.filter(status__name=status_filter)
        if category_filter:
            queryset = queryset.filter(category__id=category_filter)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)

        statut, created = Post_status.objects.get_or_create(
            name="brouillon",
            defaults={"description": "Statut initial"}
        )

        PostStatusRelation.objects.create(
            post=post,
            status=statut,
            comment="Statut initial"
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_posts(self, request):
        """
        Récupère toutes les annonces de l'utilisateur connecté
        """
        user = request.user
        posts = Post.objects.filter(user=user).select_related(
            'categorie_post', 'type_post', 'product', 'currency'
        ).prefetch_related('labels', 'status', 'bids').order_by('-created_at')

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def place_bid(self, request, pk=None):
        post = self.get_object()
        serializer = PlaceBidSerializer(data=request.data, context={"request": request, "post": post})

        if serializer.is_valid():
            try:
                bid = serializer.save()
                bid_data = BidDetailSerializer(bid).data
                return Response({"message": "Enchère placée avec succès", "bid": bid_data}, status=201)
            except Exception as e:
                logger.exception(f"[Bid] Erreur interne : {str(e)}")
                return Response({"error": f"Erreur interne : {str(e)}"}, status=500)

        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['get'])
    def bids(self, request, pk=None):
        """
        Récupère toutes les enchères d'une annonce
        """
        post = self.get_object()
        bids = post.bids.select_related('user').prefetch_related('status_relations__status')

        status_filter = request.query_params.get('bid_status')
        if status_filter:
            bids = bids.filter(status_relations__status__name=status_filter)

        serializer = BidSerializer(bids, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def invalidate_posts(self, request):
        """
        Récupère toutes les annonces en brouillon
        """
        posts = Post.objects.filter()
        post = self.get_object()
        bids = post.bids.select_related('user').prefetch_related('status_relations__status')

        status_filter = request.query_params.get('bid_status')
        if status_filter:
            bids = bids.filter(status_relations__status__name=status_filter)

        serializer = BidSerializer(bids, many=True)
        return Response(serializer.data)


    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def validation_post(self, request, pk=None):
        post = self.get_object()  # récupère le Post via pk
        comment = request.data.get("comment", "")

        try:
            # Récupérer le statut "published" directement
            published_status = Post_status.objects.get(name="published")

            # Appeler le service pour changer le statut
            changer_statut_post(
                post_id=post.id,
                statut_id=published_status.id,
                changed_by=request.user,
                comment=comment
            )
        except Post_status.DoesNotExist:
            return Response({"error": "Le statut 'published' n'existe pas"}, status=400)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        return Response({"message": "Post publié avec succès"}, status=200)

    

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

class CategoriePostViewSet(viewsets.ModelViewSet):
    """
    Endpoint public pour récupérer toutes les catégories de produits
    """
    queryset = CategoriePost.objects.all()
    serializer_class = CategoriePostSerializer
    permission_classes = [AllowAny]

class PostStatusViewSet(viewsets.ModelViewSet):
    queryset = Post_status.objects.all()
    serializer_class = PostStatusSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        print("Payload reçu :", request.data)  # Debugging pour vérifier les données reçues
        try:
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
        response_serializer = self.get_serializer(instance) 
        print("Payload a envoyer :", response_serializer.data)  
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

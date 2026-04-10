from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.models import User
from django.conf import settings
from .models import Profil


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email    = request.data.get("email")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Nom d'utilisateur et mot de passe requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if User.objects.filter(username=username).exists():
            return Response(
                {"detail": "Ce nom d'utilisateur existe déjà."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(username=username, email=email, password=password)
        # Crée automatiquement un profil vide
        Profil.objects.create(user=user, avatar_type="initiales")
        return Response({"id": user.id, "username": user.username}, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profil, _ = Profil.objects.get_or_create(user=user)
        avatar_url = None
        if profil.avatar:
            avatar_url = request.build_absolute_uri(profil.avatar.url)
        return Response({
            "id":          user.id,
            "username":    user.username,
            "email":       user.email,
            "avatar_url":  avatar_url,
            "avatar_type": profil.avatar_type,
        })


class UpdateProfilView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def patch(self, request):
        user   = request.user
        profil, _ = Profil.objects.get_or_create(user=user)

        # Mise à jour du type d'avatar
        avatar_type = request.data.get("avatar_type")
        if avatar_type:
            profil.avatar_type = avatar_type
            # Si on repasse en initiales/homme/femme, on supprime la photo
            if avatar_type != "photo" and profil.avatar:
                profil.avatar.delete(save=False)
                profil.avatar = None

        # Mise à jour de la photo
        if "avatar" in request.FILES:
            if profil.avatar:
                profil.avatar.delete(save=False)
            profil.avatar      = request.FILES["avatar"]
            profil.avatar_type = "photo"

        profil.save()

        avatar_url = None
        if profil.avatar:
            avatar_url = request.build_absolute_uri(profil.avatar.url)

        return Response({
            "avatar_url":  avatar_url,
            "avatar_type": profil.avatar_type,
        })
from django.db import models
from django.contrib.auth.models import User


class Profil(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil")
    avatar     = models.ImageField(upload_to="avatars/", null=True, blank=True)
    avatar_type = models.CharField(
        max_length=20,
        choices=[("initiales", "Initiales"), ("homme", "Avatar homme"), ("femme", "Avatar femme"), ("photo", "Photo personnelle")],
        default="initiales"
    )

    def __str__(self):
        return f"Profil de {self.user.username}"

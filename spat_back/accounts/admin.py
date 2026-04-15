from django.contrib import admin
from .models import Profil


# ✅ Correction : enregistrement du modèle Profil dans l'admin
@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar_type')
    list_filter = ('avatar_type',)
    search_fields = ('user__username', 'user__email')
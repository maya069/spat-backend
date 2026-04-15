from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import RegisterView, MeView, UpdateProfilView

urlpatterns = [
    path('admin/',                     admin.site.urls),
    path('api/auth/token/',            TokenObtainPairView.as_view()),
    path('api/auth/token/refresh/',    TokenRefreshView.as_view()),
    path('api/auth/register/',         RegisterView.as_view()),
    path('api/auth/me/',               MeView.as_view()),
    path('api/auth/update-profil/',    UpdateProfilView.as_view()),
    path('api/logi/', include('logi.urls')),
    path('api/', include('logements.urls')), 
    path('api/employes/', include('employes.urls')), # ✅ Correction : ajout des routes logements
]

# ✅ Correction : servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
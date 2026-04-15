from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView, logout_view, me_view,
    DepartementViewSet, ServiceViewSet, EmployeViewSet,
    stats_globales,
)

router = DefaultRouter()
router.register(r'departements', DepartementViewSet, basename='departement')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'employes', EmployeViewSet, basename='employe')

urlpatterns = [
    # Auth
    path('auth/login/', LoginView.as_view(), name='token_obtain'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/me/', me_view, name='me'),
    # Stats
    path('stats/', stats_globales, name='stats_globales'),
    # CRUD
    path('', include(router.urls)),
]
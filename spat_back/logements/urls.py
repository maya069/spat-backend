from rest_framework.routers import DefaultRouter
from .views import LogementViewSet

router = DefaultRouter()
router.register(r"logements", LogementViewSet, basename="logement")

urlpatterns = router.urls
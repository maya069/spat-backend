from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Logement
from .serializers import LogementSerializer

@method_decorator(csrf_exempt, name='dispatch')
class LogementViewSet(viewsets.ModelViewSet):
    queryset           = Logement.objects.all()
    serializer_class   = LogementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [filters.SearchFilter]
    search_fields      = ["id_logement", "type_logement", "localisation", "statut"]
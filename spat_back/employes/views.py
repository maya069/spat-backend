from django.db.models import Avg, Count, Q
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Departement, Service, Employe
from .serializers import (
    DepartementSerializer, DepartementListSerializer,
    ServiceSerializer, ServiceListSerializer,
    EmployeSerializer, CustomTokenObtainPairSerializer,
)


# ─── Auth ─────────────────────────────────────────────────────────────────────
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Déconnexion réussie.'}, status=status.HTTP_200_OK)
    except Exception:
        return Response({'error': 'Token invalide.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_staff': user.is_staff,
        'date_joined': user.date_joined,
    })


# ─── Département ViewSet ──────────────────────────────────────────────────────
class DepartementViewSet(viewsets.ModelViewSet):
    queryset = Departement.objects.prefetch_related('services__employes').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name', 'full_name']
    ordering_fields = ['code', 'name', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return DepartementListSerializer
        return DepartementSerializer

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        dept = self.get_object()
        employes = Employe.objects.filter(service__departement=dept)
        data = {
            'code': dept.code,
            'name': dept.name,
            'nb_services': dept.services.count(),
            'nb_employes': employes.count(),
            'eligible_logement': employes.filter(anciennete__gte=2).count(),
            'anciennete_moyenne': employes.aggregate(avg=Avg('anciennete'))['avg'] or 0,
        }
        return Response(data)


# ─── Service ViewSet ──────────────────────────────────────────────────────────
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.select_related('departement').prefetch_related('employes').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'chef', 'departement__code']
    ordering_fields = ['name', 'departement__code']

    def get_serializer_class(self):
        if self.action == 'list':
            return ServiceListSerializer
        return ServiceSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        dept_code = self.request.query_params.get('departement')
        if dept_code:
            qs = qs.filter(departement__code=dept_code)
        return qs


# ─── Employé ViewSet ──────────────────────────────────────────────────────────
class EmployeViewSet(viewsets.ModelViewSet):
    queryset = Employe.objects.select_related('service__departement').all()
    serializer_class = EmployeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['prenom', 'nom', 'matricule', 'email', 'service__name', 'service__departement__code']
    ordering_fields = ['nom', 'prenom', 'matricule', 'anciennete', 'categorie', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        if dept := params.get('departement'):
            qs = qs.filter(service__departement__code=dept)
        if service := params.get('service'):
            qs = qs.filter(service_id=service)
        if categorie := params.get('categorie'):
            qs = qs.filter(categorie=categorie)
        if situation := params.get('situation'):
            qs = qs.filter(situation=situation)
        if eligible := params.get('eligible_logement'):
            if eligible.lower() == 'true':
                qs = qs.filter(anciennete__gte=2)
            elif eligible.lower() == 'false':
                qs = qs.filter(anciennete__lt=2)

        return qs

    def perform_create(self, serializer):
        # Auto-génère un matricule si non fourni
        if not serializer.validated_data.get('matricule'):
            import time
            matricule = f"MAT{str(int(time.time()))[-5:]}"
            serializer.save(matricule=matricule)
        else:
            serializer.save()


# ─── Stats globales ───────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_globales(request):
    employes = Employe.objects.all()
    total = employes.count()

    repartition_cat = dict(
        employes.values('categorie')
        .annotate(count=Count('id'))
        .values_list('categorie', 'count')
    )
    repartition_sit = dict(
        employes.values('situation')
        .annotate(count=Count('id'))
        .values_list('situation', 'count')
    )
    repartition_dept = list(
        Departement.objects.annotate(
            nb_emp=Count('services__employes')
        ).values('code', 'name', 'nb_emp')
    )

    return Response({
        'total_employes': total,
        'total_services': Service.objects.count(),
        'total_departements': Departement.objects.count(),
        'eligible_logement': employes.filter(anciennete__gte=2).count(),
        'anciennete_moyenne': round(employes.aggregate(avg=Avg('anciennete'))['avg'] or 0, 1),
        'repartition_categories': repartition_cat,
        'repartition_situations': repartition_sit,
        'repartition_departements': repartition_dept,
    })
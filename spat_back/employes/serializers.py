from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from .models import Departement, Service, Employe


# ─── JWT Custom Claims ────────────────────────────────────────────────────────
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'is_staff': self.user.is_staff,
        }
        return data


# ─── Employé ──────────────────────────────────────────────────────────────────
class EmployeSerializer(serializers.ModelSerializer):
    eligible_logement = serializers.ReadOnlyField()
    nom_complet = serializers.ReadOnlyField()
    departement_code = serializers.SerializerMethodField()
    departement_name = serializers.SerializerMethodField()

    class Meta:
        model = Employe
        fields = [
            'id', 'matricule', 'prenom', 'nom', 'nom_complet',
            'categorie', 'anciennete', 'situation', 'nb_enfants',
            'email', 'telephone', 'adresse', 'date_embauche', 'salaire',
            'service', 'departement_code', 'departement_name',
            'eligible_logement', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'eligible_logement', 'nom_complet']

    def get_departement_code(self, obj):
        return obj.service.departement.code

    def get_departement_name(self, obj):
        return obj.service.departement.name

    def validate_matricule(self, value):
        if not value.strip():
            raise serializers.ValidationError("Le matricule ne peut pas être vide.")
        return value.upper()

    def validate_nb_enfants(self, value):
        if value < 0:
            raise serializers.ValidationError("Le nombre d'enfants ne peut pas être négatif.")
        return value

    def validate_anciennete(self, value):
        if value < 0:
            raise serializers.ValidationError("L'ancienneté ne peut pas être négative.")
        return value


# ─── Service ──────────────────────────────────────────────────────────────────
class ServiceSerializer(serializers.ModelSerializer):
    employes = EmployeSerializer(many=True, read_only=True)
    nb_employes = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'chef', 'departement', 'employes', 'nb_employes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_nb_employes(self, obj):
        return obj.employes.count()


class ServiceListSerializer(serializers.ModelSerializer):
    nb_employes = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'chef', 'departement', 'nb_employes']

    def get_nb_employes(self, obj):
        return obj.employes.count()


# ─── Département ──────────────────────────────────────────────────────────────
class DepartementSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    nb_services = serializers.SerializerMethodField()
    nb_employes = serializers.SerializerMethodField()

    class Meta:
        model = Departement
        fields = [
            'id', 'code', 'name', 'full_name', 'icon_idx', 'color_idx',
            'services', 'nb_services', 'nb_employes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_nb_services(self, obj):
        return obj.services.count()

    def get_nb_employes(self, obj):
        return Employe.objects.filter(service__departement=obj).count()

    def validate_code(self, value):
        return value.upper().strip()


class DepartementListSerializer(serializers.ModelSerializer):
    nb_services = serializers.SerializerMethodField()
    nb_employes = serializers.SerializerMethodField()

    class Meta:
        model = Departement
        fields = ['id', 'code', 'name', 'full_name', 'icon_idx', 'color_idx', 'nb_services', 'nb_employes']

    def get_nb_services(self, obj):
        return obj.services.count()

    def get_nb_employes(self, obj):
        return Employe.objects.filter(service__departement=obj).count()


# ─── Stats ────────────────────────────────────────────────────────────────────
class StatsSerializer(serializers.Serializer):
    total_employes = serializers.IntegerField()
    total_services = serializers.IntegerField()
    total_departements = serializers.IntegerField()
    eligible_logement = serializers.IntegerField()
    anciennete_moyenne = serializers.FloatField()
    repartition_categories = serializers.DictField()
    repartition_situations = serializers.DictField()
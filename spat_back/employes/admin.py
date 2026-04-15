from django.contrib import admin
from .models import Departement, Service, Employe


class EmployeInline(admin.TabularInline):
    model = Employe
    extra = 0
    fields = ['matricule', 'prenom', 'nom', 'categorie', 'anciennete']


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0
    inlines = [EmployeInline]


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'full_name', 'services_count']
    search_fields = ['code', 'name']
    inlines = [ServiceInline]
    
    def services_count(self, obj):
        return obj.services.count()


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'departement', 'chef', 'employes_count']
    list_filter = ['departement']
    search_fields = ['name', 'chef']
    inlines = [EmployeInline]
    
    def employes_count(self, obj):
        return obj.employes.count()


@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    # ✅ Corrigé : utilisez les vrais noms de champs de votre modèle
    list_display = ['matricule', 'nom_complet', 'categorie', 'service', 'anciennete', 'eligible_logement']
    list_filter = ['categorie', 'situation', 'service__departement']
    search_fields = ['matricule', 'prenom', 'nom', 'email']
    autocomplete_fields = ['service']
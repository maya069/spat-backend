from django.db import models

# Create your models here.
from django.db import models


class Departement(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=255)
    icon_idx = models.IntegerField(default=0)
    color_idx = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Département'
        verbose_name_plural = 'Départements'

    def __str__(self):
        return f"{self.code} – {self.name}"


class Service(models.Model):
    departement = models.ForeignKey(
        Departement, on_delete=models.CASCADE, related_name='services'
    )
    name = models.CharField(max_length=150)
    chef = models.CharField(max_length=150, default='À définir')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Service'

    def __str__(self):
        return f"{self.name} ({self.departement.code})"


CATEGORIE_CHOICES = [
    ('Cadre supérieur', 'Cadre supérieur'),
    ('Cadre moyen', 'Cadre moyen'),
    ('Agent maîtrise', 'Agent maîtrise'),
    ('Agent exécution', 'Agent exécution'),
]

SITUATION_CHOICES = [
    ('Célibataire', 'Célibataire'),
    ('Marié', 'Marié'),
    ('Divorcé', 'Divorcé'),
    ('Veuf', 'Veuf'),
]


class Employe(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name='employes'
    )
    matricule = models.CharField(max_length=20, unique=True)
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    categorie = models.CharField(max_length=30, choices=CATEGORIE_CHOICES, default='Agent exécution')
    anciennete = models.IntegerField(default=0, help_text='Ancienneté en années')
    situation = models.CharField(max_length=20, choices=SITUATION_CHOICES, default='Célibataire')
    nb_enfants = models.IntegerField(default=0)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=30, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    date_embauche = models.DateField(blank=True, null=True)
    salaire = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nom', 'prenom']
        verbose_name = 'Employé'
        verbose_name_plural = 'Employés'

    def __str__(self):
        return f"{self.matricule} – {self.prenom} {self.nom}"

    @property
    def eligible_logement(self):
        return self.anciennete >= 2

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"
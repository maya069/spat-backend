from django.db import models


class Logement(models.Model):
    STATUT_CHOICES = [
        ("Disponible",  "Disponible"),
        ("Occupé",      "Occupé"),
        ("Maintenance", "Maintenance"),
    ]
    TYPE_CHOICES = [
        ("F2",     "F2"),
        ("F3",     "F3"),
        ("F4",     "F4"),
        ("Villa",  "Villa"),
        ("Studio", "Studio"),
    ]

    id_logement   = models.CharField(max_length=20, unique=True)  # ex: LOG-001
    type_logement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    localisation  = models.CharField(max_length=200)
    statut        = models.CharField(max_length=20, choices=STATUT_CHOICES, default="Disponible")
    capacite      = models.PositiveIntegerField(default=1)
    superficie    = models.FloatField(default=0)
    nb_occupants_max = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.id_logement} — {self.type_logement} ({self.statut})"

    class Meta:
        ordering = ["id_logement"]
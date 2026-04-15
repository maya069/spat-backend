from django.db import models


class Materiau(models.Model):
    nom       = models.CharField(max_length=100, unique=True)
    categorie = models.CharField(max_length=100)
    stock     = models.IntegerField(default=0)
    seuil     = models.IntegerField(default=10)
    unite     = models.CharField(max_length=50)
    prix      = models.IntegerField(default=0)  # en Ariary

    def __str__(self):
        return f"{self.nom} ({self.stock} {self.unite})"

    class Meta:
        verbose_name        = "Matériau"
        verbose_name_plural = "Matériaux"
        ordering            = ['nom']


class Mouvement(models.Model):
    TYPE_CHOICES = [("Entrée", "Entrée"), ("Sortie", "Sortie")]

    materiau    = models.ForeignKey(Materiau, on_delete=models.CASCADE, related_name="mouvements")
    type        = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantite    = models.IntegerField()
    date        = models.DateField(auto_now_add=True)
    logement    = models.CharField(max_length=20, blank=True)
    fournisseur = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.type} — {self.quantite} {self.materiau.nom} ({self.date})"

    def save(self, *args, **kwargs):
        # Met à jour le stock automatiquement à la création
        if not self.pk:
            if self.type == "Entrée":
                self.materiau.stock += self.quantite
            else:
                self.materiau.stock = max(0, self.materiau.stock - self.quantite)
            self.materiau.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name        = "Mouvement"
        verbose_name_plural = "Mouvements"
        ordering            = ['-date', '-id']
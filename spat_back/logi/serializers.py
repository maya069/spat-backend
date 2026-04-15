from rest_framework import serializers
from .models import Materiau, Mouvement


class MateriauSerializer(serializers.ModelSerializer):
    en_alerte = serializers.SerializerMethodField()

    class Meta:
        model  = Materiau
        fields = ['id', 'nom', 'categorie', 'stock', 'seuil', 'unite', 'prix', 'en_alerte']

    def get_en_alerte(self, obj):
        return obj.stock <= obj.seuil


class MouvementSerializer(serializers.ModelSerializer):
    materiau_nom = serializers.CharField(source='materiau.nom', read_only=True)
    materiau_id  = serializers.IntegerField(source='materiau.id', read_only=True)

    class Meta:
        model  = Mouvement
        fields = ['id', 'materiau', 'materiau_nom', 'materiau_id', 'type', 'quantite', 'date', 'logement', 'fournisseur']
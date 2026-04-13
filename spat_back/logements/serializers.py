from rest_framework import serializers
from .models import Logement


class LogementSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Logement
        fields = "__all__"
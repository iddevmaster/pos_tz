from rest_framework import serializers
from ..models import course, student


class courseSerializer(serializers.ModelSerializer):

    class Meta:
        model = course
        fields = ('__all__')


class studentSerializer(serializers.ModelSerializer):

    class Meta:
        model = student
        # fields = ('__all__')
        exclude = ['register']


class CustomPostSerializer(serializers.Serializer):
    search = serializers.CharField(max_length=100, default=None)
    year = serializers.DateField()

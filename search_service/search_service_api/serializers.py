from rest_framework.serializers import ModelSerializer

from .models import ResultSearch


class ResultSearchSerializer(ModelSerializer):
    class Meta:
        model = ResultSearch
        fields = ('query', 'result')

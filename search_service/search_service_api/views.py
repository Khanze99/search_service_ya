import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings

from .models import ResultSearch, SearchArea
from .serializers import ResultSearchSerializer


class HistoryList(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, user_id):
        results = ResultSearch.objects.filter(bot_user_id=user_id)
        serializer = ResultSearchSerializer(results, many=True)
        return Response(serializer.data, status=200)


class ResultSearchApiView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        query = request.data.get('query', None)
        user_id = request.data.get('user_id', None)

        areas = SearchArea.objects.values_list('name')

        url = settings.YANDEX_URL
        apikey = settings.YANDEX_GEOCODER_TOKEN

        if query and user_id:
            results = requests.get(url, params={
                'format': 'json',
                'apikey': apikey,
                'geocode': query
            }).json()

        return Response({"result": 'OK'}, status=201)

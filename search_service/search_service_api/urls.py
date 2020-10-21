from django.urls import path
from .views import HistoryList, ResultSearchApiView


urlpatterns = [
    path('history/<int:user_id>/', HistoryList.as_view()),
    path('query/', ResultSearchApiView.as_view())
]

from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

extra_patterns = [
    path('pages/', CrudPageAPI.as_view()),
    path('pages/<int:questionary_id>/', ListPagesAPI.as_view()),
    path('sections/', CrudSectionAPI.as_view()),
    path('sections/<int:questionary_id>/', ListSectionsAPI.as_view())
]

urlpatterns = [
    path('', include(extra_patterns)),
    path('', CrudQuestionaryAPI.as_view()),
    path('<int:study_id>/', ListQuestionariesAPI.as_view()),
    path('count/<int:study_id>/', CountQuestionariesAPI.as_view())
]
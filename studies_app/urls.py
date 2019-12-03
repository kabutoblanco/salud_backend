from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

extra_patterns = [
    path('all/', ListStudiesAPI.as_view(), name="read_all"),
    path('center/', CrudStudyCentersAPI.as_view()),
    path('user/', CrudStudyUsersAPI.as_view()),
    path('center/<int:study_id>/', CrudStudyCentersAPI.as_view()),
    path('user/<int:study_id>/', CrudStudyUsersAPI.as_view()),
    path('user/<int:user_id>/', CrudStudyUsersAPI.as_view()),
]

urlpatterns = [
    path('', include(extra_patterns)),
    path('', CrudStudiesAPI.as_view(), name="crud_write"),
    path('<int:study_id>/', CrudStudiesAPI.as_view(), name="crud_read"),
]

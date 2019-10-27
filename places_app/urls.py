from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

extra_patterns_center = [
    path('all/', ListCentersAPI.as_view(), name="read_all_center"),
]
extra_patterns_department = [
    path('all/', ListDeparmentsAPI.as_view(), name="read_all_department"),
]

urlpatterns = [
    # CRUD PLACES
    path('center/', include(extra_patterns_center)),
    path('department/', include(extra_patterns_department)),
    path('center/', CrudCentersAPI.as_view(), name="crud_write_center"),
    path('department/', CrudDepartmentsAPI.as_view(), name="crud_write_department"),
    # path('<str:email_instance>/', CrudCentersAPI.as_view(), name="crud_read"),
    # - - - - -
]
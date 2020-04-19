from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

extra_patterns = [
    path('all/', ListStudiesAPI.as_view(), name="read_all"),
    #OBTENER CENTROS Y USUARIOS RELACIONADOS CON EL UN ESTUDIO
    path('center/', CrudStudyCentersAPI.as_view()),
    path('user/', CrudStudyUsersAPI.as_view()),
    path('center/<int:study_id>/', CrudStudyCentersAPI.as_view()),
    path('user/<int:study_id>/', CrudStudyUsersAPI.as_view()),
    path('user/me/<int:user_id>/', CrudUserStudiesAPI.as_view()),
    #OBTENER LOS PERMISOS DE UN USUARIO SOBRE UN ESTUDIO
    path('user/permissions/<int:study_id>/', CrudPermissionsAPI.as_view()),
    path('user/study/<int:study_id>/', CrudStudyUserViewAPI.as_view()),
    path('center/count/<int:study_id>/', CountStudyCentersAPI.as_view())
]

urlpatterns = [
    path('', include(extra_patterns)),
    #CRUD STUDY
    path('', CrudStudiesAPI.as_view(), name="crud_write"),
    path('<int:study_id>/', CrudStudiesAPI.as_view(), name="crud_read"),
    path('user/my/<str:email_instance>/', CrudMeStudiesAPI.as_view(), name="crud_userme"),
    # DISEÑO CUESTIONARIO
    path('design/', CrudStudieDesignAPI.as_view(), name="crud_desig_study")
]

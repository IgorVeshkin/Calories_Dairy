from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *


# dairy_list = DayDairyViewSet.as_view({
#     'get': 'list',
#     'post': 'create',
# })

# dairy_detail = DayDairyViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy',
# })


# urlpatterns = [
#     path('', startup),
#     path('dairy', dairy_list, name='dairy'),
#     path('dairy/<uuid:pk>/', dairy_detail, name='dairy-detail'),
# ]


router = DefaultRouter()
router.register(
    "dairy",
    DayDairyViewSet,
    basename="dairy"
)

urlpatterns = [
    path("", include(router.urls)),
]

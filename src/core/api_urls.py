from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .api_views import ChoreViewSet, RewardViewSet, RedemptionViewSet, ProfileViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'chores', ChoreViewSet, basename='chore')
router.register(r'rewards', RewardViewSet, basename='reward')
router.register(r'redemptions', RedemptionViewSet, basename='redemption')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]

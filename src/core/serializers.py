from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Chore, Reward, Redemption, ChoreCompletion
from profiles.models import Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'role', 'points', 'parent']

class ChoreSerializer(serializers.ModelSerializer):
    chore_type_display = serializers.CharField(source='get_chore_type_display', read_only=True)
    
    class Meta:
        model = Chore
        fields = ['id', 'title', 'description', 'points_value', 'assigned_to', 'chore_type', 'chore_type_display', 'icon', 'created_at']

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['id', 'title', 'description', 'cost', 'icon', 'created_at']

class RedemptionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    reward = RewardSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Redemption
        fields = ['id', 'user', 'reward', 'status', 'status_display', 'claimed_at', 'processed_at']

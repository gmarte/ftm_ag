from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Chore, Reward, Redemption, ChoreCompletion
from profiles.models import Profile
from .serializers import ChoreSerializer, RewardSerializer, RedemptionSerializer, ProfileSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == Profile.Role.PARENT:
            return Profile.objects.filter(parent=user.profile) | Profile.objects.filter(user=user)
        return Profile.objects.filter(user=user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def log_behavior(self, request, pk=None):
        if request.user.profile.role != Profile.Role.PARENT:
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        kid_profile = self.get_object()
        action_type = request.data.get('action_type') # 'GOOD' or 'BAD'
        
        points_change = 0
        if action_type == 'GOOD':
            points_change = 100
        elif action_type == 'BAD':
            points_change = -10
            
        kid_profile.points += points_change
        if kid_profile.points < 0: 
            kid_profile.points = 0 # Prevent negative balances
            
        kid_profile.save()
        return Response({'status': 'success', 'new_points': kid_profile.points})

class ChoreViewSet(viewsets.ModelViewSet):
    serializer_class = ChoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == Profile.Role.PARENT:
            return Chore.objects.all() # Parents see all or filter by kids
        
        # Kid only sees their uncompleted daily chores or one-time chores
        today = timezone.now().date()
        completed_today_ids = ChoreCompletion.objects.filter(
            user=user, 
            completed_at__date=today
        ).values_list('chore_id', flat=True)

        all_assigned = Chore.objects.filter(assigned_to=user)
        active_chores = []
        for chore in all_assigned:
            if chore.chore_type == Chore.Type.DAILY:
                if chore.id not in completed_today_ids:
                    active_chores.append(chore.id)
            else:
                active_chores.append(chore.id)
                
        return Chore.objects.filter(id__in=active_chores)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        chore = self.get_object()
        user = request.user
        if chore.assigned_to != user:
            return Response({'error': 'Not assigned to you'}, status=status.HTTP_403_FORBIDDEN)
            
        today = timezone.now().date()
        if chore.chore_type == Chore.Type.DAILY:
            if ChoreCompletion.objects.filter(user=user, chore=chore, completed_at__date=today).exists():
                return Response({'error': 'Already completed today'}, status=status.HTTP_400_BAD_REQUEST)

        # Add points
        profile = user.profile
        profile.points += chore.points_value
        profile.save()
        
        # Log completion
        ChoreCompletion.objects.create(user=user, chore=chore)

        if chore.chore_type == Chore.Type.ONE_TIME:
            chore.delete()

        return Response({'status': 'completed', 'new_points': profile.points})

class RewardViewSet(viewsets.ModelViewSet):
    serializer_class = RewardSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Reward.objects.all().order_by('-created_at')

    @action(detail=True, methods=['post'])
    def redeem(self, request, pk=None):
        reward = self.get_object()
        profile = request.user.profile
        
        if profile.points >= reward.cost:
            profile.points -= reward.cost
            profile.save()
            redemption = Redemption.objects.create(user=request.user, reward=reward, status=Redemption.Status.PENDING)
            return Response({'status': 'success', 'new_points': profile.points, 'redemption_id': redemption.id})
        return Response({'error': 'Not enough points'}, status=status.HTTP_400_BAD_REQUEST)

class RedemptionViewSet(viewsets.ModelViewSet):
    serializer_class = RedemptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == Profile.Role.PARENT:
            return Redemption.objects.all().order_by('-claimed_at')
        return Redemption.objects.filter(user=user).order_by('-claimed_at')

    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        if request.user.profile.role != Profile.Role.PARENT:
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        redemption = self.get_object()
        action_type = request.data.get('action') # 'approve' or 'reject'
        
        if redemption.status != Redemption.Status.PENDING:
            return Response({'error': 'Already processed'}, status=status.HTTP_400_BAD_REQUEST)

        if action_type == 'approve':
            redemption.status = Redemption.Status.APPROVED
        elif action_type == 'reject':
            redemption.status = Redemption.Status.REJECTED
            kid_profile = redemption.user.profile
            kid_profile.points += redemption.reward.cost
            kid_profile.save()
            
        redemption.processed_at = timezone.now()
        redemption.save()
        return Response({'status': 'processed', 'new_status': redemption.status})

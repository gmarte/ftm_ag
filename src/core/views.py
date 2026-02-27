from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Sum
from django.utils import timezone
from profiles.models import Profile
from .models import Chore, Reward, Redemption, BehaviorLog, ChoreCompletion

@login_required
def dashboard_view(request):
    """
    Redirects to the appropriate dashboard based on the user's role.
    """
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)
    
    if request.user.profile.role == Profile.Role.PARENT:
        return redirect('parent_dashboard')
    elif request.user.profile.role == Profile.Role.KID:
        return redirect('kid_dashboard')
    else:
        # Fallback
        return redirect('parent_dashboard') # Default to parent for now

@login_required
def parent_dashboard(request):
    if request.user.profile.role != Profile.Role.PARENT:
        return redirect('dashboard')
    
    kids = request.user.profile.kids.all()
    # If no specific kids linked yet, maybe show all kids? For now, assume linkage is manual or we show all kids in system for simple MVP
    # Actually, let's just show all profiles with role KID for this MVP to make it easy to test
    if not kids.exists():
        kids = Profile.objects.filter(role=Profile.Role.KID)

    pending_redemptions = Redemption.objects.filter(status=Redemption.Status.PENDING)
    
    context = {
        'kids': kids,
        'pending_redemptions': pending_redemptions,
    }
    return render(request, 'dashboard/parent.html', context)

@login_required
def kid_dashboard(request):
    if request.user.profile.role != Profile.Role.KID:
        return redirect('dashboard')
    
    profile = request.user.profile
    # Chores assigned to this kid
    all_assigned_chores = Chore.objects.filter(assigned_to=request.user)
    
    # Filter out daily chores completed today
    from django.utils import timezone
    today = timezone.now().date()
    
    completed_today_ids = ChoreCompletion.objects.filter(
        user=request.user, 
        completed_at__date=today
    ).values_list('chore_id', flat=True)
    
    # Show chore if it's ONE_TIME (and exists) OR if it's DAILY and NOT in completed_today_ids
    # Note: ONE_TIME chores are deleted on completion, so we just need to filter DAILY ones.
    
    active_chores = []
    for chore in all_assigned_chores:
        if chore.chore_type == Chore.Type.DAILY:
            if chore.id not in completed_today_ids:
                active_chores.append(chore)
        else:
            active_chores.append(chore)

    available_rewards = Reward.objects.all()
    
    context = {
        'profile': profile,
        'chores': active_chores,
        'rewards': available_rewards,
    }
    return render(request, 'dashboard/kid.html', context)

# API/Action Views
# ... (log_behavior stays same)

@login_required
def log_behavior(request, kid_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    if request.user.profile.role != Profile.Role.PARENT:
        return HttpResponseForbidden()

    kid_profile = get_object_or_404(Profile, id=kid_id)
    action_type = request.POST.get('action_type') # GOOD or BAD
    
    points_change = 0
    if action_type == 'GOOD':
        points_change = 100
        BehaviorLog.objects.create(user=kid_profile.user, action_type=BehaviorLog.ActionType.GOOD, points_change=points_change)
    elif action_type == 'BAD':
        points_change = -10
        BehaviorLog.objects.create(user=kid_profile.user, action_type=BehaviorLog.ActionType.BAD, points_change=points_change)
    
    kid_profile.points += points_change
    if kid_profile.points < 0: kid_profile.points = 0 # No negative balance
    kid_profile.save()

    return redirect('parent_dashboard')

@login_required
def complete_chore(request, chore_id):
    chore = get_object_or_404(Chore, id=chore_id)
    if chore.assigned_to != request.user:
         return HttpResponseForbidden()
    
    # Check if already completed today if daily
    from django.utils import timezone
    today = timezone.now().date()
    if chore.chore_type == Chore.Type.DAILY:
        if ChoreCompletion.objects.filter(user=request.user, chore=chore, completed_at__date=today).exists():
            # Already done today, don't give points (prevent spam/refresh hacks)
            return redirect('kid_dashboard')

    # Add points
    profile = request.user.profile
    profile.points += chore.points_value
    profile.save()
    
    # Log completion
    ChoreCompletion.objects.create(user=request.user, chore=chore)

    # If ONE_TIME, delete it
    if chore.chore_type == Chore.Type.ONE_TIME:
        chore.delete()

    return redirect('kid_dashboard')

@login_required
def redeem_reward(request, reward_id):
    reward = get_object_or_404(Reward, id=reward_id)
    profile = request.user.profile
    
    if profile.points >= reward.cost:
        profile.points -= reward.cost
        profile.save()
        Redemption.objects.create(user=request.user, reward=reward, status=Redemption.Status.PENDING)
    
    return redirect('kid_dashboard')

# --- Frontend Task Management (Parent) ---

@login_required
def parent_task_list(request):
    if request.user.profile.role != Profile.Role.PARENT:
        return redirect('dashboard')
        
    kids = request.user.profile.kids.all()
    if not kids.exists():
        kids = Profile.objects.filter(role=Profile.Role.KID)

    if request.method == 'POST':
        # Simple task creation
        title = request.POST.get('title')
        points = int(request.POST.get('points', 10))
        assigned_to_id = request.POST.get('assigned_to')
        chore_type = request.POST.get('chore_type', Chore.Type.DAILY)
        icon = request.POST.get('icon', '📝')
        
        assigned_user = None
        if assigned_to_id:
            kid_profile = get_object_or_404(Profile, id=assigned_to_id)
            assigned_user = kid_profile.user
            
        if title and assigned_user:
            Chore.objects.create(
                title=title,
                points_value=points,
                assigned_to=assigned_user,
                chore_type=chore_type,
                icon=icon
            )
            return redirect('parent_tasks')

    # Assign chores
    # To simplify, show all chores assigned to any kid linked.
    kid_users = [k.user for k in kids]
    chores = Chore.objects.filter(assigned_to__in=kid_users).order_by('-created_at')
    
    context = {
        'chores': chores,
        'kids': kids,
    }
    return render(request, 'dashboard/tasks.html', context)

@login_required
def delete_task(request, task_id):
    if request.user.profile.role != Profile.Role.PARENT:
        return HttpResponseForbidden()
    
    task = get_object_or_404(Chore, id=task_id)
    task.delete()
    return redirect('parent_tasks')

# --- Frontend Reward Management (Parent) ---

@login_required
def parent_reward_list(request):
    if request.user.profile.role != Profile.Role.PARENT:
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        cost = int(request.POST.get('cost', 50))
        icon = request.POST.get('icon', '🎁')
        
        if title:
            Reward.objects.create(
                title=title,
                cost=cost,
                icon=icon
            )
            return redirect('parent_rewards')

    rewards = Reward.objects.all().order_by('-created_at')
    
    context = {
        'rewards': rewards,
    }
    return render(request, 'dashboard/rewards.html', context)

@login_required
def delete_reward(request, reward_id):
    if request.user.profile.role != Profile.Role.PARENT:
        return HttpResponseForbidden()
    
    reward = get_object_or_404(Reward, id=reward_id)
    reward.delete()
    return redirect('parent_rewards')

@login_required
def manage_redemption(request, redemption_id, action):
    if request.user.profile.role != Profile.Role.PARENT:
        return redirect('dashboard')
        
    redemption = get_object_or_404(Redemption, id=redemption_id)
    if request.method == 'POST' and redemption.status == Redemption.Status.PENDING:
        if action == 'approve':
            redemption.status = Redemption.Status.APPROVED
        elif action == 'reject':
            redemption.status = Redemption.Status.REJECTED
            # Refund points to the kid
            kid_profile = redemption.user.profile
            kid_profile.points += redemption.reward.cost
            kid_profile.save()
            
        redemption.processed_at = timezone.now()
        redemption.save()
        
    return redirect('parent_dashboard')

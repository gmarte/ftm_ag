import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from profiles.models import Profile
from core.models import Chore, Reward, Redemption, BehaviorLog

User = get_user_model()

def verify():
    print("Verifying setup...")

    # Clean up
    User.objects.all().delete()
    
    # 1. Create Parent
    parent_user = User.objects.create_user(username='parent', password='password123', email='parent@example.com')
    # Profile should be created automatically by signal?
    # Profile.objects.create(user=parent_user, role=Profile.Role.PARENT) - signal handles this? 
    # Let's check if signal worked.
    if not hasattr(parent_user, 'profile'):
         Profile.objects.create(user=parent_user, role=Profile.Role.PARENT)
    else:
        parent_user.profile.role = Profile.Role.PARENT
        parent_user.profile.save()
    
    print(f"Parent created: {parent_user.username} - Role: {parent_user.profile.role}")

    # 2. Create Kid
    kid_user = User.objects.create_user(username='kid', password='password123', email='kid@example.com')
    if not hasattr(kid_user, 'profile'):
         Profile.objects.create(user=kid_user, role=Profile.Role.KID)
    else:
        kid_user.profile.role = Profile.Role.KID
        kid_user.profile.parent = parent_user.profile
        kid_user.profile.save()

    print(f"Kid created: {kid_user.username} - Role: {kid_user.profile.role} - Parent: {kid_user.profile.parent.user.username}")

    # 3. Create Chore
    chore = Chore.objects.create(
        title="Clean Room",
        description="Pick up toys",
        points_value=50,
        assigned_to=kid_user,
        icon="🧹"
    )
    print(f"Chore created: {chore.title} for {chore.assigned_to.username}")

    # 4. Create Reward
    reward = Reward.objects.create(
        title="Ice Cream",
        cost=100,
        icon="🍦"
    )
    print(f"Reward created: {reward.title} cost {reward.cost}")

    # 5. Complete Chore (Simulate View Logic)
    # Kid gains points
    kid_user.profile.points += chore.points_value
    kid_user.profile.save()
    print(f"Chore completed. Kid points: {kid_user.profile.points}")
    
    # 6. Log Bad Behavior (Simulate View Logic)
    # Kid loses points
    kid_user.profile.points -= 10
    kid_user.profile.save()
    BehaviorLog.objects.create(user=kid_user, action_type=BehaviorLog.ActionType.BAD, points_change=-10)
    print(f"Bad behavior logged. Kid points: {kid_user.profile.points}")

    # 7. Redeem Reward (Simulate View Logic)
    # Should fail if not enough points (40 < 100)
    if kid_user.profile.points >= reward.cost:
        print("Redeeming reward...")
        kid_user.profile.points -= reward.cost
        kid_user.profile.save()
        Redemption.objects.create(user=kid_user, reward=reward)
    else:
        print(f"Not enough points to redeem {reward.title}. Needs {reward.cost}, has {kid_user.profile.points}")

    # 8. Add more points to test redemption
    kid_user.profile.points += 100
    kid_user.profile.save()
    print(f"Added 100 points. Kid points: {kid_user.profile.points}")

    if kid_user.profile.points >= reward.cost:
        kid_user.profile.points -= reward.cost
        kid_user.profile.save()
        Redemption.objects.create(user=kid_user, reward=reward)
        print(f"Redemption successful! Remaining points: {kid_user.profile.points}")
        
verify()

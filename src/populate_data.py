import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from profiles.models import Profile
from core.models import Chore, Reward

User = get_user_model()

def populate():
    print("Populating data...")
    
    # 1. Create Parent (if not exists)
    parent, _ = User.objects.get_or_create(username='parent', defaults={'email': 'parent@example.com'})
    if _:
        parent.set_password('password123')
        parent.save()
        # Profile created by signal
    
    parent_profile = parent.profile
    parent_profile.role = Profile.Role.PARENT
    parent_profile.save()
    print(f"Parent: {parent.username}")

    # 2. Ian (12yo, Autism, User ID 19)
    try:
        ian = User.objects.get(id=19)
        ian.username = 'Ian'
        ian.save()
    except User.DoesNotExist:
        try:
            ian = User.objects.create(id=19, username='Ian', email='ian@example.com')
            ian.set_password('password123')
            ian.save()
        except Exception as e:
            print(f"Could not force ID 19: {e}. Creating standard user 'Ian'.")
            ian, _ = User.objects.get_or_create(username='Ian', defaults={'email': 'ian@example.com'})
            if _:
                ian.set_password('password123')
                ian.save()
    
    # Update profile
    ian_profile = ian.profile
    ian_profile.role = Profile.Role.KID
    ian_profile.parent = parent_profile
    ian_profile.save()
    print(f"Ian: {ian.username} (ID: {ian.id})")

    # Ian's Chores (Daily)
    ian_chores = [
        ("Brush Teeth", "Morning and Night", 10, "🪥"),
        ("Make Bed", "Arrange pillows and blanket", 20, "🛏️"),
        ("Put Dishes Away", "After eating", 15, "🍽️"),
        ("Clean Table", "Wipe it down", 15, "🧽")
    ]
    
    for title, desc, points, icon in ian_chores:
        Chore.objects.get_or_create(
            title=title,
            assigned_to=ian,
            defaults={
                'description': desc,
                'points_value': points,
                'icon': icon,
                'chore_type': Chore.Type.DAILY
            }
        )

    # 3. Gael (7yo, Soccer)
    gael, _ = User.objects.get_or_create(username='Gael', defaults={'email': 'gael@example.com'})
    if _:
        gael.set_password('password123')
        gael.save()
    
    gael_profile = gael.profile
    gael_profile.role = Profile.Role.KID
    gael_profile.parent = parent_profile
    gael_profile.save()
    print(f"Gael: {gael.username}")

    # Gael's Chores (Soccer focus)
    gael_chores = [
        ("Soccer Practice", "Practice dribbling for 15 mins", 30, "⚽"),
        ("Put Away Toys", "Clear the floor", 10, "🧸"),
        ("Help with Dinner", "Set the table", 20, "🍴")
    ]
    
    for title, desc, points, icon in gael_chores:
        Chore.objects.get_or_create(
            title=title,
            assigned_to=gael,
            defaults={
                'description': desc,
                'points_value': points,
                'icon': icon,
                'chore_type': Chore.Type.DAILY 
            }
        )

    # 4. Rewards
    rewards = [
        ("Roblox Time (30m)", 150, "🎮"),
        ("Ice Cream Treat", 200, "🍦"),
        ("New Soccer Ball", 500, "⚽"),
        ("Pizza Night", 300, "🍕")
    ]
    
    for title, cost, icon in rewards:
        Reward.objects.get_or_create(
            title=title,
            defaults={
                'cost': cost,
                'icon': icon
            }
        )

    print("Data populated successfully.")

if __name__ == '__main__':
    populate()

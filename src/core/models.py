from django.conf import settings
from django.db import models

class Chore(models.Model):
    class Type(models.TextChoices):
        ONE_TIME = 'ONE_TIME', 'One Time'
        DAILY = 'DAILY', 'Daily'

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    points_value = models.IntegerField(default=10)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_chores')
    chore_type = models.CharField(max_length=20, choices=Type.choices, default=Type.ONE_TIME)
    icon = models.CharField(max_length=50, default="🧹", help_text="Emoji or Icon name")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.points_value} pts)"

class ChoreCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chore_completions')
    chore = models.ForeignKey(Chore, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.chore.title} - {self.completed_at}"

class Reward(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cost = models.IntegerField(default=50)
    icon = models.CharField(max_length=50, default="🎁", help_text="Emoji or Icon name")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.cost} pts)"

class Redemption(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='redemptions')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    claimed_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} redeemed {self.reward.title} - {self.status}"

class BehaviorLog(models.Model):
    class ActionType(models.TextChoices):
        GOOD = 'GOOD', 'Good Behavior'
        BAD = 'BAD', 'Bad Behavior'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='behavior_logs')
    action_type = models.CharField(max_length=10, choices=ActionType.choices)
    points_change = models.IntegerField() # Positive for good, negative for bad
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.action_type} ({self.points_change})"

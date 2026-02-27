from django.contrib import admin
from .models import Chore, Reward, Redemption, BehaviorLog

admin.site.register(Chore)
admin.site.register(Reward)
admin.site.register(Redemption)
admin.site.register(BehaviorLog)

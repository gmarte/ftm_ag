from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/parent/', views.parent_dashboard, name='parent_dashboard'),
    path('dashboard/kid/', views.kid_dashboard, name='kid_dashboard'),
    path('log-behavior/<int:kid_id>/', views.log_behavior, name='log_behavior'),
    path('complete-chore/<int:chore_id>/', views.complete_chore, name='complete_chore'),
    path('redeem-reward/<int:reward_id>/', views.redeem_reward, name='redeem_reward'),
    
    # Parent Manage Tasks & Rewards
    path('dashboard/parent/tasks/', views.parent_task_list, name='parent_tasks'),
    path('dashboard/parent/tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    
    path('dashboard/parent/rewards/', views.parent_reward_list, name='parent_rewards'),
    path('dashboard/parent/rewards/<int:reward_id>/delete/', views.delete_reward, name='delete_reward'),
    
    path('dashboard/parent/redemptions/<int:redemption_id>/<str:action>/', views.manage_redemption, name='manage_redemption'),
]

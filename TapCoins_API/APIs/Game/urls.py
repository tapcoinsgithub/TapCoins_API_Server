from django.urls import path
from .views import send_points, create_game, check_in_game, get_user_and_game, start_user_streak


app_name = "game_api"
urlpatterns = [
    # Send points contains Update Players wins function BC
    path('sendPoints', send_points, name="sendPoints"),
    path('createGame', create_game, name="createGame"),
    path('check_in_game', check_in_game, name="check_in_game"),
    path('get_user_and_game', get_user_and_game, name="getUserAndGame"),
    path('start_user_streak', start_user_streak, name="startUserStreak")
]
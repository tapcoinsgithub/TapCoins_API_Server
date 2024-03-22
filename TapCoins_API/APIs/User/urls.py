from django.urls import path
from .views import registration_view, get_user, logout_view, login_view, guest_login, send_username, send_code, change_password, save, save_location, get_leaderboard_data, confirm_password, testing_cloud, test_celery


app_name = "user_api"
urlpatterns = [
    path('testing', testing_cloud, name="testingCloud"),
    path('register', registration_view, name="register"),
    path('info', get_user, name="getUser"),
    path('login', login_view, name="login"),
    path('logout', logout_view, name="logout"),
    path('guestLogin', guest_login, name="guestLogin"),
    path("send_username", send_username, name="sendUsername"),
    path("send_code", send_code, name="sendCode"),
    path("change_password", change_password, name="changePassword"),
    path("save", save, name="save"),
    path("confirm_password", confirm_password, name="confirmPassword"),
    path("save_location", save_location, name="saveLocation"),
    path("get_leaderboard_data", get_leaderboard_data, name="getLeaderboardData"),
    path("test_celery", test_celery, name="test_celery")
]
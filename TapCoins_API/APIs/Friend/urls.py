from django.urls import path
from .views import send_friendRequest, accept_friendRequest, decline_friendRequest, remove_friend, send_invite, ad_invite


app_name = "friend_api"
urlpatterns = [
    path('sfr', send_friendRequest, name="sendFriendRequest"),
    path("afr", accept_friendRequest, name="acceptFriendRequest"),
    path("dfr", decline_friendRequest, name="declineFriendRequest"),
    path("remove_friend", remove_friend, name="removeFriend"),
    path("send_invite", send_invite, name="sendInvite"),
    path("ad_invite", ad_invite, name="accept/declineInvite"),
]
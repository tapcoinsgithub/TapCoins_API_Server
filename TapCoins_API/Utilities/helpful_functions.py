from datetime import datetime, timedelta
from ..models import User, Token

# Ping function for Users activity
def ping(active, _token):
    token = Token.objects.get(token=_token)
    user = User.objects.get(token=token)
    user.last_active_date = datetime.now()
    user.is_active = True
    user.save()
    print(f"Username: {user.username}, is_active: {user.is_active}")
    return "Active"
    
# Find time difference between two dates for active users logic
def find_time_difference(date1, date2):
    time_difference = abs(date1 - date2)
    return time_difference >= timedelta(minutes=5)
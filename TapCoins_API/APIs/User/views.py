from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import RegistrationSerializer, GetUserSerializer, LoginSerializer, TestPasswordSerializer
from ...models import *
from decouple import config
import binascii
import os
import bcrypt
import requests
from random import randrange
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.http import HttpResponse
import re
from ...task import start_time_limit_for_users_streaks
# from google.cloud import recaptchaenterprise_v1
# Make sure each function is getting the Users token from the request in order to send the users token
# to the ping function. Reg, Login and Logout will call the ping function at the end only.

@api_view(['POST'])
def registration_view(request):
    if request.method == 'POST':
        print("REQUEST DATA BELOW")
        print(request.data)
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            print("SERIALIZER IS VALID")
            user = serializer.save()
            print(type(user))
            if type(user) == str:
                data["error"] = user
                data["isErr"] = True
                return Response(data)
            print(user.username)
            data['response'] = "Success"
            data['username'] = user.username
            user1 = User.objects.get(username=data['username'])
            token = user1.token
            data['token'] = token.token
            user1.in_game = False
            user1.in_queue = False
            user1.logged_in = True
            if request.data['first_name'] != "":
                user1.first_name = request.data['first_name']
            if request.data['last_name'] != "":
                user1.last_name = request.data['last_name']
            if request.data['phone_number'] != "":
                validate_phone_number_pattern = "^\\+?[1-9][0-9]{7,14}$"
                is_valid_phone_number = re.match(validate_phone_number_pattern, request.data['phone_number'])
                print("IS VALID PHONE NUMBER BELOW")
                print(is_valid_phone_number)
                if is_valid_phone_number:
                    user1.phone_number = request.data['phone_number']
                    user1.has_phone_number = True
                else:
                    user1.delete()
                    data = {
                        "response": "Invalid phone number.",
                        "token": "Invalid.",
                        "username": "Invalid."
                    }
                    return Response(data)
            # ping(True, token.token)
            u = User.objects.get(token=token)
            u.is_active = True
            u.last_active_date = datetime.now()
            u.save()
            user1.save()
        else:
            data = serializer.errors
            print("DATA ERROR IS BELOW")
            print(data)
        print("RETURNING DATA BELOW")
        print(data)
        return Response(data)

@api_view(['POST'])
def login_view(request):
    serializer = LoginSerializer(data=request.data)

    data = {}
    if serializer.is_valid():
        user = serializer.save()
        if type(user) == dict:
            return Response(user)
        data['response'] = "Success"
        data['username'] = user.username
        user1 = User.objects.get(username=user.username)
        if user1.logged_in:
            newData = {
                'log_in_error': "User already logged in."
            }
            return Response(newData)
        user1.in_game = False
        user1.in_queue = False
        user1.logged_in = True
        # user1.has_wallet = True # Remove this later
        user1.save()
        token = binascii.hexlify(os.urandom(config('TOKEN', cast=int))).decode()
        token1 = user1.token
        token1.token = token
        token1.save()
        data['token'] = token
        print("THE TOKEN IS BELOW")
        print(token)
        # ping(True, token)
        u = User.objects.get(token=token1)
        u.is_active = True
        u.last_active_date = datetime.now()
        u.save()
    else:
        data = serializer.errors
    return Response(data)

@api_view(['GET'])
def get_user(request):
    print("**********")
    print("**********")
    print("**********")
    print("IN GET USER")
    token = request.GET.get('token', None)
    print(token)
    de_queue = request.GET.get('de_queue', None)
    newData = {
        "token": token
    }
    # Validate and process the parameters as needed
    if token is not None and de_queue is not None:
        pass
    else:
        # Handle invalid or missing parameters
        print("INVALID OR MISSING PARAMETERS")
        error_response = {
            'error': 'Invalid or missing parameters',
        }
        return Response(error_response, status=400)
    
    serializer = GetUserSerializer(data=newData)

    data = {}

    if serializer.is_valid():
        print("SERIALIZER VALID")
        user = serializer.save()
        data['response'] = "Getting your information"
        data['username'] = user.username
        data['hasInvite'] = False
        if user.first_name:
            data['first_name'] = user.first_name
        else:
            data['first_name'] = ""
        if user.last_name:
            data['last_name'] = user.last_name
        else:
            data['last_name'] = ""
        try:
            data['wins'] = user.wins
            data['losses'] = user.losses
            data['best_streak'] = user.best_streak
            data['win_streak'] = user.win_streak
        except:
            pass
        active_friends_index_list = []
        if type(user.friends) == list:
            print("USER HAS FRIENDS")
            friend_names = []
            index_count = 0
            for friend_id in user.friends:
                friend = FriendModel.objects.get(id=friend_id)
                temp_friend = None
                
                if user.username == friend.sending_user:
                    temp_friend = User.objects.get(username=friend.receiving_user)
                    if friend.pending_request:
                        friend_line = "Pending request to " + friend.receiving_user
                        friend_names.append(friend_line)
                    else:
                        if user.has_game_invite:
                            try:
                                GameInvite.objects.get(sender=friend.receiving_user)
                                friend_line = "Game invite from " + friend.receiving_user
                                friend_names.append(friend_line)
                                data['hasInvite'] = True
                            except:
                                friend_names.append(friend.receiving_user)
                        else:
                            data['hasInvite'] = False
                            friend_names.append(friend.receiving_user)
                else:
                    print("FRIEND IS NOT SENDING USER")
                    temp_friend = User.objects.get(username=friend.sending_user)
                    if friend.pending_request:
                        friend_line = "Friend request from " + friend.sending_user
                        friend_names.append(friend_line)
                    else:
                        print("IT IS NOT A PENDING REQUEST")
                        if user.has_game_invite:
                            print("USER HAS GAME INVITES?")
                            try:
                                GameInvite.objects.get(sender=friend.sending_user)
                                friend_line = "Game invite from " + friend.sending_user
                                friend_names.append(friend_line)
                                data['hasInvite'] = True
                                print("PASSED THE TRY")
                            except:
                                print("IN THE EXCEPT")
                                friend_names.append(friend.sending_user)
                        else:
                            print("USER DOES NOT HAVE GAME INVITE")
                            print(friend.sending_user)
                            print(friend.receiving_user)
                            data['hasInvite'] = False
                            friend_names.append(friend.sending_user)
                if temp_friend.is_active:
                    print("THE TEMP FRIEND IS ACTIVE HERE")
                    print(temp_friend.username)
                    print(temp_friend.is_active)
                    active_friends_index_list.append(index_count)
                index_count += 1
            data['friends'] = friend_names
            print("######")
            print("######")
            print("######")
            print("FRIENDS BELOW")
            print(data['friends'])
            print("######")
            print("######")
            print("######")
            data['active_friends_index_list'] = active_friends_index_list
        else:
            print("USER HAS 0 FRIENDS")
            data['friends'] = ["0"]
        data['is_guest'] = user.is_guest
        data['has_wallet'] = user.has_wallet
        if user.phone_number:
            data['phone_number'] = user.phone_number
            user.has_phone_number = True
            data['HPN'] = True
            user.save()
        else:
            data['phone_number'] = "No Phone number"
            data['HPN'] = False
        # ping(True, token)
        # u = User.objects.get(token=token)
        user.is_active = True
        user.last_active_date = datetime.now()
        user.save()
        user.save()
        if user.has_location == True:
            data['has_location'] = True
        else:
            data['has_location'] = False
        
        users_games = user.wins + user.losses
        if users_games >= 25:
            league_placement_val = league_placement(user.wins, users_games)
            if league_placement_val:
                user.league = league_placement_val
                user.save()
                data['league_placement'] = league_placement_val
        else:
            data['league_placement']  = 1
        # _current_active_date = datetime.now()
        # check_all_users_active()
        if user.security_questions_answers == None:
            data['has_security_questions'] = False
        else:
            data['has_security_questions'] = True
    else: 
        print("SERIALIZER ERRORS")
        data = serializer.errors
    if de_queue:
        user.in_queue = False
        user.in_game = False
        user.save()
    print("Get User Data Is Below")
    print(data)
    print("!!!!!!!!!!!!")
    print("!!!!!!!!!!!!")
    print("!!!!!!!!!!!!")
    return Response(data)

@api_view(['POST'])
def logout_view(request):
    session = request.data['token']
    print("THE TOKEN IS BELOW")
    print(session)
    data = {}

    token1 = None
    try:
        for token in Token.objects.all():
            if token.token == session:
                token1 = token
        data['response'] = "Success"
    except:
        data['response'] = "Failure"
        return Response(data)
    user = User.objects.get(token=token1)
    if user.is_guest:
        token1.delete()
        user.delete()
    else:
        user.logged_in = False
        user.in_queue = False
        user.in_game = False
        user.is_active = False
        token1.token = "null"
        token.save()
        user.save()
    return Response(data)

@api_view(['POST'])
def guest_login(request):
    data = {}
    token = binascii.hexlify(os.urandom(config('TOKEN', cast=int))).decode()
    pw = "guestPassword"
    salt = bcrypt.gensalt(rounds=config('ROUNDS', cast=int))
    hashed = bcrypt.hashpw(pw.encode(config('ENCODE')), salt).decode()
    token1 = Token.objects.create(token=token)
    count = 0
    for user in User.objects.all():
        try:
            if user.username.split("_")[0] == "CoinTapper":
                count += 1
        except:
            count = count

    newCount = str(count)
    user = None
    try:
        user = User.objects.create(first_name="Guest",last_name="Tapper", username="CoinTapper_" + newCount, token=token1, password=hashed)
        user.is_guest = True
        user.in_game = False
        user.in_queue = False
        user.logged_in = True
        user.save()
        data['response'] = "succesfully registered a new guest user."
        data['username'] = user.username
        data['error'] = False
        data['token'] = token1.token
        # ping(True, token1.token)
        u = User.objects.get(token=token1)
        u.is_active = True
        u.last_active_date = datetime.now()
        u.save()
    except Exception as e:
        newError = str(e)
        newErr = newError.split("DETAIL:")[1]
        error = newErr.split("=")[1]
        data['response'] = "Something went wrong."
        data['username'] = error
        data['error'] = True
        data['token'] = ""
        return Response(data)

    return Response(data)

# Look into these below functions for implementing ping
@api_view(['POST'])
def send_username(request):
    phone_number = request.data['phone_number']
    data = {
        "response": True,
        "message" : ""
    }

    try:
        user = User.objects.get(phone_number=phone_number)
        data['message'] = "BEFORE SEND TEXT"
        requests.post('https://textbelt.com/text', {
            'phone': phone_number,
            'message': f'Your username is: {user.username}',
            'key': '0d40a9c1f04d558428eb525db9b4502e0a15cd31F5JAs5vP0Yc2JcS2TzrtsqFKd',
        })
        data['message'] = "RESPONSE IS A SUCCESS"
        # ping(True, user.token.token)
    except Exception as e:
        data['response'] = False
        data['message'] = f"IN THE EXCEPT BLOCK e: {e}"
    
    return Response(data)

@api_view(['POST'])
def send_code(request):
    phone_number = request.data['phone_number']
    code = ""

    for i in range(4):
        num = randrange(10)
        code += str(num)
    data = {
        "response": True,
        "code" : code
    }

    try:
        print("IN THE TRY")
        user = User.objects.get(phone_number=phone_number)
        print("GOT THE USER BY PHONE NUMBER")
        print(user.phone_number)
        data['message'] = "BEFORE SEND TEXT"
        requests.post('https://textbelt.com/text', {
            'phone': phone_number,
            'message': f'Your temporary code is: {code}',
            'key': '951292afc50e335e0bc2ac92e70e3ecd4030853aQFJFjuPmMccnZjNCihpssKcII',
        })
        print("AFTER SENDING REQUEST")
        right_now = make_aware(datetime.now())
        print("AFTER RIGHT NOW")
        user.p_code = int(code)
        print("AFTER USER P CODE")
        user.p_code_time = right_now
        print("AFTER USER P CODE TIME")
        user.save()
        print("AFTER USER SAVE")
        data['message'] = f"RESPONSE IS A SUCCESS {right_now}."
    except Exception as e:
        print("IN EXCEPTION")
        print(e)
        data['response'] = False
        data['message'] = f"IN THE EXCEPT BLOCK e: {e}"
    
    return Response(data)

@api_view(['POST'])
def change_password(request):
    if request.data['code'] == "SAVE":
        print("IN SAVED IF STATMENT")
        data = {
            "response": True,
            "message": "",
            "error_type": 0
        }
        try:
            print("IN THE TRY BLOCK")
            password = request.data['password']
            if password.strip() == "":
                data["response"] = False
                data["error_type"] = 0
                data["message"] = "Password can't be blank."
                return Response(data)
            print("AFTER CHECKING FOR EMPTY")
            token = Token.objects.get(token=request.data['token'])
            user = User.objects.get(token=token)
            print("GOT USER")
            newPW = bcrypt.hashpw(password.encode(config('ENCODE')), user.password.encode(config('ENCODE')))
            print("GOT NEW PW")
            if newPW == user.password.encode(config('ENCODE')):
                print("PASSWORD IS PREVIOUS PASSWORD")
                data["response"] = False
                data["error_type"] = 1
                data["message"] = "Password can't be previous password."
                print(data)
                return Response(data)
            print("PASSWORDS ARE DIFFERENT")
            salt = bcrypt.gensalt(rounds=config('ROUNDS', cast=int))
            print("GOT THE SALT")
            hashed = bcrypt.hashpw(password.encode(config('ENCODE')), salt).decode()
            print("GOT THE HASHED")
            user.password = hashed
            print("SET USER PASSWORD")
            user.is_guest = False
            print("SET THE GUEST")
            user.save()
        except:
            print("IN EXCEPT BLOCK")
            data["response"] = False
            data["error_type"] = 3
            data["message"] = "Something went wrong."
        return Response(data)
    elif request.data['code'] == "Change_Password":
        print("IN Change_Password IF STATMENT")
        data = {
            "response": True,
            "message": "",
            "error_type": 0,
            "expired": False
        }
        try:
            print("IN THE TRY BLOCK")
            password = request.data['password']
            if password.strip() == "":
                data["response"] = False
                data["error_type"] = 0
                data["message"] = "Password can't be blank."
                return Response(data)
            print("AFTER CHECKING FOR EMPTY")
            user = User.objects.get(username=request.data['username'])
            print("GOT USER")
            newPW = bcrypt.hashpw(password.encode(config('ENCODE')), user.password.encode(config('ENCODE')))
            print("GOT NEW PW")
            if newPW == user.password.encode(config('ENCODE')):
                print("PASSWORD IS PREVIOUS PASSWORD")
                data["response"] = False
                data["error_type"] = 1
                data["message"] = "Password can't be previous password."
                print(data)
                return Response(data)
            print("PASSWORDS ARE DIFFERENT")
            salt = bcrypt.gensalt(rounds=config('ROUNDS', cast=int))
            print("GOT THE SALT")
            hashed = bcrypt.hashpw(password.encode(config('ENCODE')), salt).decode()
            print("GOT THE HASHED")
            user.password = hashed
            print("SET USER PASSWORD")
            user.is_guest = False
            print("SET THE GUEST")
            user.save()
            data["response"] = True
            data["error_type"] = 0
            data["message"] = "Success"
            data['expired'] = False
        except:
            print("IN EXCEPT BLOCK")
            data["response"] = False
            data["error_type"] = 3
            data["message"] = "Something went wrong."
        print("DATA IS BELOW")
        print(data)
        return Response(data)
    data = {
        "response": True,
        "expired": False,
        "message": "",
        "error_type": 0
    }
    code = request.data['code']
    password = request.data['password']
    if password.strip() == "":
        data["response"] = False
        data["error_type"] = 0
        data["message"] = "Password can't be blank."
        data["expired"] = False
        return Response(data)
    user = User.objects.get(p_code=int(code))
    ser_data = {
        "username": user.username,
        "password": password
    }
    newPW = bcrypt.hashpw(password.encode(config('ENCODE')), user.password.encode(config('ENCODE')))
    if newPW == user.password.encode(config('ENCODE')):
        data["response"] = False
        data["error_type"] = 1
        data["message"] = "Password can't be previous password."
        data["expired"] = False
        return Response(data)
    p_word_datetime_limit = user.p_code_time + timedelta(minutes=5)
    right_now = make_aware(datetime.datetime.now())
    try:
        if p_word_datetime_limit > right_now:
            salt = bcrypt.gensalt(rounds=config('ROUNDS', cast=int))
            hashed = bcrypt.hashpw(password.encode(config('ENCODE')), salt).decode()
            user.password = hashed
            user.save()
            data['message'] = f"Successfully saved password."
        else:
            data["response"] = False
            data['message'] = "Time limit reached. Invalid code."
            data["error_type"] = 2
            data['expired'] = True
    except:
        data['response'] = False
        data["error_type"] = 3
        data['message'] = "Something went wrong."
        data['expired'] = False

    return Response(data)

# Look into these above functions for implementing ping      
@api_view(['POST'])
def save(request):
    print("IN SAVE")
    data = {
        "response" : ""
    }
    try:
        print("IN TRY BLOCK")
        # print(request.data['answer_2'])
        # print(request.data['edit_qnas'])
        token = Token.objects.get(token=request.data['token'])
        print("CREATED TOKEN")
        user = User.objects.get(token=token)
        print("FOUND USER")
        if request.data['changed_username'] == True:
            for u in User.objects.all():
                if u.username == request.data['username']:
                    if u != user:
                        print("INVALID USERNAME")
                        data['response'] = "Invalid username."
                        return Response(data)
        print("SAVING DATA")
        user.first_name = request.data['first_name']
        print("SAVED FIRST NAME")
        user.last_name = request.data['last_name']
        print("SAVED LAST NAME")
        if request.data['changed_username'] == True:
            user.username = request.data['username']
            print("SAVED USERNAME")
        user.phone_number = request.data['phone_number']
        print("SAVED PHONE NUMBER")
        user.save()
        print("SAVED")
        if request.data['guest']:
            print("IS A GUEST")
            data['response'] = "Guest"
        else:
            print("IS NOT A GUEST")
            data['response'] = "Successfully saved data."
        # ping(True, token.token)
        u = User.objects.get(token=token)
        u.is_active = True
        u.last_active_date = datetime.now()
        u.save()
    except Exception as e:
        print("E IS BELOW")
        print(e)
        data['response'] = "Something went wrong: " + e

    return Response(data)

@api_view(['POST'])
def save_location(request):
    try:
        print("IN THE TRY BLOCK")
        print(request.data['latitude'])
        print(request.data['longitude'])
        print(request.data['timezone'])
        token = Token.objects.get(token=request.data['token'])
        print("GOT THE TOKEN")
        user = User.objects.get(token=token)
        print("GOT THE USER")
        user.user_latitude = request.data['latitude']
        print("GOT LATITUDE")
        user.user_longitude = request.data['longitude']
        print("SET THE COORDINATES")
        user.user_time_zone = request.data['timezone']
        print("SET THE TIME ZONE")
        user.has_location = True
        print("USER LOCATION IS TRUE")
        user.save()
        print("SAVED USER")
        data = {
            "result" : "SUCCESS"
        }
        print("RETURNING SUCCESS")
        # ping(True, token.token)
        u = User.objects.get(token=token)
        u.is_active = True
        u.last_active_date = datetime.now()
        u.save()
        return Response(data)
    except:
        print("SOMETHING WENT WRONG")
        data = {
            "result" : "Something went wrong."
        }
        return Response(data)

@api_view(['POST']) 
def confirm_password(request):
    password = request.data['password']
    request_token = request.data['token']
    token = Token.objects.get(token=request_token)
    request_user = User.objects.get(token=token)
    serializer_data = {
        "username": request_user.username,
        "password": password
    }
    serializer = TestPasswordSerializer(data=serializer_data)

    data = {}
    if serializer.is_valid():
        user = serializer.save()
        if type(user) == dict:
            data['result'] = False
            return Response(data)
        data['result'] = True
    else:
        data['result'] = False
    # ping(True, token.token)
    u = User.objects.get(token=token)
    u.is_active = True
    u.last_active_date = datetime.now()
    u.save()
    return Response(data)

def sort_leaderboard(e):
    print("E IS BELOW")
    print(e)
    return e['win_percentage']

# Send token for this function for ping
@api_view(['GET']) 
def get_leaderboard_data(request):
    print("IN GET LEADERBOARD DATA")
    try:
        print("IN THE TRY")
        all_users = User.objects.all()
        print("GOT ALL USERS")
        all_users_adjusted = []
        for user in all_users:
            print("GETTING USER BELOW")
            print(user.username)
            total_games = user.wins + user.losses
            print("GOT TOTAL GAMES BELOW")
            print(total_games)
            if total_games > 0:
                win_percentage = user.wins / total_games
                win_percentage = win_percentage * 100
            else:
                win_percentage = 0
            print("GOT WIN PERCENTAGE")
            print(round(win_percentage))
            user_obj = {
                "username": user.username[:4],
                "wins": user.wins,
                "losses": user.losses,
                "win_percentage" : round(win_percentage),
                "total_games": total_games,
                "league": user.league
            }
            print("CREATED USER OBJ")
            print(user_obj)
            all_users_adjusted.append(user_obj)
            print("APPENDED USER TO LIST")
        print("GOT ALL USERS ADJUSTED LIST")
        print(all_users_adjusted)
        all_users_adjusted.sort(key=sort_leaderboard, reverse=True)
        print("GOT ALL USERS ADJUSTED LIST AGAIN")
        print(all_users_adjusted)
        data = {
            "result": "Success",
            "all_users":all_users_adjusted
        }
        # ping(True, token.token)
        return Response(data)
    except Exception as e:
        print("SOMETHING WENT WRONG")
        print(e)
        data = {
            "result": "Something went wrong.",
            "all_users": []
        }
        return Response(data)

@api_view(['POST']) 
def testing_cloud(request):
    test_var = request.data['test']
    print(f"TEST VAR HERE: {test_var}")
    data = {
        "response": "SUCCESS"
    }
    return Response(data)

@api_view(['POST'])
def test_celery(request):
    token = Token.objects.get(token=request.data['token'])
    user = User.objects.get(token=token)
    user.is_active_task_value = not user.is_active_task_value
    user.lost_streak = False
    user.save()
    task_data = {
        "token": request.data['token'], 
        "value": user.is_active_task_value
    }
    start_time_limit_for_users_streaks.delay(task_data)
    return HttpResponse("Done")

def league_placement(wins, games):
    print("IN LEAGUE PLACEMENT FUNCTION")
    percentage = (wins / games) * 100
    print("THE PERCENTAGE IS: ", percentage)
    str_percentage = str(percentage)
    print("STRING PERCENTAGE IS: ", str_percentage)
    if "." in str_percentage:
        print("HAS DECIMAL")
        new_percentage = str_percentage.split(".")[0]
        print("NEW_PERCENTAGE: ", new_percentage)
        percentage = int(new_percentage)
        print("NEW PERCENTAGE CONVERTED TO INT: ", percentage)
    if percentage <= 35:
        print("IS A NOOB PLAYER")
        return LeagueEnum.NOOB_TAPPER.value
    elif percentage <= 43:
        print("IS A BAD PLAYER")
        return LeagueEnum.BAD_TAPPER.value
    elif percentage <= 51:
        print("IS AN OKAY PLAYER")
        return LeagueEnum.OKAY_TAPPER.value
    elif percentage <= 59:
        print("IS A BETTER PLAYER")
        return LeagueEnum.BETTER_TAPPER.value
    elif percentage <= 67:
        print("IS A GOOD PLAYER")
        return LeagueEnum.GOOD_TAPPER.value
    elif percentage <= 75:
        print("IS A SOLID PLAYER")
        return LeagueEnum.SOLID_TAPPER.value
    elif percentage <= 83:
        print("IS A SUPER PLAYER")
        return LeagueEnum.SUPER_TAPPER.value
    elif percentage <= 91:
        print("IS A MEGA PLAYER")
        return LeagueEnum.MEGA_TAPPER.value
    elif percentage > 91:
        print("IS A GODLY PLAYER")
        return LeagueEnum.GODLY_TAPPER.value
    else:
        print("IS A NOOB PLAYER IN THE LESE STATEMENT")
        return LeagueEnum.NOOB_TAPPER.value

def ping(active, _token):
    token = Token.objects.get(token=_token)
    user = User.objects.get(token=token)
    user.last_active_date = datetime.now()
    user.is_active = True
    user.save()
    print(f"Username: {user.username}, is_active: {user.is_active}")
    return "Active"
# def check_all_users_active():
#     all_users = User.objects.all()
#     print("IN CHECK FOR ALL ACTIVE USERS")
#     if _current_active_date != None:
#         print("CURRENT ACTIVE DATE DOES NOT EQUAL NONE")
#         COMP_TIME = _current_active_date - timedelta(minutes=3)
#         for user in all_users:
#             if user.is_active:
#                 if user.last_active_date < COMP_TIME:
#                     user.is_active = False
#                     user.save()
#                 else:
#                     print("USERS TIME IS FINE")
#             else:
#                 print("USER IS NOT ACTIVE")
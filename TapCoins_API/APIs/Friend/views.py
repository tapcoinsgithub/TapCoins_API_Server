from rest_framework.response import Response
from rest_framework.decorators import api_view
from ...models import *
import binascii
import os
from ...Utilities.helpful_functions import ping
from datetime import datetime

@api_view(['POST'])
def send_friendRequest(request):
    try:
        print("IN SEND FRIEND REQUEST")
        print("1")
        token1 = Token.objects.get(token=request.data['token'])
        print("2")
        user1 = User.objects.get(token=token1)
        print("3")
        user2 = User.objects.get(username=request.data['username'])
        print("4")
        if user1 == user2:
            print("5")
            data = {
                "result": "Cannot send request to self.",
                "friends": "No friends"
            }
            return Response(data)
        # Check if FriendModel already created with both usernames
        users_usernames_type1 = user1.username + user2.username
        users_usernames_type2 = user2.username + user1.username
        print("6")
        try:
            print("7")
            FriendModel.objects.get(users_names_string=users_usernames_type1)
            data = {
                    "result": "Already created a friend request with: ",
                    "friends": user2.username
                }
            return Response(data)
        except:
            print("8")
            try:
                print("9")
                FriendModel.objects.get(users_names_string=users_usernames_type2)
                data = {
                    "result": "Already created a friend request with: ",
                    "friends": user2.username
                }
                return Response(data)
            except:
                print("10")
                pass
        print("11")
        # Create FriendModel with both user names | make pending_request True
        new_friend_model = FriendModel.objects.create(sending_user=user1.username, receiving_user=user2.username, pending_request=True, users_names_string=users_usernames_type1)
        print("12")
        # Capture FriendModel Id
        new_friend_model_id = new_friend_model.id
        print("13")
        # Save FriendModel Id in both users friends list
        if user1.friends:
            print("14")
            user1.friends.append(new_friend_model_id)
        else:
            print("15")
            user1_friends = [new_friend_model_id] 
            user1.friends = user1_friends
        if user2.friends:
            print("16")
            user2.friends.append(new_friend_model_id)
        else:
            print("17")
            user2_friends = [new_friend_model_id] 
            user2.friends = user2_friends
        print("18")
        user1.save()
        user2.save()
        print("19")
        data = {
            "result": "Success",
            "friends": user2.username
        }
        # ping(True, token1.token)
        u = User.objects.get(token=token1)
        u.is_active = True
        u.last_active_date = datetime.now()
        u.save()
        return Response(data)
    except Exception as e:
        print("20")
        print(e)
        data = {
            "result": "Could not find username.",
            "friends": "No friends"
        }
        return Response(data)

@api_view(['POST'])
def accept_friendRequest(request):
    try:
        print("1")
        token1 = Token.objects.get(token=request.data['token'])
        print("2")
        accepter = User.objects.get(token=token1)
        print("3")
        sender = User.objects.get(username=request.data['username'])
        print("4")
        # Get friend model based on usernames
        users_usernames = sender.username + accepter.username
        print("5")
        friend_model = FriendModel.objects.get(users_names_string=users_usernames)
        print("6")
        # Adjust pending_request attribute to False
        friend_model.pending_request = False
        print("7")
        # Save Friend Model
        friend_model.save()
        print("8")
        data = {
            "result": "Accepted"
        }
        # ping(True, token1.token)
        u = User.objects.get(token=token1)
        print("9")
        u.is_active = True
        print("10")
        u.last_active_date = datetime.now()
        print("11")
        u.save()
        return Response(data)
    except:
        print("IN THE EXCEPT")
        data = {
            "result": "Colud not accept request"
        }
        return Response(data)

@api_view(['POST'])
def decline_friendRequest(request):
    try:
        token1 = Token.objects.get(token=request.data['token'])
        decliner = User.objects.get(token=token1)
        sender = User.objects.get(username=request.data['username'])
        users_usernames = sender.username + decliner.username
        friend_model = FriendModel.objects.get(users_names_string=users_usernames)
        sender.friends.pop(sender.friends.index(friend_model.id))
        decliner.friends.pop(decliner.friends.index(friend_model.id))
        friend_model.delete()
        sender.save()
        decliner.save()
        data = {
            "result": "Declined"
        }
        # ping(True, token1.token)
        u = User.objects.get(token=token1)
        u.is_active = True
        u.last_active_date = datetime.now()
        u.save()
        return Response(data)
    except:
        data = {
            "result": "Colud not decline request."
        }
        return Response(data)

@api_view(['POST'])
def remove_friend(request):
    try:
        print("IN REMOVE FRIEND FUNCTION CALL")
        token1 = Token.objects.get(token=request.data['token'])
        print("GOT TOKEN")
        remover = User.objects.get(token=token1)
        print("GOT REMOVER")
        removed = User.objects.get(username=request.data['username'])
        print("GOT REMOVED")
        users_usernames_type1 = remover.username + removed.username
        users_usernames_type2 = removed.username + remover.username
        friend_model = None
        print(users_usernames_type1)
        print(users_usernames_type2)
        try:
            friend_model = FriendModel.objects.get(users_names_string=users_usernames_type1)
        except:
            try:
                friend_model = FriendModel.objects.get(users_names_string=users_usernames_type2)
            except:
                print("IN FIRST ECEPT BLOCK")
                data = {
                    "result": "Could not remove friend."
                }
                return Response(data)
        print("AFTER FIRST TRY AND EXCEPT")
        remover.friends.pop(remover.friends.index(friend_model.id))
        print("REMOVER FREIND REMOVED")
        removed.friends.pop(removed.friends.index(friend_model.id))
        print("REMOVED FRIEND REMOVED")
        friend_model.delete()
        print("FRIEND MODEL DELETED")
        remover.save()
        removed.save()
        print("BOTH SAVED")
        data = {
            "result": "Removed"
        }
        # ping(True, token1.token)
        u = User.objects.get(token=token1)
        u.is_active = True
        u.last_active_date = datetime.now()
        u.save()
        return Response(data)
    except:
        print("IN SECOND EXCEPT BLOCK")
        data = {
            "result": "Could not remove friend."
        }
        return Response(data)

@api_view(['POST'])
def send_invite(request):
    print("IN SEND INVITE")
    token = Token.objects.get(token=request.data['token'])
    user1 = User.objects.get(token=token)
    user2 = User.objects.get(username=request.data['username'])
    gameId = binascii.hexlify(os.urandom(8)).decode()
    uniqueId = False
    while(not uniqueId):
        foundId = False
        for game in Game.objects.all():
            if game.gameId == gameId:
                foundId = True
                break
        if foundId:
            gameId = binascii.hexlify(os.urandom(8)).decode()
        else:
            uniqueId = True
    for gInvite in GameInvite.objects.all():
        if gInvite.sender == user1.username:
            if gInvite.reciever == user2.username:
                data = {
                    "first": "ALREADY EXISTS",
                    "second": "ALREADY EXISTS",
                    "gameId": "ALREADY EXISTS"
                }
                # ping(True, token.token)
                u = User.objects.get(token=token)
                u.is_active = True
                u.last_active_date = datetime.now()
                u.save()
                return Response(data)
        elif gInvite.sender == user2.username:
            if gInvite.reciever == user1.username:
                data = {
                    "first": "ALREADY EXISTS",
                    "second": "ALREADY EXISTS",
                    "gameId": "ALREADY EXISTS"
                }
                # ping(True, token.token)
                u = User.objects.get(token=token)
                u.is_active = True
                u.last_active_date = datetime.now()
                u.save()
                return Response(data)
    gameInvite = GameInvite.objects.create(sender=user1.username, reciever=user2.username, gameId=gameId)
    print("GAME INVITE OBJECT IS BELOW")
    print(gameInvite)
    game = Game.objects.create(first=user1.username, second=user2.username, gameId=gameId)
    print("GAME OBJECT IS BELOW")
    print(game)
    user1.cg_Id = gameId
    user2.cg_Id = gameId
    user2.has_game_invite = True
    user1.save()
    user2.save()
    data = {
        "first":user1.username,
        "second":user2.username,
        "gameId":gameId
    }
    print("DATA IS BELOW")
    print(data)
    # ping(True, token.token)
    u = User.objects.get(token=token)
    u.is_active = True
    u.last_active_date = datetime.now()
    u.save()
    return Response(data)

@api_view(['POST'])
def ad_invite(request):
    print("IN AD INVITE")
    print(request.data)
    sender = User.objects.get(username=request.data['username'])
    print("GOT SENDER")
    token = Token.objects.get(token=request.data['token'])
    print("GOT TOKEN")
    reciever = User.objects.get(token=token)
    print("GOT RECEIVER")
    ad_request = request.data['adRequest']
    try:
        print("IN THE TRY")
        print(ad_request)
        if ad_request == "delete":
            print("IT IS DELETE")
            deleted = False
            try:
                if request.data['cancelled'] == True:
                    print("CANCELLED IS TRUE")
                    data = {
                        "result": "Cancelled",
                        "gameId": sender.cg_Id
                    }
                    # ping(True, token.token)
                    u = User.objects.get(token=token)
                    u.is_active = True
                    u.last_active_date = datetime.now()
                    u.save()
                    return Response(data)
                else:
                    print("CANCELLED IS NOT TRUE")
                    for invite in GameInvite.objects.all():
                        if invite.sender == sender.username:
                            if invite.reciever == reciever.username:
                                game = Game.objects.get(gameId=invite.gameId)
                                game.delete()
                                invite.delete()
                                deleted = True
                        elif invite.sender == reciever.username:
                            if invite.reciever == sender.username:
                                game = Game.objects.get(gameId=invite.gameId)
                                game.delete()
                                invite.delete()
                                deleted = True
                    if deleted:
                        print("DELETED IS TRUE")
                        data = {
                            "result": "Cancelled",
                            "gameId": sender.cg_Id
                        }
                    else:
                        print("DELETED IS NOT TRUE")
                        data = {
                            "result": "Something went wrong",
                            "gameId": "None"
                        }
                    # ping(True, token.token)
                    u = User.objects.get(token=token)
                    u.is_active = True
                    u.last_active_date = datetime.now()
                    u.save()
                    print("RETURNING RESPONSE")
                    return Response(data)
            except:
                print("IN THE EXCEPT BLOCK")
                for invite in GameInvite.objects.all():
                    if invite.sender == sender.username:
                        if invite.reciever == reciever.username:
                            game = Game.objects.get(gameId=invite.gameId)
                            game.delete()
                            invite.delete()
                            deleted = True
                    elif invite.sender == reciever.username:
                        if invite.reciever == sender.username:
                            game = Game.objects.get(gameId=invite.gameId)
                            game.delete()
                            invite.delete()
                            deleted = True
                if deleted:
                    print("DELETED IS TRUE")
                    data = {
                        "result": "Cancelled",
                        "gameId": sender.cg_Id
                    }
                    # ping(True, token.token)
                    u = User.objects.get(token=token)
                    u.is_active = True
                    u.last_active_date = datetime.now()
                    u.save()
                else:
                    print("DELETED IS FALSE")
                    data = {
                        "result": "Soemthing went wrong",
                        "gameId": "None"
                    }
                return Response(data)
        else:
            print("IT IS GAME INVITE")
            game = None
            for invite in GameInvite.objects.all():
                if invite.sender == sender.username:
                    print("SENDERS ARE EQUAL")
                    print(invite.sender)
                    print(invite.reciever)
                    print(sender.username)
                    print(reciever.username)
                    if invite.reciever == reciever.username:
                        print("RECEIVERS ARE EQUAL TOO")
                        game = Game.objects.get(gameId=invite.gameId)
                        invite.delete()
                        deleted = True
                elif invite.sender == reciever.username:
                    print("RECEIVERS ARE EQUAL")
                    if invite.reciever == sender.username:
                        print("SENDERS ARE EQUAL TOO")
                        game = Game.objects.get(gameId=invite.gameId)
                        invite.delete()
                        deleted = True
            if deleted:
                print("IN DELETED")
                data = {
                    "result": "Accepted",
                    "first":game.first,
                    "second":game.second,
                    "gameId":game.gameId
                }
                # ping(True, token.token)
                u = User.objects.get(token=token)
                u.is_active = True
                u.last_active_date = datetime.now()
                u.save()
                print("IT DELETED")
            else:
                print("IN ELSE DELETED")
                data = {
                    "result": "Soemthing went wrong",
                    "first":"None",
                    "second":"None",
                    "gameId":"None"
                }
            return Response(data)
    except:
        print("IN EXCEPT BLOCK")
        data = {
            "result": "Somethiong went wrong"
        }
        return Response(data)
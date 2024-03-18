from rest_framework import serializers
from ...models import User, Token
import binascii
import os
import bcrypt
from decouple import config

def check_pw_complexity(pw:str):
        symbols_arr = ["!","@", "#", "$", "%", "^", "&", "*", "(", ")", "?"]
        if len(pw) < 8:
            return "Password must be at least 8 charcters long."
        has_int = False
        has_symbol = False
        has_lower = False
        has_upper = False
        for char in pw:
            try:
                if has_int is False:
                    int(char)
                    has_int = True
                elif char in symbols_arr:
                    has_symbol = True
                elif char == char.lower():
                    has_lower = True
                elif char == char.upper():
                    has_upper = True
            except:
                if char in symbols_arr:
                    has_symbol = True
                elif char == char.lower():
                    has_lower = True
                elif char == char.upper():
                    has_upper = True
        if has_int is False:
            return "Password must contain at least one integer."
        if has_symbol is False:
            seperator = ","
            return "Password must contain at least one symbol.[ " + seperator.join(symbols_arr) + " ]"
        if has_lower is False:
            return "Password must contain at least one lower case character."
        if has_upper is False:
            return "Password must contain at least one upper case character."
        return "Complexity Passed."


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=config('CHAR', cast=int))
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
 
    def create(self, validated_data):
        try:
            uName = validated_data.pop("username")
            print("VALIDATED DATA USERNAME")
            print(uName)
            if len(uName) <=1 or uName is None:
                return "Username must be greater than two characters long."
            for char in uName:
                if char == " ":
                    return "Username cannot have any spaces."
            token = binascii.hexlify(os.urandom(config('TOKEN', cast=int))).decode()
            pw = validated_data.pop("password")
            result = check_pw_complexity(pw)
            if result != "Complexity Passed.":
                return result
            print("PASSWORD COMPLEXITY PASSED")
            salt = bcrypt.gensalt(rounds=config('ROUNDS', cast=int))
            hashed = bcrypt.hashpw(pw.encode(config('ENCODE')), salt).decode()
            token1 = Token.objects.create(token=token)
            try:
                user = User.objects.create(**validated_data, token=token1, password=hashed, username=uName)
                print("CREATED USER BELOW")
                print(user)
            except Exception as e:
                print("IS AN ERROR IN SERIALIZER")
                newError = str(e)
                newErr = newError.split("DETAIL:")[1]
                error = newErr.split("=")[1]
                return error
            print("RETURNING THE USER NOW")
            return user
        except:
            return "Something went wrong."


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=config('CHAR', cast=int))
    password = serializers.CharField(max_length=config('CHAR', cast=int))

    def create(self, validated_data):
        user1 = None
        foundUser = False
        foundPassword = False
        try:
            for user in User.objects.all():
                if user.username == validated_data['username']: 
                    foundUser = True
                    newPW = bcrypt.hashpw(validated_data['password'].encode(config('ENCODE')), user.password.encode(config('ENCODE')))
                    if newPW == user.password.encode(config('ENCODE')):
                        foundPassword = True
                        user1 = user
            if foundUser == False:
                if foundPassword == False:
                    user1 = {
                        "error": True,
                        "user": "Could not find username.",
                        "password": "Incorrect Password."
                        }
            else:
                if foundPassword == False:
                    user1 = {
                        "error": True,
                        "user": "None",
                        "password": "Incorrect Password"
                    }
                
        except Exception as e:
            return False

        return user1

class GetUserSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=config('TK', cast=int))

    def create(self, validated_data):
        token1 = None
        user = None
        try:
            for token in Token.objects.all():
                if token.token == validated_data['token']:
                    token1 = token
            for user in User.objects.all():
                if user.token.token == token1.token:
                    user = user
                    break
        except:
            return False

        return user

class TestPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=config('CHAR', cast=int))
    password = serializers.CharField(max_length=config('CHAR', cast=int))

    def create(self, validated_data):
        user1 = None
        foundUser = False
        foundPassword = False
        try:
            for user in User.objects.all():
                if user.username == validated_data['username']: 
                    foundUser = True
                    newPW = bcrypt.hashpw(validated_data['password'].encode(config('ENCODE')), user.password.encode(config('ENCODE')))
                    if newPW == user.password.encode(config('ENCODE')):
                        foundPassword = True
                        user1 = user
            if foundUser == False:
                if foundPassword == False:
                    user1 = {
                        "error": True,
                        "user": "Could not find username.",
                        "password": "Incorrect Password."
                        }
            else:
                if foundPassword == False:
                    user1 = {
                        "error": True,
                        "user": "None",
                        "password": "Incorrect Password"
                    }
                
        except Exception as e:
            return False

        return user1

class LogoutSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=config('TK', cast=int))

    def create(self, validated_data):
        token1 = None
        user = None
        try:
            for token in Token.objects.all():
                if token.token == validated_data['token']:

                    token1 = token
            for user in User.objects.all():
                if user.token == token1.id:
                    user = user
        except:
            return False
        token1.token = "null"
        token1.save()
        return user
from django.db import models
from django.contrib.postgres.fields import ArrayField
from decouple import config
from enum import Enum

class LeagueEnum(Enum):
    NOOB_TAPPER = 1
    BAD_TAPPER = 2
    OKAY_TAPPER = 3
    BETTER_TAPPER = 4
    GOOD_TAPPER = 5
    SOLID_TAPPER = 6
    SUPER_TAPPER = 7
    MEGA_TAPPER = 8
    GODLY_TAPPER = 9

class Token(models.Model): 
    token = models.CharField(max_length=config('TK', cast=int), null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UsersSecurityQuestionsAnswers(models.Model):
    question_1 = models.CharField(verbose_name="question one", max_length=config('DOUBLE_CHAR', cast=int), null=True)
    answer_1 = models.CharField(verbose_name="answer one", max_length=config('DOUBLE_CHAR', cast=int), null=True)
    question_2 = models.CharField(verbose_name="question two", max_length=config('DOUBLE_CHAR', cast=int), null=True)
    answer_2 = models.CharField(verbose_name="answer two", max_length=config('DOUBLE_CHAR', cast=int), null=True)

class League(models.Model):
    league_title = models.CharField(verbose_name="league title", max_length=config('CHAR', cast=int), null=True)
    created_at = models.DateTimeField(verbose_name="created at", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="updated at", auto_now=True)

class User(models.Model):
    first_name = models.CharField(verbose_name="first name", max_length=config('CHAR', cast=int), null=True)
    last_name = models.CharField(verbose_name="last name", max_length=config('CHAR', cast=int), null=True)
    username = models.CharField(max_length=config('CHAR', cast=int), unique=True, null=True)
    phone_number = models.CharField(max_length=16, null=True)
    password = models.CharField(max_length=config('CHAR', cast=int), unique=True, null=True)
    cg_Id = models.CharField(verbose_name="current game id", max_length=config('GID', cast=int), null=True)
    token = models.OneToOneField(Token, on_delete=models.CASCADE, primary_key=True, null=False)
    friends = ArrayField(ArrayField(models.IntegerField(default=0), null=True, blank=True), null=True, blank=True, default=list)
    win_streak = models.IntegerField(verbose_name="win streak", null=True, default=0)
    best_streak = models.IntegerField(verbose_name="best streak", null=True, default=0)
    has_streak = models.BooleanField(verbose_name="has streak", default=False)
    lost_streak = models.BooleanField(verbose_name="lost streak", default=False)
    wins = models.IntegerField(verbose_name="wins", null=True, default=0)
    losses = models.IntegerField(verbose_name="losses", null=True, default=0)
    games = models.IntegerField(verbose_name="number of games", null=True, default=0)
    league = models.IntegerField(verbose_name="league placement", choices=[(tag, tag.value) for tag in LeagueEnum], default=LeagueEnum.NOOB_TAPPER.value, null=True)
    p_code = models.IntegerField(null=True)
    in_game = models.BooleanField(verbose_name="in game", default=False)
    in_queue = models.BooleanField(verbose_name="in queue", default=False)
    logged_in = models.BooleanField(verbose_name="logged in", default=False)
    in_create_game = models.BooleanField(verbose_name="in create game", default=False)
    is_guest = models.BooleanField(verbose_name="is guest", default=False)
    has_phone_number = models.BooleanField(verbose_name="has a phone number", default=False)
    has_game_invite = models.BooleanField(verbose_name="has a game invite", default=False)
    p_code_time = models.DateTimeField(verbose_name="password code time added", null=True)
    streak_time = models.DateTimeField(verbose_name="win streak time", null=True)
    security_questions_answers = models.OneToOneField(UsersSecurityQuestionsAnswers, on_delete=models.CASCADE, null=True)
    has_wallet = models.BooleanField(verbose_name="has wallet", default=False)
    has_location = models.BooleanField(verbose_name="has location", default=False)
    user_latitude = models.CharField(verbose_name="users latitude", max_length=config('DOUBLE_CHAR', cast=int), null=True)
    user_longitude = models.CharField(verbose_name="users longitude", max_length=config('DOUBLE_CHAR', cast=int), null=True)
    user_time_zone = models.CharField(verbose_name="user time zone", max_length=config('DOUBLE_CHAR', cast=int), null=True)
    is_active = models.BooleanField(verbose_name="is active", default=False, null=True)
    last_active_date = models.DateTimeField(verbose_name="last active date", auto_now=True, null=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)

    def __unicode__(self):
        return self.username

class FriendModel(models.Model):
    sending_user = models.CharField(max_length=config('CHAR', cast=int), null=True)
    receiving_user = models.CharField(max_length=config('CHAR', cast=int), null=True)
    pending_request = models.BooleanField(verbose_name="pending request", default=False)
    users_names_string = models.CharField(verbose_name="both users names", max_length=config('DOUBLE_CHAR', cast=int), unique=True, null=True)
    created_at = models.DateTimeField(verbose_name="created at", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="updated at", auto_now=True)

class Game(models.Model):
    first = models.CharField(verbose_name="first player", max_length=config('CHAR', cast=int), null=True)
    second = models.CharField(verbose_name="second player", max_length=config('CHAR', cast=int), null=True)
    winner = models.CharField(verbose_name="winner", max_length=config('CHAR', cast=int), null=True)
    winner_streak = models.IntegerField(verbose_name="winner streak", null=True)
    fPoints = models.IntegerField(verbose_name="first points", null=True)
    sPoints = models.IntegerField(verbose_name="second points", null=True)
    gameId = models.CharField(verbose_name="game id", max_length=config('GID', cast=int), unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class GameInvite(models.Model):
    sender = models.CharField(verbose_name="sender", max_length=80, null=True)
    reciever = models.CharField(verbose_name="reciever", max_length=80, null=True)
    accepted = models.BooleanField(verbose_name="accepted invite", default=False)
    cancel = models.BooleanField(verbose_name="cancel invite", default=False)
    gameId = models.CharField(verbose_name="game id", max_length=16, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CommentOrBug(models.Model):
    message = models.CharField(verbose_name="CommentOrBug", max_length=150)
    user = models.CharField(verbose_name="username", max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SecurityQuestionsText(models.Model):
    text = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

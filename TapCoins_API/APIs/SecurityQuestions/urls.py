from django.urls import path
from .views import get_security_questions_text, save_users_security_questions, check_has_questions, check_users_answers, get_users_questions_answers


app_name = "securityquestions_api"
urlpatterns = [
    path("get_security_questions_text", get_security_questions_text, name="getSecurityQuestionsText"),
    path("save_users_security_questions", save_users_security_questions, name="saveUsersSecurityQuestions"),
    path("check_has_questions", check_has_questions, name="checkHasQuestions"),
    path("check_users_answers", check_users_answers, name="checkUsersAnswers"),
    path("get_users_questions_answers", get_users_questions_answers, name="getUsersQuestionsAnswers"),
]
# path('sendCB', send_cb, name="sendCommentorBug")
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ...models import *
from ...Utilities.helpful_functions import ping
from datetime import datetime

@api_view(['GET'])   
def get_security_questions_text(request):
    try:
        all_security_questions = SecurityQuestionsText.objects.all()
        count = 0
        options1 = ["Select One"]
        options2 = ["Select One"]
        for q in all_security_questions:
            if count < 4:
                options1.append(q.text)
            else:
                options2.append(q.text)
            count+=1
        data={
            "options_1": options1,
            "options_2": options2
        }
        print("GOT BOTH OPTIONS")
        print(options1)
        print(options2)
        return Response(data)
    except:
        print("SOMETHING WENT WRING")
        data={
            "options_1": "Nothing",
            "options_2": "Nothing"
        }
        return Response(data)

@api_view(['POST'])
def save_users_security_questions(request):
    try:
        print("SAVING USERS SECURITY QUESTIONS")
        print(request.data['question_1'])
        print(request.data['answer_1'])
        print(request.data['question_2'])
        print(request.data['answer_2'])
        new_security_question_object = UsersSecurityQuestionsAnswers.objects.create(
            question_1=request.data['question_1'],
            answer_1=request.data['answer_1'],
            question_2=request.data['question_2'],
            answer_2=request.data['answer_2']
        )

        token = Token.objects.get(token=request.data['token'])
        user = User.objects.get(token=token)

        user.security_questions_answers = new_security_question_object
        user.save()
        data = {
            "result": "Success"
        }
        # ping(True, token.token)
        u = User.objects.get(token=token)
        u.is_active = True
        u.last_active_date = datetime.now()
        u.save()
        return Response(data)
    except:
        data ={
            "result": "Failure"
        }
        return Response(data)

@api_view(['POST'])
def check_has_questions(request):
    try:
        print("IN THE TRY BLOCK")
        user = User.objects.get(username=request.data['username'])
        print("GOT THE USER")
        if user.security_questions_answers == None:
            print("USER HAS NO QUESTIONS")
            data = {
                "result": "User has no questions.",
                "question_1": "None",
                "question_2": "None",
            }
            # ping(True, user.token.token)
            return Response(data)
        else:
            print("USER HAS QUESTIONS")
            print(user.security_questions_answers)
            print("GOT THE USERS QUESTIONS OBJECT BY ID")
            data = {
                "result": "Success",
                "question_1": user.security_questions_answers.question_1,
                "question_2": user.security_questions_answers.question_2,
            }
            return Response(data)
    except:
        print("IN THE EXCEPT BLOCK")
        data = {
            "result": "Something went wrong.",
            "question_1": "None",
            "question_2": "None",
        }
        return Response(data)

@api_view(['POST'])
def check_users_answers(request):
    try:
        user = User.objects.get(username=request.data['username'])
        if user.security_questions_answers.answer_1 == request.data['answer_1']:
            if user.security_questions_answers.answer_2 == request.data['answer_2']:
                print("CORRECT ANSWERS")
                data = {
                    "result": True
                }
                return Response(data)
        print("InCORRECT ANSWERS")
        data = {
            "result": False
        }
        # ping(True, user.token.token)
        u = User.objects.get(token=user.token)
        u.is_active = True
        u.last_active_date = datetime.now()
        u.save()
        return Response(data)
    except:
        print("In Except Block")
        data = {
            "result": False
        }
        return Response(data)

@api_view(['POST'])
def get_users_questions_answers(request):
    print("IN GETTING THE USERS Q AND A FUNCTION")
    print("IN GETTING THE USERS Q AND A FUNCTION")
    print("IN GETTING THE USERS Q AND A FUNCTION")
    print("IN GETTING THE USERS Q AND A FUNCTION")
    try:
        print("IN THE TRY BLOCK")
        token = Token.objects.get(token=request.data['token'])
        user = User.objects.get(token=token)
        print("GOT THE USER")
        if user.security_questions_answers == None:
            print("USER HAS NO QUESTIONS")
            data = {
                "result": "User has no questions.",
                "question_1": "None",
                "question_2": "None",
                "answer_1": "None",
                "answer_2": "None"
            }
            # ping(True, token.token)
            u = User.objects.get(token=token)
            u.is_active = True
            u.last_active_date = datetime.now()
            u.save()
            return Response(data)
        else:
            print("USER HAS QUESTIONS")
            print(user.security_questions_answers)
            print("GOT THE USERS QUESTIONS OBJECT BY ID")
            data = {
                "result": "Success",
                "question_1": user.security_questions_answers.question_1,
                "question_2": user.security_questions_answers.question_2,
                "answer_1": user.security_questions_answers.answer_1,
                "answer_2": user.security_questions_answers.answer_2
            }
            # ping(True, token.token)
            u = User.objects.get(token=token)
            u.is_active = True
            u.last_active_date = datetime.now()
            u.save()
            return Response(data)
    except:
        print("IN THE EXCEPT BLOCK")
        data = {
            "result": "Something went wrong.",
            "question_1": "None",
            "question_2": "None",
            "answer_1": "None",
            "answer_2": "None"
        }
        return Response(data)
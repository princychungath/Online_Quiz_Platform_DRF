from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSignUpSerializer,QuizSerializer,QuizListSerializer,UserSerializer,QuizTakingSerializer,QuizResultSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .models import Quiz,User,UserQuizResponse,Question,Answers
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.db.models import Avg,Max,Min,Count
from .pagination import MyCustomPagination


#-------------------User Registeation ------------------#

class RegisterUser(APIView):
    def post(self, request, format=None):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            refresh = RefreshToken.for_user(customer)
            return Response({"message": "User created."}) 
        else:
            return Response(serializer.errors)



#----------------------User profile-------------------#


class UserProfile(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self, request, *args, **kwargs):

        user_serializer = self.serializer_class(request.user)
        quiz_queryset = Quiz.objects.filter(created_user=request.user)
        quiz_serializer = QuizListSerializer(quiz_queryset, many=True)

        response_data = {
            "username": user_serializer.data['username'],
            "email": user_serializer.data['email'],
            "quizzes_created": quiz_serializer.data
        }

        return Response(response_data)


#----------admin operations (user-create , edit , delete )----------------#

class AdminRegisterUser(APIView):
    permission_classes=[IsAdminUser]
    authentication_classes=[JWTAuthentication]

    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            refresh = RefreshToken.for_user(customer)
            return Response({"message": "User created."}) 
        else:
            return Response(serializer.errors)


class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    pagination_class=MyCustomPagination
    authentication_classes=[JWTAuthentication]



class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    authentication_classes=[JWTAuthentication]




#--------------------QUIZ  Create ---------------------------#

class QuizCreateView(generics.CreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        serializer.save(created_user=self.request.user)

    def post(self, request, *args, **kwargs):
        request.data['created_user'] = request.user.id
        response = super().post(request, *args, **kwargs)
        return Response({"message": "New Quiz created"})




#----------------quiz listing and filtering ----------------#

class QuizListfilter(generics.ListAPIView):
    queryset = Quiz.objects.all()
    pagination_class=MyCustomPagination
    serializer_class = QuizListSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['topic', 'difficulty_level', 'created_at']



#----------------quiz Taking  ----------------#


class QuizTakingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            quiz = Quiz.objects.get(pk=pk)
            serializer = QuizTakingSerializer(quiz)
            return Response(serializer.data)
        except Quiz.DoesNotExist:
            raise ValidationError("Quiz not found.")

    def post(self, request, pk):
        try:
            quiz = Quiz.objects.get(pk=pk)
            questions = quiz.questions.all()
            total_questions = questions.count()
            correct_answers = 0

            for question in questions:
                question_id = question.id
                selected_choice_id = request.data.get(str(question_id), None)
                if selected_choice_id is not None:
                    try:
                        selected_choice = Answers.objects.get(pk=selected_choice_id)
                    except Answers.DoesNotExist:
                        return Response({"error":"Selected answer not found"})

                    if selected_choice.is_correct:
                        correct_answers += 1

            score = (correct_answers / total_questions) * 100
            UserQuizResponse.objects.create(user=request.user, quiz=quiz, score=score)
            return Response({"You are scored ": score})

        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found."})



#----------------------User Quiz RESULTS -------------------#

class QuizResultView(generics.ListAPIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    serializer_class=QuizResultSerializer
    pagination_class=MyCustomPagination

    def get_queryset(self):
        user=self.request.user
        return UserQuizResponse.objects.filter(user=user)


#---------------------- Quiz Analytics -------------------#


class QuizAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):

        total_quizzes = Quiz.objects.count()
        total_quiz_takers = UserQuizResponse.objects.values('user').distinct().count()
        average_quiz_score = UserQuizResponse.objects.aggregate(avg_score=Avg('score'))['avg_score']

        quizzes = Quiz.objects.all()
        avgscores_of_eachquiz= quizzes.annotate(avg_score=Avg('userquizresponse__score')).values('title', 'avg_score')
        highest_score = UserQuizResponse.objects.aggregate(max_score=Max('score'))['max_score']
        lowest_score = UserQuizResponse.objects.aggregate(min_score=Min('score'))['min_score']
        quiz_taken_counts = UserQuizResponse.objects.values('quiz__title').annotate(quiz_count=Count('quiz'))


        question_responses_count = UserQuizResponse.objects.values('quiz__questions__qstn').annotate(response_count=Count('quiz'))
        least_answered = question_responses_count.order_by('response_count')
        most_answered = question_responses_count.order_by('-response_count')
        most_answered_questions = [item['quiz__questions__qstn'] for item in most_answered]
        least_answered_questions = [item['quiz__questions__qstn'] for item in least_answered]


        total_users=User.objects.count()
        passed_users = UserQuizResponse.objects.filter(score__gte=40).values('user').distinct().count()
        percentage_of_users= (passed_users/total_users)*100


        Quiz_Overview= {
            'total_quizzes': total_quizzes,
            'total_quiz_takers': total_quiz_takers,
            'average_quiz_score': average_quiz_score,
        }

        Performance_Metrics= {
            'quiz_taken_counts': list(quiz_taken_counts),
            'average_scores': list(avgscores_of_eachquiz),  
            'highest_score': highest_score,
            'lowest_score': lowest_score,
        }

        Question_Statistics = {
            "most_answered_questions":most_answered_questions,
            "least_answered_questions":least_answered_questions
        }

        Percentage = {
            "percentage_of_users_passed":percentage_of_users,
        }

        return Response({
            'Quiz_Overview': Quiz_Overview,
            'Performance_Metrics': Performance_Metrics,
            'Question_Statistics': Question_Statistics,
            'percentage_of_users_passed':percentage_of_users
        })


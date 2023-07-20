from .models import User,Quiz,Question,Answers,UserQuizResponse
from rest_framework import serializers


class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password", "password2"]

    def save(self):
        register = User(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Password should match'})
        register.set_password(password)
        register.save()
        return register


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answers
        fields = ('id', 'choice','ans','is_correct')


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ('id', 'qstn', 'answers')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    created_user=UserSerializer(read_only=True)

    class Meta:
        model = Quiz
        fields = '__all__'

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(**validated_data)
        for question_data in questions_data:
            answers_data = question_data.pop('answers')
            question = Question.objects.create(quiz=quiz, **question_data)
            for answer_data in answers_data:
                Answers.objects.create(question=question, **answer_data)
        return quiz



class QuizListSerializer(serializers.ModelSerializer):
    class Meta:
        model=Quiz
        fields=('id', 'topic', 'title','difficulty_level', 'created_at')
    

class QuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answers
        fields = ('id', 'choice', 'ans')

class QuizQuestionSerializer(serializers.ModelSerializer):
    answers = QuizAnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ('id', 'qstn', 'answers')

class QuizTakingSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ('title', 'questions')

class QuizResultSerializer(serializers.ModelSerializer):
    class Meta: 
        model=UserQuizResponse
        fields = '__all__'



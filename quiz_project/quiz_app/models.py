from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


class Quiz(models.Model):

    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    topic= models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    difficulty_level = models.CharField(max_length=50,choices=DIFFICULTY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    created_user=models.ForeignKey(User, on_delete=models.CASCADE)


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE,related_name='questions')
    qstn = models.CharField(max_length=255)


class Answers(models.Model):
    CHOICES = [
        ('A', 'Choice A'),
        ('B', 'Choice B'),
        ('C', 'Choice C'),
    ]
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    ans = models.CharField(max_length=255)
    choice = models.CharField(max_length=1, choices=CHOICES)
    is_correct = models.BooleanField(default=False)


class UserQuizResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

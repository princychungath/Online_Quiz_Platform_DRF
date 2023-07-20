from django.contrib import admin
from .models import User,Quiz,Question,Answers,UserQuizResponse

class UserQuizResponse_admin(admin.ModelAdmin):
    list_display = ['user','quiz','score','timestamp'] 
admin.site.register(UserQuizResponse,UserQuizResponse_admin)

class User_admin(admin.ModelAdmin):
    list_display = ['username'] 
admin.site.register(User,User_admin)

class Quiz_admin(admin.ModelAdmin):
    list_display = ['title'] 
admin.site.register(Quiz,Quiz_admin)

class Question_admin(admin.ModelAdmin):
    list_display = ['qstn'] 
admin.site.register(Question,Question_admin)

class Answers_admin(admin.ModelAdmin):
    list_display = ['ans'] 
admin.site.register(Answers,Answers_admin)


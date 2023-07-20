from django.urls import path
from quiz_app import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns=[
    path('register/',views.RegisterUser.as_view(),name="register"),
    path('login/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('reg/user/',views.AdminRegisterUser.as_view(),name="register-admin"),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/',views.UserDetailView.as_view(), name='user-detail'),

    path('profile/',views.UserProfile.as_view(), name='user-profile'),
    path('result/view/',views.QuizResultView.as_view(), name='quiz-result'),
    path('analytics/',views.QuizAnalyticsView.as_view(), name='analytics'),

    path('quiz/create/',views.QuizCreateView.as_view(), name='quiz-create'),
    path('quiz/list/filter/',views.QuizListfilter.as_view(), name='quiz-filter'),
    path('quiz/take/<int:pk>/',views.QuizTakingView.as_view(), name='quiz-taking'),

]
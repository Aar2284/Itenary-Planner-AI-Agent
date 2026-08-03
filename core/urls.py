from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("questions/", views.question_list_view, name="question_list"),
    path("ask/", views.ask_question_view, name="ask"),
    path("questions/<int:pk>/", views.question_detail_view, name="question_detail"),
    path("questions/<int:pk>/answer/", views.post_answer_view, name="post_answer"),
    path("answers/<int:pk>/vote/", views.toggle_vote_view, name="toggle_vote"),
]

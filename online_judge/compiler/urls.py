from django.urls import path
from . import views

app_name = 'compiler'

urlpatterns = [
    path('', views.start_view, name='start'),
    path('home/', views.home_view, name='home'),
    path('playground/', views.playground_view, name='playground'),
    path('questions/', views.question_list_view, name='question_list'),
    path('questions/<int:question_id>/', views.question_detail_view, name='question_detail'),
    path('run-code/', views.run_code, name='run_code'),
    path('submit-code/', views.submit_code, name='submit_code'),
]

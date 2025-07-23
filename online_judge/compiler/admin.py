from django.contrib import admin
from .models import Question, TestCase, Submission

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'created_at']
    list_filter = ['difficulty', 'created_at']
    search_fields = ['title', 'description']

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['question', 'input_data', 'expected_output']
    list_filter = ['question']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'passed_tests', 'total_tests', 'submitted_at']
    list_filter = ['question', 'submitted_at']

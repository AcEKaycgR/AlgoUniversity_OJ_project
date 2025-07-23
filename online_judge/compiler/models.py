from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=10,
        choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')],
        default='Easy'
    )
    sample_input = models.TextField()
    sample_output = models.TextField()
    explanation = models.TextField(blank=True)
    constraints = models.TextField(blank=True)
    follow_up = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Add starter code templates
    python_starter = models.TextField(default="class Solution:\n    def solve(self):\n        pass")
    java_starter = models.TextField(blank=True)
    cpp_starter = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.id}. {self.title}"

class Example(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='examples')
    input_data = models.TextField()
    output_data = models.TextField()
    explanation = models.TextField(blank=True)
    order = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['order']

class TestCase(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_example = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Test case for {self.question.title}"

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    code = models.TextField()
    passed_tests = models.IntegerField()
    total_tests = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question.title}"

import subprocess
import tempfile
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question, Submission
import json

def start_view(request):
    if request.user.is_authenticated:
        return redirect('compiler:home')
    return render(request, 'compiler/start.html')

@login_required
def home_view(request):
    return render(request, 'compiler/home.html')

@login_required
def playground_view(request):
    return render(request, 'compiler/playground.html')

@login_required
def question_list_view(request):
    questions = Question.objects.all()
    return render(request, 'compiler/question_list.html', {'questions': questions})

@login_required
def question_detail_view(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    return render(request, 'compiler/question_detail.html', {'question': question})

@csrf_exempt
def run_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')
        input_data = data.get('input', '')
        
        try:
            # Create temporary file for the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run the code with input
            process = subprocess.run(
                ['python', temp_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Clean up
            os.unlink(temp_file)
            
            if process.returncode == 0:
                return JsonResponse({'success': True, 'output': process.stdout})
            else:
                return JsonResponse({'success': False, 'error': process.stderr})
                
        except subprocess.TimeoutExpired:
            return JsonResponse({'success': False, 'error': 'Code execution timed out'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def submit_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')
        question_id = data.get('question_id')
        
        question = get_object_or_404(Question, id=question_id)
        test_cases = question.test_cases.all()
        
        passed = 0
        total = len(test_cases)
        
        for test_case in test_cases:
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                
                process = subprocess.run(
                    ['python', temp_file],
                    input=test_case.input_data,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                os.unlink(temp_file)
                
                if process.returncode == 0 and process.stdout.strip() == test_case.expected_output.strip():
                    passed += 1
                    
            except Exception:
                pass
        
        # Save submission
        Submission.objects.create(
            user=request.user,
            question=question,
            code=code,
            passed_tests=passed,
            total_tests=total
        )
        
        return JsonResponse({
            'success': True,
            'passed': passed,
            'total': total,
            'message': f'Passed {passed}/{total} test cases'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

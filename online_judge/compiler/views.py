import subprocess
import tempfile
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Question, Submission, TestCase
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
    questions = Question.objects.all().order_by('id')
    return render(request, 'compiler/question_list.html', {'questions': questions})

@login_required
def question_detail_view(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    # Get test cases for display - both examples and regular test cases
    test_cases = question.test_cases.all()[:5]  # Limit to first 5 test cases
    # Get user's last submission
    last_submission = Submission.objects.filter(
        user=request.user, 
        question=question
    ).order_by('-submitted_at').first()
    
    context = {
        'question': question,
        'test_cases': test_cases,
        'last_submission': last_submission,
    }
    return render(request, 'compiler/question_detail.html', context)


def execute_code(code, language, input_data="", timeout=10):
    """
    Execute code in different programming languages
    Returns: (success: bool, output: str, error: str)
    """
    try:
        if language == 'python':
            return execute_python(code, input_data, timeout)
        elif language == 'java':
            return execute_java(code, input_data, timeout)
        elif language == 'cpp':
            return execute_cpp(code, input_data, timeout)
        else:
            return False, "", "Unsupported language"
    except Exception as e:
        return False, "", str(e)

def execute_python(code, input_data, timeout):
    """Execute Python code"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        process = subprocess.run(
            ['python', temp_file],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        os.unlink(temp_file)
        
        if process.returncode == 0:
            return True, process.stdout.strip(), ""
        else:
            return False, "", process.stderr.strip()
            
    except subprocess.TimeoutExpired:
        os.unlink(temp_file)
        return False, "", f"Code execution timed out ({timeout}s limit)"
    except Exception as e:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        return False, "", str(e)

def execute_java(code, input_data, timeout):
    """Execute Java code"""
    # Create temporary directory for Java files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Extract class name from code (simple approach)
        class_name = "Solution"
        if "public class" in code:
            lines = code.split('\n')
            for line in lines:
                if "public class" in line:
                    class_name = line.split("public class")[1].split()[0].split('{')[0]
                    break
        
        java_file = os.path.join(temp_dir, f"{class_name}.java")
        class_file = os.path.join(temp_dir, f"{class_name}.class")
        
        # Write Java code to file
        with open(java_file, 'w') as f:
            f.write(code)
        
        # Compile Java code
        compile_process = subprocess.run(
            ['javac', java_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if compile_process.returncode != 0:
            return False, "", f"Compilation Error: {compile_process.stderr.strip()}"
        
        # Run Java code
        run_process = subprocess.run(
            ['java', '-cp', temp_dir, class_name],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if run_process.returncode == 0:
            return True, run_process.stdout.strip(), ""
        else:
            return False, "", run_process.stderr.strip()
            
    except subprocess.TimeoutExpired:
        return False, "", f"Code execution timed out ({timeout}s limit)"
    except Exception as e:
        return False, "", str(e)
    finally:
        # Clean up temporary files
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass

def execute_cpp(code, input_data, timeout):
    """Compile and execute C++ code safely with proper flags (Windows)"""
    
    cpp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False)
    exe_file = tempfile.NamedTemporaryFile(delete=False, suffix='.exe')  # ✅ Ensure .exe extension
    exe_file.close()  # Close so g++ can write to it

    try:
        # Write code to .cpp file
        cpp_file.write(code)
        cpp_file.close()

        # Compile the code with MinGW and proper flags
        compile_cmd = [
            'g++',
            '-std=c++17',
            '-static-libgcc',
            '-static-libstdc++',
            '-mconsole',            # ✅ Ensure console entry point (main)
            cpp_file.name,
            '-o',
            exe_file.name
        ]

        compile_process = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            timeout=timeout // 2
        )

        if compile_process.returncode != 0:
            error_msg = compile_process.stderr.replace(cpp_file.name, 'solution.cpp')
            return False, "", f"Compilation Error:\n{error_msg}"

        # Run the compiled executable
        run_process = subprocess.run(
            [exe_file.name],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if run_process.returncode == 0:
            return True, run_process.stdout.strip(), ""
        else:
            return False, "", f"Runtime Error:\n{run_process.stderr.strip()}"

    except subprocess.TimeoutExpired:
        return False, "", f"Time limit exceeded ({timeout}s)"
    except Exception as e:
        return False, "", str(e)
    finally:
        # Clean up
        try:
            os.unlink(cpp_file.name)
            os.unlink(exe_file.name)
        except:
            pass


@csrf_exempt
@require_http_methods(["POST"])
def run_code(request):
    try:
        data = json.loads(request.body)
        code = data.get('code', '')
        input_data = data.get('input', '')
        language = data.get('language', 'python')  # Default to Python
        
        if not code.strip():
            return JsonResponse({'success': False, 'error': 'No code provided'})

        # Execute code based on language
        success, output, error = execute_code(code, language, input_data)
        
        if success:
            return JsonResponse({'success': True, 'output': output})
        else:
            return JsonResponse({'success': False, 'error': error})
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
def submit_code(request):
    try:
        data = json.loads(request.body)
        code = data.get('code', '')
        question_id = data.get('question_id')
        language = data.get('language', 'python')  # Default to Python

        if not code.strip():
            return JsonResponse({'success': False, 'error': 'No code provided'})

        question = get_object_or_404(Question, id=question_id)
        test_cases = question.test_cases.all()
        
        if not test_cases:
            return JsonResponse({'success': False, 'error': 'No test cases available'})

        passed = 0
        total = len(test_cases)
        failed_test_details = []

        for i, test_case in enumerate(test_cases):
            success, output, error = execute_code(code, language, test_case.input_data)
            
            if success and output == test_case.expected_output.strip():
                passed += 1
            else:
                failed_test_details.append({
                    'test_case': i + 1,
                    'expected': test_case.expected_output.strip(),
                    'actual': output if success else f"Error: {error}",
                    'input': test_case.input_data
                })

        # Save submission
        Submission.objects.create(
            user=request.user,
            question=question,
            code=code,
            passed_tests=passed,
            total_tests=total
        )

        response_data = {
            'success': True,
            'passed': passed,
            'total': total,
            'message': f'Passed {passed}/{total} test cases'
        }
        
        # Include failed test details if any
        if failed_test_details:
            response_data['failed_tests'] = failed_test_details[:3]  # Limit to first 3 failures

        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})

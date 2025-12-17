"""
Flask API for BODMAS Master Tutoring System
Provides REST endpoints and serves a BODMAS-focused intelligent tutoring interface
"""

from flask import Flask, render_template, jsonify, request
import re
from typing import List, Dict

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# ========================
# BODMAS Solver & Validation
# ========================

class BODMASSolver:
    """Solves arithmetic expressions following BODMAS rules"""
    
    def __init__(self):
        self.operations = {
            '+': (1, lambda a, b: a + b),
            '-': (1, lambda a, b: a - b),
            '*': (2, lambda a, b: a * b),
            '/': (2, lambda a, b: a / b if b != 0 else float('inf')),
            '**': (3, lambda a, b: a ** b),
        }
    
    def solve(self, expr: str) -> float:
        """Solve expression following BODMAS - the ONLY correct way"""
        try:
            # Use Python's built-in eval which follows BODMAS rules
            result = eval(expr)
            return float(result)
        except Exception as e:
            return None
    
    def validate_answer(self, expr: str, student_answer: float) -> Dict:
        """Strictly validate answer against BODMAS rules"""
        try:
            correct_answer = self.solve(expr)
            
            if correct_answer is None:
                return {
                    'is_correct': False,
                    'error': 'Invalid expression',
                    'correct_answer': None
                }
            
            # Allow small floating point errors
            is_correct = abs(float(student_answer) - correct_answer) < 0.0001
            
            return {
                'is_correct': is_correct,
                'correct_answer': correct_answer,
                'student_answer': float(student_answer)
            }
        except Exception as e:
            return {
                'is_correct': False,
                'error': str(e),
                'correct_answer': None
            }
    
    def get_correct_steps(self, expr: str) -> List[Dict]:
        """Get step-by-step solution following BODMAS"""
        steps = [{'step': 0, 'expression': expr, 'description': 'Original expression'}]
        
        try:
            # Remove spaces
            expr_clean = expr.replace(' ', '')
            
            # Handle brackets
            step_num = 1
            current_expr = expr_clean
            
            while '(' in current_expr:
                match = re.search(r'\([^()]+\)', current_expr)
                if match:
                    bracket_expr = match.group(0)[1:-1]
                    try:
                        bracket_result = eval(bracket_expr)
                        new_expr = current_expr[:match.start()] + str(bracket_result) + current_expr[match.end():]
                        steps.append({
                            'step': step_num,
                            'expression': new_expr,
                            'description': f'Brackets: ({bracket_expr}) = {bracket_result}'
                        })
                        current_expr = new_expr
                        step_num += 1
                    except:
                        break
                else:
                    break
            
            # Handle exponents
            while '**' in current_expr:
                match = re.search(r'(\d+\.?\d*)\*\*(\d+\.?\d*)', current_expr)
                if match:
                    try:
                        result = float(match.group(1)) ** float(match.group(2))
                        new_expr = current_expr[:match.start()] + str(result) + current_expr[match.end():]
                        steps.append({
                            'step': step_num,
                            'expression': new_expr,
                            'description': f'Orders/Exponents: {match.group(0)} = {result}'
                        })
                        current_expr = new_expr
                        step_num += 1
                    except:
                        break
                else:
                    break
            
            # Handle multiplication and division (left to right)
            while '*' in current_expr or '/' in current_expr:
                match = re.search(r'(-?\d+\.?\d*)\s*([\*/])\s*(-?\d+\.?\d*)', current_expr)
                if match:
                    try:
                        op = match.group(2)
                        a, b = float(match.group(1)), float(match.group(3))
                        result = a * b if op == '*' else a / b if b != 0 else float('inf')
                        new_expr = current_expr[:match.start()] + str(result) + current_expr[match.end():]
                        steps.append({
                            'step': step_num,
                            'expression': new_expr,
                            'description': f'Division/Multiplication: {match.group(0)} = {result}'
                        })
                        current_expr = new_expr
                        step_num += 1
                    except:
                        break
                else:
                    break
            
            # Handle addition and subtraction (left to right)
            while '+' in current_expr[1:] or '-' in current_expr[1:]:  # Skip leading sign
                match = re.search(r'(-?\d+\.?\d*)\s*([\+\-])\s*(-?\d+\.?\d*)', current_expr[1:])
                if match:
                    try:
                        offset = 1
                        op = match.group(2)
                        a, b = float(match.group(1)), float(match.group(3))
                        result = a + b if op == '+' else a - b
                        new_expr = current_expr[:match.start() + offset] + str(result) + current_expr[match.end() + offset:]
                        steps.append({
                            'step': step_num,
                            'expression': new_expr,
                            'description': f'Addition/Subtraction: {match.group(0)} = {result}'
                        })
                        current_expr = new_expr
                        step_num += 1
                    except:
                        break
                else:
                    break
            
            return steps
        except Exception as e:
            return steps

solver = BODMASSolver()

# ========================
# Helper Functions
# ========================

def get_sample_questions() -> List[Dict]:
    """Get sample BODMAS questions from ontology"""
    return [
        {
            'id': 1,
            'question': '2 + 3 * 4',
            'difficulty': 'Easy',
            'concept': 'Multiplication before Addition',
            'correct_answer': 14
        },
        {
            'id': 2,
            'question': '(2 + 3) * 4',
            'difficulty': 'Easy',
            'concept': 'Brackets first',
            'correct_answer': 20
        },
        {
            'id': 3,
            'question': '10 - 2 * 3',
            'difficulty': 'Medium',
            'concept': 'Multiplication before Subtraction',
            'correct_answer': 4
        },
        {
            'id': 4,
            'question': '20 / 4 + 3',
            'difficulty': 'Medium',
            'concept': 'Division before Addition',
            'correct_answer': 8
        },
        {
            'id': 5,
            'question': '2 ** 3 + 4',
            'difficulty': 'Medium',
            'concept': 'Orders/Exponents first',
            'correct_answer': 12
        },
        {
            'id': 6,
            'question': '(10 - 4) * 2 + 3',
            'difficulty': 'Hard',
            'concept': 'Complex expression',
            'correct_answer': 15
        },
        {
            'id': 7,
            'question': '24 / 3 / 2',
            'difficulty': 'Hard',
            'concept': 'Division left to right',
            'correct_answer': 4
        },
        {
            'id': 8,
            'question': '2 * 3 + 4 * 5',
            'difficulty': 'Hard',
            'concept': 'Multiple operations',
            'correct_answer': 26
        },
    ]

# ========================
# API Routes
# ========================

@app.route('/')
def index():
    """Serve the BODMAS tutoring interface"""
    return render_template('index.html')

@app.route('/api/questions')
def api_questions():
    """API endpoint: Get sample BODMAS questions"""
    try:
        questions = get_sample_questions()
        return jsonify({
            'success': True,
            'questions': questions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/solve', methods=['POST'])
def api_solve():
    """API endpoint: Solve a BODMAS expression"""
    try:
        data = request.get_json()
        expr = data.get('expression', '')
        
        if not expr:
            return jsonify({
                'success': False,
                'error': 'Expression is required'
            }), 400
        
        steps = solver.get_correct_steps(expr)
        answer = solver.solve(expr)
        
        return jsonify({
            'success': True,
            'expression': expr,
            'answer': answer,
            'steps': steps
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Invalid expression: {str(e)}'
        }), 400

@app.route('/api/check-answer', methods=['POST'])
def api_check_answer():
    """API endpoint: Check student's answer and provide feedback"""
    try:
        data = request.get_json()
        expr = data.get('expression', '')
        student_answer = data.get('answer')
        
        if not expr or student_answer is None:
            return jsonify({
                'success': False,
                'error': 'Expression and answer are required'
            }), 400
        
        # Convert to float
        try:
            student_answer = float(student_answer)
        except:
            return jsonify({
                'success': False,
                'error': 'Invalid answer format. Please enter a number.'
            }), 400
        
        # Validate answer strictly against BODMAS rules
        validation = solver.validate_answer(expr, student_answer)
        
        if 'error' in validation:
            return jsonify({
                'success': False,
                'error': validation['error']
            }), 400
        
        # Get correct steps
        steps = solver.get_correct_steps(expr)
        
        response = {
            'success': True,
            'expression': expr,
            'student_answer': validation['student_answer'],
            'correct_answer': validation['correct_answer'],
            'is_correct': validation['is_correct'],
            'steps': steps,
            'feedback': generate_feedback(validation)
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/learn/<concept>')
def api_learn_concept(concept):
    """API endpoint: Get learning material for a BODMAS concept"""
    concepts = {
        'brackets': {
            'title': 'Understanding Brackets',
            'description': 'Brackets show which calculation to do first',
            'rule': 'Always solve what is inside brackets before doing anything else',
            'example': '(2 + 3) × 4 = 5 × 4 = 20, NOT 2 + (3 × 4) = 2 + 12 = 14',
            'common_mistakes': ['Ignoring brackets', 'Solving outside brackets first']
        },
        'orders': {
            'title': 'Understanding Orders (Exponents)',
            'description': 'Orders means powers, roots, and other similar operations',
            'rule': 'Solve exponents and powers before multiplication/division',
            'example': '2 × 3² = 2 × 9 = 18, NOT (2 × 3)² = 6² = 36',
            'common_mistakes': ['Treating exponents as multiplication', 'Wrong order of operations']
        },
        'division_multiplication': {
            'title': 'Division and Multiplication',
            'description': 'These operations have equal priority and are done left to right',
            'rule': 'Do multiplication and division from left to right, before addition/subtraction',
            'example': '12 ÷ 2 × 3 = 6 × 3 = 18, NOT 12 ÷ (2 × 3) = 12 ÷ 6 = 2',
            'common_mistakes': ['Wrong order', 'Not going left to right']
        },
        'addition_subtraction': {
            'title': 'Addition and Subtraction',
            'description': 'These are done last and from left to right',
            'rule': 'Do addition and subtraction from left to right, after all other operations',
            'example': '10 - 2 + 3 = 8 + 3 = 11, NOT 10 - (2 + 3) = 10 - 5 = 5',
            'common_mistakes': ['Wrong order', 'Not going left to right']
        }
    }
    
    if concept not in concepts:
        return jsonify({
            'success': False,
            'error': f'Unknown concept: {concept}'
        }), 404
    
    return jsonify({
        'success': True,
        'concept': concepts[concept]
    })

def generate_feedback(validation: Dict) -> str:
    """Generate personalized feedback based on validation"""
    if validation['is_correct']:
        return '🎉 Excellent! Your answer is correct!'
    else:
        return f'❌ Incorrect. Your answer: {validation["student_answer"]}, Correct answer: {validation["correct_answer"]}'

# ========================
# Error Handlers
# ========================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("Starting BODMAS Master Tutoring System...")
    print("Web interface available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

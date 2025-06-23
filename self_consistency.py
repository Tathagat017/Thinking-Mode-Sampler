#!/usr/bin/env python3
"""
Simple Self-Consistency Evaluation
Compares single deterministic vs majority vote for GRE problems.
"""

import os
import re
import json
from collections import Counter
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# GRE Problems
PROBLEMS = [
    {"problem": "A store sold 450 books Monday, 325 Tuesday, 275 Wednesday. Thursday it sold 50 more than Wednesday. Total books sold?", "answer": 1100},
    {"problem": "Sarah has $120. Spends 1/4 on jacket, 1/3 of remaining on shoes. Money left?", "answer": 60},
    {"problem": "Train travels 240 miles in 4 hours. How many miles in 7 hours at same speed?", "answer": 420},
    {"problem": "Class of 30: 18 girls, rest boys. 2/3 girls and 3/4 boys play sports. How many play sports?", "answer": 21},
    {"problem": "Rectangle 15cm x 8cm. Length +20%, width -25%. New area?", "answer": 108},
    {"problem": "Tom scored 85, 92, 78 on three tests. What score needed on fourth test for 88 average?", "answer": 97},
    {"problem": "Item costs $75, 20% discount, then 6% tax on discounted price. Total paid?", "answer": 63.6},
    {"problem": "Pool filled by pipe A in 6 hours, pipe B in 8 hours. Both together?", "answer": 3.43},
    {"problem": "Car to motorcycle ratio 5:2. If 35 cars, how many motorcycles?", "answer": 14},
    {"problem": "Profit increased from $50,000 to $65,000. Percentage increase?", "answer": 30}
]

def get_response(problem, temperature=0):
    """Get response from OpenAI."""
    prompt = f"Solve: {problem}\n\nLet's think step-by-step:"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=300
    )
    return response.choices[0].message.content

def extract_number(text):
    """Extract final answer number from response."""
    # Look for numbers in the response
    numbers = re.findall(r'\d+(?:\.\d+)?', text)
    return float(numbers[-1]) if numbers else None

def evaluate_problem(problem_data):
    """Evaluate one problem with both methods."""
    problem = problem_data["problem"]
    correct = problem_data["answer"]
    
    print(f"\nProblem: {problem}")
    print(f"Correct: {correct}")
    
    # Method 1: Single deterministic
    det_response = get_response(problem, temperature=0)
    det_answer = extract_number(det_response)
    det_correct = abs(det_answer - correct) < 0.1 if det_answer else False
    
    print(f"Deterministic: {det_answer} ({'✓' if det_correct else '✗'})")
    
    # Method 2: Majority vote (10 samples)
    answers = []
    for i in range(10):
        response = get_response(problem, temperature=1.1)
        answer = extract_number(response)
        if answer:
            answers.append(answer)
    
    if answers:
        majority_answer = Counter(answers).most_common(1)[0][0]
        maj_correct = abs(majority_answer - correct) < 0.1
        print(f"Majority vote: {majority_answer} ({'✓' if maj_correct else '✗'})")
        print(f"All answers: {answers}")
    else:
        majority_answer = None
        maj_correct = False
        print("Majority vote: Failed to extract answers")
    
    return {
        "problem": problem,
        "correct_answer": correct,
        "deterministic_answer": det_answer,
        "deterministic_correct": det_correct,
        "majority_answer": majority_answer,
        "majority_correct": maj_correct,
        "all_answers": answers
    }

def main():
    """Run evaluation on all problems."""
    if not os.environ.get("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY environment variable")
        return
    
    results = []
    det_score = 0
    maj_score = 0
    
    for i, problem_data in enumerate(PROBLEMS):
        print(f"\n{'='*50}")
        print(f"Problem {i+1}/10")
        
        result = evaluate_problem(problem_data)
        results.append(result)
        
        if result["deterministic_correct"]:
            det_score += 1
        if result["majority_correct"]:
            maj_score += 1
    
    # Final results
    print(f"\n{'='*50}")
    print("RESULTS")
    print(f"{'='*50}")
    print(f"Deterministic accuracy: {det_score}/10 ({det_score*10}%)")
    print(f"Majority vote accuracy: {maj_score}/10 ({maj_score*10}%)")
    print(f"Improvement: {(maj_score-det_score)*10:+}%")
    
    # Save results
    with open("problems.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to problems.json")

if __name__ == "__main__":
    main() 
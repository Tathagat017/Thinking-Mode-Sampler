#!/usr/bin/env python3
"""
Generate accuracy comparison chart.
"""

import json
import matplotlib.pyplot as plt

def create_accuracy_chart():
    """Create accuracy comparison chart and save as accuracy.png"""
    try:
        with open("problems.json", "r") as f:
            results = json.load(f)
    except FileNotFoundError:
        print("Run self_consistency.py first to generate results")
        return
    
    # Count correct answers
    det_correct = sum(1 for r in results if r["deterministic_correct"])
    maj_correct = sum(1 for r in results if r["majority_correct"])
    total = len(results)
    
    # Create simple bar chart
    methods = ['Deterministic\n(temp=0)', 'Majority Vote\n(temp=1.1)']
    scores = [det_correct/total, maj_correct/total]
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(methods, scores, color=['lightcoral', 'lightblue'], alpha=0.7)
    
    # Add percentage labels
    for bar, score in zip(bars, scores):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{score:.1%}', ha='center', va='bottom')
    
    plt.ylabel('Accuracy')
    plt.title('Chain-of-Thought: Deterministic vs Self-Consistency')
    plt.ylim(0, 1)
    plt.tight_layout()
    
    # Save chart
    plt.savefig('accuracy.png', dpi=150, bbox_inches='tight')
    print("Accuracy chart saved as accuracy.png")
    
    # Show improvement
    improvement = (maj_correct - det_correct) / total
    print(f"\nAccuracy Results:")
    print(f"Deterministic: {det_correct}/{total} ({det_correct/total:.1%})")
    print(f"Majority Vote: {maj_correct}/{total} ({maj_correct/total:.1%})")
    print(f"Improvement: {improvement:+.1%}")

if __name__ == "__main__":
    create_accuracy_chart() 
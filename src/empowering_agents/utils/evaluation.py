def empowerment_score(goal_completion_rate: float, avg_satisfaction: float) -> float:
    return (goal_completion_rate * 0.6) + (avg_satisfaction * 0.4)

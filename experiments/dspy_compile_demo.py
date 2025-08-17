"""
DSPy Compile Demo: Planning & Actions
-------------------------------------
This script shows how to *compile* a small planning program with DSPy using a few
seed examples. It optimizes prompts/demos to improve JSON-structured outputs.

Requirements:
  - Set LLM_PROVIDER=openai and OPENAI_API_KEY in your .env
  - Optional: set OPENAI_MODEL (defaults to gpt-4o-mini)

Run:
  python experiments/dspy_compile_demo.py
"""

import os, json, random, sys
from dotenv import load_dotenv

load_dotenv()

provider = os.getenv("LLM_PROVIDER", "dummy").lower()
if provider != "openai":
    print("Set LLM_PROVIDER=openai and OPENAI_API_KEY in your .env to run the DSPy compile demo.")
    sys.exit(0)

try:
    import dspy
except ImportError:
    print("Please install dspy-ai first: pip install dspy-ai")
    sys.exit(1)

model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
dspy.configure(lm=dspy.OpenAI(model=model))

# --- Signatures ---
class PlanGoal(dspy.Signature):
    """Create a SMART learning goal from a user message and context."""
    user_message: str
    context_json: str
    goal_json: str  # JSON with fields: objective, why, timeframe, milestones

class PlanActions(dspy.Signature):
    """Given a learning goal JSON, return 3 concrete next steps as JSON list."""
    goal_json: str
    steps_json: str  # JSON list of steps

# --- Program ---
class Planner(dspy.Module):
    def __init__(self):
        super().__init__()
        self.plan_goal = dspy.Predict(PlanGoal)
        self.plan_actions = dspy.Predict(PlanActions)

    def forward(self, user_message: str, context_json: str):
        g = self.plan_goal(user_message=user_message, context_json=context_json).goal_json
        s = self.plan_actions(goal_json=g).steps_json
        return dict(goal_json=g, steps_json=s)

# --- Seed training data (tiny, illustrative) ---
train = [
    dspy.Example(
        user_message="I want to learn data analysis to change jobs in 3 months.",
        context_json=json.dumps({"timeframe":"90 days","constraints":["evenings only"]}),
        goal_json=json.dumps({
            "objective":"Learn data analysis fundamentals",
            "why":"Qualify for entry-level data analyst roles",
            "timeframe":"90 days",
            "milestones":["Finish SQL basics","Complete 3 analysis projects","Learn basic statistics"]
        }),
        steps_json=json.dumps([
            "Block 25 minutes this evening for SQL SELECT practice",
            "Pick one dataset and outline analysis questions",
            "Log one takeaway and one confusion point"
        ])
    ).with_inputs("user_message","context_json"),
    dspy.Example(
        user_message="I have 8 weeks to pass the AWS Cloud Practitioner exam.",
        context_json=json.dumps({"timeframe":"56 days","constraints":["weekends + 2 weeknights"]}),
        goal_json=json.dumps({
            "objective":"Pass AWS Cloud Practitioner",
            "why":"Improve cloud literacy and career prospects",
            "timeframe":"56 days",
            "milestones":["Finish official AWS learning path","Do 4 full practice tests","Review weak domains"]
        }),
        steps_json=json.dumps([
            "Schedule two 45-minute study blocks this week",
            "Skim exam guide and mark weak topics",
            "Attempt 20 practice questions and review mistakes"
        ])
    ).with_inputs("user_message","context_json"),
    dspy.Example(
        user_message="I want conversational Spanish for travel in 10 weeks.",
        context_json=json.dumps({"timeframe":"70 days","constraints":["10-15min daily","mobile-first"]}),
        goal_json=json.dumps({
            "objective":"Achieve basic conversational Spanish",
            "why":"Travel confidently and connect with locals",
            "timeframe":"70 days",
            "milestones":["Master 500 core words","Complete phrasebook basics","Hold 3 five-minute chats"]
        }),
        steps_json=json.dumps([
            "Do a 10-minute phrase review today (greetings, directions)",
            "Record yourself saying 10 phrases; note pronunciation issues",
            "Schedule a 5-minute chat with a language buddy this week"
        ])
    ).with_inputs("user_message","context_json"),
]

# Hold-out dev example
dev = [
    dspy.Example(
        user_message="I need to learn Python for data work within 6 weeks.",
        context_json=json.dumps({"timeframe":"42 days","constraints":["30 min/day","beginner"]}),
    ).with_inputs("user_message","context_json")
]

# --- Metric: score JSON quality and structure ---
def metric(example, pred, trace=None):
    score = 0.0
    try:
        g = json.loads(pred["goal_json"])
        if isinstance(g, dict):
            score += 0.4
            needed = {"objective","why","timeframe","milestones"}
            score += 0.2 * (len(needed.intersection(g.keys()))/len(needed))
    except Exception:
        pass
    try:
        s = json.loads(pred["steps_json"])
        if isinstance(s, list) and len(s) >= 3:
            score += 0.4
    except Exception:
        pass
    return max(0.0, min(1.0, score))

# --- Teleprompter (few-shot bootstrapping) ---
from dspy.teleprompt import BootstrapFewShot

teleprompter = BootstrapFewShot(
    metric=metric,
    max_bootstrapped_demos=4,
    max_labeled_demos=len(train),
    num_candidate_programs=8
)

compiled = teleprompter.compile(task=Planner(), trainset=train)

print("=== COMPILED PROGRAM ===")
print(compiled)

# Evaluate on dev (quick check)
for ex in dev:
    pred = compiled(ex.user_message, ex.context_json)
    print("\\n--- DEV PREDICTION ---")
    print("Goal JSON:", pred["goal_json"])
    print("Steps JSON:", pred["steps_json"])

# Save artifacts (simple text dump)
os.makedirs("experiments/.artifacts", exist_ok=True)
with open("experiments/.artifacts/compiled_planner.txt", "w", encoding="utf-8") as f:
    f.write(str(compiled))
print("\\nSaved: experiments/.artifacts/compiled_planner.txt")

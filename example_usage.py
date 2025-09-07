import os
import sys

# Ensure src is in the path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core import unittestplus
from manipulate import run_regression
from testsuite import TestSuite


# --- Simple function to test ---
def add(a, b):
    return a + b


# --- Run unittestplus ---
print("Running unittestplus...")
result = unittestplus(
    func=add,
    inputs=[2, 3],
    expected_output=5,
    alias="Addition test",
    message="Basic addition check",
    assertion={"type": "equals", "value": 5},
    display=True,
)
print("unittestplus result:", result)

# --- Run regression ---
print("\nRunning regression...")
regression_result = run_regression(
    func="add",  # Name as string for regression
    inputs=[[2, 3], [10, 20], [0, 0]],
    display=True,
)
print("regression result:", regression_result)

# --- Run testsuite ---
print("\nRunning testsuite...")
suite = TestSuite()

func = "add"

suite.unittestplus(func, inputs=[5, 5])
suite.unittestplus(func, inputs=[10, 20], expected_output=30)
suite.unittestplus(func, inputs=[-5, 5], expected_output=0)
suite.unittestplus(
    func, inputs=[1, 2], expected_output=3, assertion={"type": "equals", "value": 3}
)
suite.unittestplus(
    func, inputs=[1, 2], expected_output=4, assertion={"type": "equals", "value": 3}
)
suite.unittestplus(
    func, inputs=[1, 2], expected_output=4, assertion={"type": "equals", "value": 2}
)
suite.unittestplus(func, inputs=["1", 2])
suite.run_tests()
suite.print_summary()


#------ Test AI Call --------#
import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

system_prompt = """ 
Be informative
Do not tell the user what you are doing, just do it.
""" 

prompt = "Respond with 500 words on read vs write speed in database design"

max_tokens = 5000

 
params = {
    "model": 'claude-3-7-sonnet-20250219',
    "max_tokens": max_tokens,
    "system": system_prompt,
    "messages": [{"role": "user", "content": prompt}],
}
def call_anthropic_api(params):
    try:
        response = client.messages.create(**params)
        return response.content[0].text
    except anthropic.AnthropicAPIError as e:
        print(f"Anthropic API Error: {e}")
        return None

unittestplus(
    func=call_anthropic_api,
    inputs=params,
    expected_output=5,
    alias="AI Test"
)
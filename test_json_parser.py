from utils import safe_json_parse
import json

# Test the enhanced JSON parser
test_cases = [
    '{"status": "PASS", "feedback": "Good job"}',
    '```json\n{"status": "PASS", "feedback": "Good job"}\n```',
    'Some text here {"status": "PASS", "feedback": "Good job"} more text',
    'Response: {"status": "PASS", "feedback": "Good job"}, End',
    'This is not valid json {"status": "PASS", "feedback": "Good job"} trailing text',
    'Completely invalid text that is not JSON at all'
]

print('Testing enhanced safe_json_parse:')
for i, test_case in enumerate(test_cases):
    result = safe_json_parse(test_case)
    print(f'Test {i+1}: {result}')
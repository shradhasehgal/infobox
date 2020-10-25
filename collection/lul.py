import json

with open('category_dependency.jsonl') as f:
    data = f.readlines()

data = [ json.loads(line) for line in data]

with open('child_to_index.json') as f:
    child_to_index = json.loads(f.read())

print(child_to_index['चित्र_जोड़ें'])

अंतर्राष्ट्रीय_जलक्षेत्र
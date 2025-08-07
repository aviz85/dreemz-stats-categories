#!/usr/bin/env python3
"""Test simplified normalization"""

from groq_service import GroqService

service = GroqService()

test_cases = [
    "build an animal rescue farm in Belgium",
    "להתחתן ושיהיו לי ילדים השנה",
    "לקנות 3 נכסי נדלן",
    "become a YouTube star with 1 million subscribers",
    "open a successful shopping site like Shein and Sephora",
    "למכור את הבית המדהים שלי בקוסטה ריקה",
    "לפתוח עסק מצליח כמו שיין וסאפורו עם דברים של בנות",
    "buy 5 houses in Tel Aviv by 2025"
]

print("TESTING SIMPLIFIED NORMALIZATION")
print("="*60)

for test in test_cases:
    result = service.normalize_dream(test)
    print(f"Input:  {test[:50]}")
    print(f"Output: {result}")
    print("-"*40)
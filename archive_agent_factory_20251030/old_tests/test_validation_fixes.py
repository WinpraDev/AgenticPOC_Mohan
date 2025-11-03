#!/usr/bin/env python3
"""Quick test to verify validation fixes"""

from loguru import logger
from meta_agent.validators.code_validator import validate_code

logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True, format="<level>{message}</level>")

print("\n" + "="*70)
print("TESTING VALIDATION FIXES")
print("="*70 + "\n")

# Test 1: os.getenv() should be allowed
print("Test 1: os.getenv() for DATABASE_URL")
print("-" * 70)
code1 = """
import os
from typing import Dict

class DataAgent:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.password = os.getenv('DB_PASSWORD', '')
    
    def connect(self) -> Dict:
        return {"status": "connected"}
"""

result1 = validate_code(code1)
print(f"Result: {'✅ PASS' if result1.valid else '❌ FAIL'}")
print(f"Risk Score: {result1.risk_score:.2f}")
print(f"Issues: {len(result1.issues)}")
for issue in result1.issues:
    print(f"  - {issue.severity}: {issue.message}")
print()

# Test 2: Hardcoded password should be rejected
print("Test 2: Hardcoded password (should FAIL)")
print("-" * 70)
code2 = """
import os

class DataAgent:
    def __init__(self):
        self.password = "admin123"  # This should be caught
    
    def connect(self):
        return {"status": "connected"}
"""

result2 = validate_code(code2)
print(f"Result: {'✅ PASS' if result2.valid else '❌ FAIL (expected)'}")
print(f"Risk Score: {result2.risk_score:.2f}")
print(f"Issues: {len(result2.issues)}")
for issue in result2.issues:
    print(f"  - {issue.severity}: {issue.message}")
print()

# Test 3: Empty string password should be allowed
print("Test 3: Empty string password")
print("-" * 70)
code3 = """
import os

class DataAgent:
    def __init__(self):
        self.password = ""  # Empty string is OK
        self.api_key = os.getenv('API_KEY', '')
    
    def connect(self):
        return {"status": "connected"}
"""

result3 = validate_code(code3)
print(f"Result: {'✅ PASS' if result3.valid else '❌ FAIL'}")
print(f"Risk Score: {result3.risk_score:.2f}")
print(f"Issues: {len(result3.issues)}")
for issue in result3.issues:
    print(f"  - {issue.severity}: {issue.message}")
print()

# Summary
print("="*70)
print("SUMMARY")
print("="*70)
print(f"Test 1 (os.getenv):        {'✅ PASS' if result1.valid else '❌ FAIL'}")
print(f"Test 2 (hardcoded - fail): {'✅ PASS (correctly rejected)' if not result2.valid else '❌ FAIL (should reject)'}")
print(f"Test 3 (empty string):     {'✅ PASS' if result3.valid else '❌ FAIL'}")

all_pass = result1.valid and not result2.valid and result3.valid
print()
print(f"Overall: {'✅ ALL TESTS PASSED' if all_pass else '❌ SOME TESTS FAILED'}")
print()


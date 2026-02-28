#!/usr/bin/env python3
"""Test script to verify translation accuracy"""

from translator import translate

tests = [
    ('what happened', 'english', 'telugu'),
    ('where is the bathroom', 'english', 'telugu'),  
    ('i am fine', 'english', 'hindi'),
    ('how much does it cost', 'english', 'spanish'),
    ('i am sorry', 'english', 'german'),
    ('can you help me', 'english', 'tamil'),
    ('where are you going', 'english', 'malayalam'),
]

print("\n" + "="*70)
print("TRANSLATION ACCURACY TEST".center(70))
print("="*70 + "\n")

for text, src, tgt in tests:
    r = translate(text, src, tgt)
    icon = "✅" if r["source"] != "not-found" else "❌"
    print(f"{icon} '{text}'")
    print(f"   {src.upper()} → {tgt.upper()}")
    print(f"   Translation: {r['translated']}")
    print(f"   Source: {r['source']} | Confidence: {r['confidence']}\n")

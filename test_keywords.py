#!/usr/bin/env python3
"""
Simple test to verify keyword matching logic
"""

# Sample content from our database
content = """Professional Profile: Alexandros Karanikola
Title: Software Engineer / DevOps | Cloud, AI Infrastructure, and Blockchain
Location: Sydney, Australia

Summary: DevOps & Software Engineer focused on cloud-native platforms, AI infrastructure, and blockchain-enabled security. I build automation and reliability into regulated environments, leading initiatives such as automated Splunk token rotation, automated Tomcat upgrades, and Kafka HA resilience improvements. Entrepreneurial creator of CryptoGent, an enterprise system that tokenises API calls for AI workflows with chain-anchored, per-call cryptographic authorization and verifiable usage receipts.

Elevator Pitch: I'm a DevOps-focused software engineer who makes complex platforms reliable, secure, and automatable. From custom private cloud ops to AI orchestration and blockchain-powered API security, I design and ship systems that reduce toil, harden security, and scale. If you need someone to bridge DevOps, AI infra, and crypto-grade authorization, I'm your engineer."""

# Test keywords
keywords = ["ai", "machine learning", "artificial intelligence"]

print("Content:")
print(content)
print("\n" + "="*60)

print("Testing keyword matching:")
content_lower = content.lower()
for keyword in keywords:
    if keyword.lower() in content_lower:
        print(f"✓ Found: '{keyword}'")
    else:
        print(f"✗ Not found: '{keyword}'")

print(f"\nContent contains 'ai': {'ai' in content_lower}")
print(f"Content contains 'AI': {'AI' in content}")
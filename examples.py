#!/usr/bin/env python3
"""Example script showing how to use adverstorial."""

import os
import sys

# Example usage of the adverstorial CLI
# This script shows the command structure without making actual API calls

def print_usage_examples():
    """Print example commands for using adverstorial."""
    
    print("=" * 80)
    print("ADVERSTORIAL - AI Story Writer Examples")
    print("=" * 80)
    print()
    
    print("Before running, set up your API keys:")
    print("  export OPENAI_API_KEY='your-key-here'")
    print("  export ANTHROPIC_API_KEY='your-key-here'")
    print()
    
    print("Example 1: Basic story with OpenAI")
    print("-" * 80)
    print("python3 -m adverstorial.cli \\")
    print('  --prompt "A detective solves a mystery in space" \\')
    print("  --rounds 3 \\")
    print("  --protagonist-system openai \\")
    print("  --protagonist-model gpt-4 \\")
    print("  --antagonist-system openai \\")
    print("  --antagonist-model gpt-4")
    print()
    
    print("Example 2: Mixed systems (OpenAI + Anthropic)")
    print("-" * 80)
    print("python3 -m adverstorial.cli \\")
    print('  --prompt "A hero battles a dragon" \\')
    print("  --rounds 5 \\")
    print("  --protagonist-system openai \\")
    print("  --protagonist-model gpt-4 \\")
    print("  --antagonist-system anthropic \\")
    print("  --antagonist-model claude-3-5-sonnet-20241022")
    print()
    
    print("Example 3: Save to file")
    print("-" * 80)
    print("python3 -m adverstorial.cli \\")
    print('  --prompt "Time travelers fix paradoxes" \\')
    print("  --rounds 4 \\")
    print("  --protagonist-system anthropic \\")
    print("  --protagonist-model claude-3-5-sonnet-20241022 \\")
    print("  --antagonist-system anthropic \\")
    print("  --antagonist-model claude-3-5-sonnet-20241022 \\")
    print("  --output story.txt")
    print()
    
    print("=" * 80)
    print()
    
    # Check if API keys are set
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    print("API Key Status:")
    print(f"  OPENAI_API_KEY: {'✓ Set' if openai_key else '✗ Not set'}")
    print(f"  ANTHROPIC_API_KEY: {'✓ Set' if anthropic_key else '✗ Not set'}")
    print()
    
    if not openai_key and not anthropic_key:
        print("⚠️  No API keys found. Set at least one to use the tool.")
        print()


if __name__ == "__main__":
    print_usage_examples()

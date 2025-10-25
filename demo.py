#!/usr/bin/env python3
"""Demo script showing adverstorial output format."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adverstorial.llm_client import LLMClient
from adverstorial.dialogue import AdversarialDialogue


class DemoLLMClient(LLMClient):
    """Demo LLM client that generates pre-written story content."""
    
    def __init__(self, model: str, character: str, responses: list):
        super().__init__(model)
        self.character = character
        self.responses = responses
        self.index = 0
    
    def generate(self, messages):
        """Generate a response from the pre-written list."""
        response = self.responses[self.index % len(self.responses)]
        self.index += 1
        return response


def run_demo():
    """Run a demo story generation."""
    
    # Pre-written protagonist responses
    protagonist_responses = [
        "Detective Nova stepped onto the space station, her neural scanner already picking up anomalies. 'Someone's been tampering with the life support systems,' she muttered.",
        "She examined the control panel, finding molecular traces of exotic matter. 'This wasn't an accident—it's sabotage. And whoever did it knows quantum mechanics.'",
        "Nova's scanner beeped urgently. 'The tampering is active. If I don't stop it in the next ten minutes, the entire station will lose atmosphere.' She sprinted toward the reactor core.",
        "With seconds to spare, she reconfigured the quantum locks. The life support stabilized. 'Got you,' she smiled, recognizing the perpetrator's unique signature in the code."
    ]
    
    # Pre-written antagonist responses
    antagonist_responses = [
        "Dr. Void watched from the shadows, his cybernetic implants gleaming. 'Let her search. She'll never understand the true purpose of my modifications.'",
        "He activated his wrist computer, initiating the next phase. 'Those aren't just sabotage attempts, Detective. They're the key to opening a rift to another dimension.'",
        "The alarms blared as Nova raced toward the core. Void chuckled darkly. 'Too late. Even if she stops this one, she can't stop what's already in motion.'",
        "As the quantum locks engaged, Void vanished in a shimmer of displaced space-time. 'This station was just the beginning, Detective. You've only delayed the inevitable.'"
    ]
    
    print("=" * 80)
    print("ADVERSTORIAL DEMO - Pre-generated Story")
    print("=" * 80)
    print()
    
    # Create demo clients
    protagonist = DemoLLMClient("demo-model", "Protagonist", protagonist_responses)
    antagonist = DemoLLMClient("demo-model", "Antagonist", antagonist_responses)
    
    # Create dialogue system
    dialogue = AdversarialDialogue(
        protagonist_client=protagonist,
        antagonist_client=antagonist,
        prompt="A detective solves a mystery on a space station"
    )
    
    # Run dialogue for 4 rounds
    dialogue.run_dialogue(4)
    
    # Show the formatted story
    print("\n" + "=" * 80)
    print("\n📚 COMPLETE STORY:\n")
    story = dialogue.format_as_story()
    print(story)
    
    print("\n" + "=" * 80)
    print("\nThis is a demo using pre-written content.")
    print("With real API keys, the AI would generate unique stories!")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()

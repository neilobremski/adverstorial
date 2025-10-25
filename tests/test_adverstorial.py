"""Tests for the adverstorial package."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adverstorial.llm_client import LLMClient
from adverstorial.dialogue import AdversarialDialogue


class MockLLMClient(LLMClient):
    """Mock LLM client for testing without API calls."""
    
    def __init__(self, model: str, character_name: str):
        super().__init__(model)
        self.character_name = character_name
        self.call_count = 0
    
    def generate(self, messages):
        """Generate a mock response."""
        self.call_count += 1
        # Return a simple response based on the call count
        return f"{self.character_name} response {self.call_count}: This is a test story segment."


def test_dialogue_creation():
    """Test that dialogue system can be created."""
    protagonist = MockLLMClient("test-model", "Protagonist")
    antagonist = MockLLMClient("test-model", "Antagonist")
    
    dialogue = AdversarialDialogue(
        protagonist_client=protagonist,
        antagonist_client=antagonist,
        prompt="A test story"
    )
    
    assert dialogue.prompt == "A test story"
    assert dialogue.dialogue_history == []
    print("✓ Dialogue creation test passed")


def test_dialogue_rounds():
    """Test that dialogue runs for the correct number of rounds."""
    protagonist = MockLLMClient("test-model", "Protagonist")
    antagonist = MockLLMClient("test-model", "Antagonist")
    
    dialogue = AdversarialDialogue(
        protagonist_client=protagonist,
        antagonist_client=antagonist,
        prompt="A test story"
    )
    
    rounds = 3
    history = dialogue.run_dialogue(rounds)
    
    # Each round should have 2 entries (one from each character)
    assert len(history) == rounds * 2
    
    # Each client should have been called the same number of times
    assert protagonist.call_count == rounds
    assert antagonist.call_count == rounds
    
    print(f"✓ Dialogue rounds test passed ({len(history)} entries for {rounds} rounds)")


def test_story_formatting():
    """Test that story can be formatted from dialogue."""
    protagonist = MockLLMClient("test-model", "Protagonist")
    antagonist = MockLLMClient("test-model", "Antagonist")
    
    dialogue = AdversarialDialogue(
        protagonist_client=protagonist,
        antagonist_client=antagonist,
        prompt="A test story"
    )
    
    dialogue.run_dialogue(2)
    story = dialogue.format_as_story()
    
    # Story should contain the prompt
    assert "A test story" in story
    # Story should contain character labels
    assert "Protagonist" in story or "Antagonist" in story
    # Story should contain the responses
    assert "test story segment" in story
    
    print("✓ Story formatting test passed")


def test_system_prompt_generation():
    """Test that system prompts are generated correctly."""
    protagonist = MockLLMClient("test-model", "Protagonist")
    antagonist = MockLLMClient("test-model", "Antagonist")
    
    dialogue = AdversarialDialogue(
        protagonist_client=protagonist,
        antagonist_client=antagonist,
        prompt="Space adventure"
    )
    
    protagonist_prompt = dialogue._create_system_prompt("protagonist")
    antagonist_prompt = dialogue._create_system_prompt("antagonist")
    
    # Both should contain the story prompt
    assert "Space adventure" in protagonist_prompt
    assert "Space adventure" in antagonist_prompt
    
    # Each should have role-specific content
    assert "protagonist" in protagonist_prompt.lower()
    assert "antagonist" in antagonist_prompt.lower()
    
    print("✓ System prompt generation test passed")


def run_tests():
    """Run all tests."""
    print("=" * 80)
    print("Running Adverstorial Tests")
    print("=" * 80)
    print()
    
    tests = [
        test_dialogue_creation,
        test_dialogue_rounds,
        test_story_formatting,
        test_system_prompt_generation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print()
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

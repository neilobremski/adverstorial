"""Adversarial dialogue system for story generation."""

import random
from typing import List, Dict, Tuple
from .llm_client import LLMClient


class AdversarialDialogue:
    """Manages the adversarial dialogue between protagonist and antagonist."""
    
    def __init__(
        self,
        protagonist_client: LLMClient,
        antagonist_client: LLMClient,
        prompt: str
    ):
        """Initialize the adversarial dialogue system.
        
        Args:
            protagonist_client: LLM client for the protagonist
            antagonist_client: LLM client for the antagonist
            prompt: The story prompt
        """
        self.protagonist_client = protagonist_client
        self.antagonist_client = antagonist_client
        self.prompt = prompt
        self.dialogue_history: List[Dict[str, str]] = []
    
    def _create_system_prompt(self, role: str) -> str:
        """Create the system prompt for a character.
        
        Args:
            role: Either 'protagonist' or 'antagonist'
            
        Returns:
            The system prompt string
        """
        if role == "protagonist":
            return (
                f"You are the protagonist in a story. The story prompt is: {self.prompt}\n"
                "You are engaged in a creative dialogue with the antagonist to build this story. "
                "Each response you give should advance the narrative from the protagonist's perspective. "
                "Keep responses concise (2-4 sentences) and engaging. Build upon what has been said "
                "while adding new story elements."
            )
        else:  # antagonist
            return (
                f"You are the antagonist in a story. The story prompt is: {self.prompt}\n"
                "You are engaged in a creative dialogue with the protagonist to build this story. "
                "Each response you give should advance the narrative from the antagonist's perspective. "
                "Keep responses concise (2-4 sentences) and engaging. Build upon what has been said "
                "while adding new story elements and creating conflict or tension."
            )
    
    def _get_messages_for_character(self, role: str) -> List[Dict[str, str]]:
        """Get the message history formatted for a character.
        
        Args:
            role: Either 'protagonist' or 'antagonist'
            
        Returns:
            List of messages in the format expected by LLM clients
        """
        messages = [{"role": "system", "content": self._create_system_prompt(role)}]
        
        for entry in self.dialogue_history:
            # Map character role to assistant/user for the current character
            if entry["character"] == role:
                messages.append({"role": "assistant", "content": entry["content"]})
            else:
                messages.append({"role": "user", "content": entry["content"]})
        
        return messages
    
    def run_dialogue(self, rounds: int) -> List[Dict[str, str]]:
        """Run the adversarial dialogue for the specified number of rounds.
        
        Args:
            rounds: Number of dialogue rounds (each round has both characters speak)
            
        Returns:
            The complete dialogue history
        """
        # Coin flip to determine who starts
        characters = ["protagonist", "antagonist"]
        random.shuffle(characters)
        first_speaker = characters[0]
        second_speaker = characters[1]
        
        print(f"\n🎲 Coin flip: {first_speaker.capitalize()} goes first!")
        print(f"\n📖 Story Prompt: {self.prompt}\n")
        print("=" * 80)
        
        for round_num in range(rounds):
            print(f"\n--- Round {round_num + 1}/{rounds} ---\n")
            
            # First speaker's turn
            self._character_turn(first_speaker, round_num, rounds)
            
            # Second speaker's turn
            self._character_turn(second_speaker, round_num, rounds)
        
        return self.dialogue_history
    
    def _character_turn(self, character: str, round_num: int, total_rounds: int):
        """Execute a turn for a character.
        
        Args:
            character: Either 'protagonist' or 'antagonist'
            round_num: Current round number (0-indexed)
            total_rounds: Total number of rounds
        """
        client = (
            self.protagonist_client if character == "protagonist"
            else self.antagonist_client
        )
        
        messages = self._get_messages_for_character(character)
        
        # Add context about the round if it's the last round
        if round_num == total_rounds - 1 and len(self.dialogue_history) >= total_rounds * 2 - 1:
            # Last turn - encourage conclusion
            messages.append({
                "role": "user",
                "content": "This is the final exchange. Please bring the story to a satisfying conclusion."
            })
        
        print(f"{character.capitalize()}: ", end="", flush=True)
        response = client.generate(messages)
        print(response)
        
        self.dialogue_history.append({
            "character": character,
            "content": response
        })
    
    def format_as_story(self) -> str:
        """Format the dialogue history as a cohesive story.
        
        Returns:
            The formatted story text
        """
        story_parts = []
        
        story_parts.append(f"# Story: {self.prompt}\n")
        
        for i, entry in enumerate(self.dialogue_history, 1):
            character_label = "🦸 Protagonist" if entry["character"] == "protagonist" else "🦹 Antagonist"
            story_parts.append(f"{character_label}: {entry['content']}\n")
        
        return "\n".join(story_parts)

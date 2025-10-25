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
    
    def _create_system_prompt(self, role: str, round_num: int, total_rounds: int) -> str:
        """Create the system prompt for a character based on the current round.
        
        Args:
            role: Either 'protagonist' or 'antagonist'
            round_num: Current round number (0-indexed)
            total_rounds: Total number of rounds
            
        Returns:
            The system prompt string
        """
        base_intro = f"You are the {role} in a collaborative story creation process. The story prompt is: {self.prompt}\n"
        
        # Round 1: Self-description
        if round_num == 0:
            if role == "protagonist":
                return (
                    base_intro +
                    "In this first round, describe yourself as the protagonist of this story. "
                    "Who are you? What are your motivations, background, and key characteristics? "
                    "Keep it concise (2-4 sentences) but compelling."
                )
            else:
                return (
                    base_intro +
                    "In this first round, describe yourself as the antagonist of this story. "
                    "Who are you? What are your motivations, background, and key characteristics? "
                    "Keep it concise (2-4 sentences) but compelling."
                )
        
        # Round 2: Plot generation
        elif round_num == 1:
            if role == "protagonist":
                return (
                    base_intro +
                    "Based on the character descriptions, propose or enhance the plot of the story. "
                    "What is the main conflict? What events will drive the narrative? "
                    "Build on what the antagonist has proposed if they went first. "
                    "Keep it concise (3-5 sentences)."
                )
            else:
                return (
                    base_intro +
                    "Based on the character descriptions, propose or enhance the plot of the story. "
                    "What is the main conflict? What events will drive the narrative? "
                    "Build on what the protagonist has proposed if they went first. "
                    "Keep it concise (3-5 sentences)."
                )
        
        # Rounds 3 to N-1: Add details and improve
        elif round_num < total_rounds - 1:
            if role == "protagonist":
                return (
                    base_intro +
                    "Add more details to make the protagonist's part of the story more interesting and compelling. "
                    "You can add scenes, character development, or enhance existing plot points. "
                    "Try to make your contribution stand out while maintaining story coherence. "
                    "Keep it concise (3-5 sentences)."
                )
            else:
                return (
                    base_intro +
                    "Add more details to make the antagonist's part of the story more interesting and compelling. "
                    "You can add scenes, character development, or enhance existing plot points. "
                    "Try to make your contribution stand out while maintaining story coherence. "
                    "Keep it concise (3-5 sentences)."
                )
        
        # Final round: Write the complete story
        else:
            if role == "protagonist":
                return (
                    base_intro +
                    "This is the final round. Based on all the character descriptions, plot points, and details shared, "
                    "write the complete short story in narrative form. This should be a cohesive narrative, "
                    "not a dialogue or outline. Tell the story from beginning to end with proper narrative structure. "
                    "Aim for 300-500 words."
                )
            else:
                return (
                    base_intro +
                    "This is the final round. Based on all the character descriptions, plot points, and details shared, "
                    "write the complete short story in narrative form. This should be a cohesive narrative, "
                    "not a dialogue or outline. Tell the story from beginning to end with proper narrative structure. "
                    "Aim for 300-500 words."
                )
    
    def _get_messages_for_character(self, role: str, round_num: int, total_rounds: int) -> List[Dict[str, str]]:
        """Get the message history formatted for a character.
        
        Args:
            role: Either 'protagonist' or 'antagonist'
            round_num: Current round number (0-indexed)
            total_rounds: Total number of rounds
            
        Returns:
            List of messages in the format expected by LLM clients
        """
        messages = [{"role": "system", "content": self._create_system_prompt(role, round_num, total_rounds)}]
        
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
        
        messages = self._get_messages_for_character(character, round_num, total_rounds)
        
        # Describe what's happening in this round
        if round_num == 0:
            round_desc = "Character Description"
        elif round_num == 1:
            round_desc = "Plot Development"
        elif round_num == total_rounds - 1:
            round_desc = "Final Story"
        else:
            round_desc = "Adding Details"
        
        print(f"{character.capitalize()} ({round_desc}): ", end="", flush=True)
        response = client.generate(messages)
        print(response)
        
        self.dialogue_history.append({
            "character": character,
            "content": response,
            "round": round_num
        })
    
    def format_as_story(self) -> str:
        """Format the dialogue history as a cohesive story.
        
        Returns:
            The formatted story text - returns the final story from the last round
        """
        if not self.dialogue_history:
            return "No story generated."
        
        # Find the final story entries (last round)
        final_round = max(entry.get("round", 0) for entry in self.dialogue_history)
        final_stories = [entry for entry in self.dialogue_history if entry.get("round") == final_round]
        
        if final_stories:
            # Return the last final story (second one to speak gets to end)
            story_parts = [f"# Story: {self.prompt}\n"]
            story_parts.append("\n" + final_stories[-1]["content"])
            return "\n".join(story_parts)
        else:
            # Fallback to dialogue format if no final round found
            story_parts = [f"# Story: {self.prompt}\n"]
            for i, entry in enumerate(self.dialogue_history, 1):
                character_label = "🦸 Protagonist" if entry["character"] == "protagonist" else "🦹 Antagonist"
                story_parts.append(f"{character_label}: {entry['content']}\n")
            return "\n".join(story_parts)

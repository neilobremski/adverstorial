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
    
    # Pre-written protagonist responses for each round
    protagonist_responses = [
        # Round 1: Character description
        "I am Captain Elena Nova, an astronaut and investigator sent from Earth. My mission is to explore mysterious balloon-like structures found floating beyond our atmosphere. I'm trained in xenobiology and have a deep curiosity about the unknown.",
        # Round 2: Plot
        "The plot centers on my discovery that the balloons are not natural phenomena but sentient beings. As I attempt to communicate with them, I realize they're being exploited by someone on Earth who wants to weaponize them. I must prevent this while protecting the balloon creatures.",
        # Round 3: Details
        "The balloons communicate through color changes and electromagnetic pulses. I've developed a translation device from spare parts on my ship. One of them, which I call 'Azure,' has bonded with me and shows me visions of their homeworld being destroyed by similar exploitation.",
        # Round 4: Final story
        """Captain Elena Nova floated in the vast darkness beyond Earth's atmosphere, her spacesuit's thrusters keeping her steady as she approached the cluster of iridescent balloons. They weren't weather balloons—she'd known that the moment her scanners picked up their complex energy signatures.

"Hello," she whispered, activating her makeshift translation device. The nearest balloon pulsed with soft blue light—the one she'd started calling Azure.

Back on her ship, Elena had intercepted communications from Titan Industries. They knew about the balloons, had known for weeks, and were preparing to capture them for military experiments. The thought made her sick.

Azure flashed rapidly: amber, violet, crimson. Through her translator, Elena heard fragments of memory—a world of floating cities, peaceful beings of light and gas, and then fire, exploitation, death. The balloons were refugees.

"I won't let them hurt you," Elena promised, but even as she spoke, she saw the corporate ships approaching, their weapons charging. She had minutes to decide: follow orders and return to Earth, or protect these gentle creatures and become a fugitive.

Azure touched her faceplate with a tendril of glowing plasma. In that moment, Elena felt their gratitude, their hope. She smiled and fired up her ship's engines, positioning herself between the balloons and Titan's fleet.

"This is Captain Nova," she broadcast on all channels. "These beings are under my protection. They're not weapons or resources—they're people. And I won't let anyone hurt them."

The standoff lasted hours, but eventually, the corporate ships withdrew. As Elena guided the balloons toward a safe nebula, Azure pulsed a brilliant gold—the color, she'd learned, of joy."""
    ]
    
    # Pre-written antagonist responses for each round
    antagonist_responses = [
        # Round 1: Character description
        "I am Marcus Veil, CEO of Titan Industries and a corporate mogul determined to secure humanity's dominance in space. I see the balloon structures as valuable resources that could revolutionize energy and defense, regardless of their origin or nature.",
        # Round 2: Plot
        "The plot involves my covert operation to capture and study these balloon entities. I've been monitoring them for weeks and have sent Captain Nova on a reconnaissance mission to gather data—though she doesn't know I plan to weaponize her findings. The conflict arises when she discovers my true intentions.",
        # Round 3: Details
        "I've assembled a private military fleet and developed containment technology based on electromagnetic fields. My team has already captured smaller balloon specimens for testing. The data shows they can generate immense energy and could be used as living shields or weapons.",
        # Round 4: Final story
        """Marcus Veil stood in his orbital command center, watching the live feed from his fleet. The balloons were within reach—beautiful, powerful, and worth billions. He'd spent years building Titan Industries into a force that nations feared, and these creatures would cement his legacy.

"Sir, Captain Nova is blocking our approach," his tactical officer reported.

Marcus smiled coldly. He'd chosen Nova precisely because she was idealistic—easy to manipulate, easier to discard. "Send her the override codes. Remind her that her contract with Titan Industries has... clauses."

But when Nova's voice came over the comm, it wasn't what he expected. She was protecting them, calling them people, defying him openly. Marcus's jaw tightened. No one defied him.

"Lieutenant, prepare the EMP nets. We'll take the balloons and deal with Nova later."

As his ships advanced, something unexpected happened. The balloons began to glow in synchronized patterns, and space itself seemed to ripple. Energy readings spiked off the charts. Marcus watched, stunned, as a fleet of larger balloon-entities materialized from a fold in space—the cavalry had arrived.

His ships were disabled in seconds by precise electromagnetic pulses. Not destroyed, but powerless. The message was clear: they could have annihilated him but chose mercy.

Marcus slumped in his chair, watching Nova and the balloons disappear into a shimmering portal. For the first time in decades, he'd been outmaneuvered. The balloons weren't weapons to be captured—they were a civilization that had just demonstrated they could crush humanity if provoked.

In the aftermath, leaked recordings of his operation went viral. Titan Industries' stock crashed. Marcus Veil, once untouchable, faced investigations from every major government. As he sat alone in his office, he realized that perhaps some things in the universe were not meant to be conquered—they were meant to be respected."""
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
        prompt="Balloons in space"
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

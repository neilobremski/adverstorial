"""Command-line interface for Adverstorial."""

import argparse
import sys
from .llm_client import create_client
from .dialogue import AdversarialDialogue


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate short stories using adversarial dialogue between AI characters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with OpenAI for both characters
  adverstorial --prompt "A detective solves a mystery in space" --rounds 3 \\
    --protagonist-system openai --protagonist-model gpt-4 \\
    --antagonist-system openai --antagonist-model gpt-4

  # Mixed systems - OpenAI protagonist, Anthropic antagonist
  adverstorial --prompt "A hero battles a dragon" --rounds 5 \\
    --protagonist-system openai --protagonist-model gpt-4 \\
    --antagonist-system anthropic --antagonist-model claude-3-5-sonnet-20241022

Environment Variables:
  OPENAI_API_KEY      Required if using OpenAI
  ANTHROPIC_API_KEY   Required if using Anthropic
        """
    )
    
    parser.add_argument(
        "--prompt",
        required=True,
        help="The story prompt that sets the theme/premise"
    )
    
    parser.add_argument(
        "--rounds",
        type=int,
        required=True,
        help="Number of dialogue rounds (each round has both characters speak)"
    )
    
    parser.add_argument(
        "--protagonist-system",
        required=True,
        choices=["openai", "anthropic"],
        help="LLM system for the protagonist (openai or anthropic)"
    )
    
    parser.add_argument(
        "--protagonist-model",
        required=True,
        help="Model name for the protagonist (e.g., gpt-4, claude-3-5-sonnet-20241022)"
    )
    
    parser.add_argument(
        "--antagonist-system",
        required=True,
        choices=["openai", "anthropic"],
        help="LLM system for the antagonist (openai or anthropic)"
    )
    
    parser.add_argument(
        "--antagonist-model",
        required=True,
        help="Model name for the antagonist (e.g., gpt-4, claude-3-5-sonnet-20241022)"
    )
    
    parser.add_argument(
        "--output",
        help="Output file path (optional, defaults to stdout)"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Validate rounds
    if args.rounds < 1:
        print("Error: Number of rounds must be at least 1", file=sys.stderr)
        sys.exit(1)
    
    # Warn if rounds is less than recommended minimum
    if args.rounds < 4:
        print(f"⚠️  Warning: You specified {args.rounds} rounds. For best results, use at least 4 rounds:")
        print("   - Round 1: Character descriptions")
        print("   - Round 2: Plot development")
        print("   - Round 3: Detail enhancement")
        print("   - Round 4: Final story")
        print()
    
    try:
        # Create LLM clients
        print(f"🤖 Initializing {args.protagonist_system} protagonist ({args.protagonist_model})...")
        protagonist_client = create_client(args.protagonist_system, args.protagonist_model)
        
        print(f"🤖 Initializing {args.antagonist_system} antagonist ({args.antagonist_model})...")
        antagonist_client = create_client(args.antagonist_system, args.antagonist_model)
        
        # Create dialogue system
        dialogue = AdversarialDialogue(
            protagonist_client=protagonist_client,
            antagonist_client=antagonist_client,
            prompt=args.prompt
        )
        
        # Run the dialogue
        dialogue.run_dialogue(args.rounds)
        
        # Format and output the story
        print("\n" + "=" * 80)
        print("\n📚 COMPLETE STORY:\n")
        story = dialogue.format_as_story()
        print(story)
        
        # Save to file if output path specified
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(story)
            print(f"\n✅ Story saved to: {args.output}")
    
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

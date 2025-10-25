# Adverstorial

AI Story Writer using collaborative story building between a protagonist and antagonist.

## Overview

Adverstorial is a Python CLI program that constructs short stories using AI-powered collaborative creation. The program creates engaging narratives through a structured process where two AI characters (a protagonist and an antagonist) work together through multiple rounds to build a cohesive story:

1. **Round 1**: Both characters describe themselves
2. **Round 2**: They collaboratively develop the plot
3. **Rounds 3 to N-1**: They add details and enhance their parts
4. **Round N**: One generates the complete narrative story

## Features

- 🎲 **Random start**: Coin flip determines which character speaks first (and who writes the final story)
- 🤖 **Flexible AI backends**: Support for both OpenAI and Anthropic models
- 🎭 **Mixed systems**: Use different AI systems for each character
- 📝 **Structured process**: Multi-round collaborative story building
- 📖 **Story output**: Get a complete narrative (not a dialogue)
- ⚙️ **Minimum 4 rounds**: Ensures proper story development through all phases

## Installation

```bash
# Clone the repository
git clone https://github.com/neilobremski/adverstorial.git
cd adverstorial

# Install the package
pip install -e .
```

## Configuration

Set up API keys as environment variables:

```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key"

# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## Usage

### Basic Command Structure

```bash
adverstorial --prompt "Your story prompt" \
  --rounds NUMBER_OF_ROUNDS \
  --protagonist-system SYSTEM \
  --protagonist-model MODEL \
  --antagonist-system SYSTEM \
  --antagonist-model MODEL
```

### Examples

**Example 1: OpenAI for both characters (minimum 4 rounds)**
```bash
adverstorial --prompt "Balloons in space" \
  --rounds 4 \
  --protagonist-system openai \
  --protagonist-model gpt-4 \
  --antagonist-system openai \
  --antagonist-model gpt-4
```

**Example 2: Mixed systems**
```bash
adverstorial --prompt "A hero battles a dragon" \
  --rounds 5 \
  --protagonist-system openai \
  --protagonist-model gpt-4 \
  --antagonist-system anthropic \
  --antagonist-model claude-3-5-sonnet-20241022
```

**Example 3: Save output to file**
```bash
adverstorial --prompt "Time travelers fix paradoxes" \
  --rounds 4 \
  --protagonist-system anthropic \
  --protagonist-model claude-3-5-sonnet-20241022 \
  --antagonist-system anthropic \
  --antagonist-model claude-3-5-sonnet-20241022 \
  --output story.txt
```

### Command-Line Options

- `--prompt`: The story prompt that sets the theme/premise (required)
- `--rounds`: Number of rounds - minimum 4 recommended (required)
  - Round 1: Character descriptions
  - Round 2: Plot development
  - Rounds 3 to N-1: Detail enhancement
  - Round N: Final story writing
- `--protagonist-system`: LLM system for protagonist: `openai` or `anthropic` (required)
- `--protagonist-model`: Model name for protagonist (required)
- `--antagonist-system`: LLM system for antagonist: `openai` or `anthropic` (required)
- `--antagonist-model`: Model name for antagonist (required)
- `--output`: Output file path (optional, defaults to stdout)

### Supported Models

**OpenAI:**
- `gpt-4`
- `gpt-4-turbo`
- `gpt-3.5-turbo`

**Anthropic:**
- `claude-3-5-sonnet-20241022`
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`

## How It Works

1. **Initialization**: The program creates two LLM clients (one for protagonist, one for antagonist)
2. **Coin Flip**: Randomly determines which character speaks first (they also get to write the final story)
3. **Structured Rounds**: 
   - **Round 1**: Both characters describe themselves
   - **Round 2**: Both characters collaborate on plot development
   - **Rounds 3 to N-1**: Characters add details and enhance their contributions
   - **Round N**: The second speaker writes the complete narrative story
4. **Story Output**: The final narrative story is displayed and optionally saved to a file

## License

MIT License - see LICENSE file for details

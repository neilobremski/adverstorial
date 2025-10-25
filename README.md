# Adverstorial

AI Story Writer using adversarial dialogue between a protagonist and antagonist.

## Overview

Adverstorial is a Python CLI program that constructs short stories using AI-powered adversarial dialogue. The program creates engaging narratives by having two AI characters (a protagonist and an antagonist) engage in a back-and-forth dialogue based on a user-provided prompt. 

## Features

- 🎲 **Random start**: Coin flip determines which character speaks first
- 🤖 **Flexible AI backends**: Support for both OpenAI and Anthropic models
- 🎭 **Mixed systems**: Use different AI systems for each character
- 📝 **Automated dialogue**: Characters automatically respond to each other for the specified number of rounds
- 📖 **Story output**: Get a formatted story from the dialogue

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

**Example 1: OpenAI for both characters**
```bash
adverstorial --prompt "A detective solves a mystery in space" \
  --rounds 3 \
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
- `--rounds`: Number of dialogue rounds - each round has both characters speak (required)
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
2. **Coin Flip**: Randomly determines which character speaks first
3. **Dialogue Loop**: For each round:
   - First character generates a response based on the prompt and conversation history
   - Second character responds to the first character's contribution
4. **Story Formation**: The dialogue is formatted into a cohesive story
5. **Output**: The complete story is displayed and optionally saved to a file

## License

MIT License - see LICENSE file for details

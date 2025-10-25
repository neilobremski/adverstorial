# Adverstorial Quick Start Guide

## Installation

```bash
# Install dependencies
pip install openai anthropic

# Or install the package
pip install -e .
```

## Set API Keys

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Basic Usage

```bash
# Run with Python module (minimum 4 rounds recommended)
python3 -m adverstorial.cli \
  --prompt "Your story idea here" \
  --rounds 4 \
  --protagonist-system openai \
  --protagonist-model gpt-4 \
  --antagonist-system openai \
  --antagonist-model gpt-4
```

## Quick Examples

**1. OpenAI Only (4 rounds)**
```bash
python3 -m adverstorial.cli \
  --prompt "Balloons in space" \
  --rounds 4 \
  --protagonist-system openai --protagonist-model gpt-4 \
  --antagonist-system openai --antagonist-model gpt-4
```

**2. Anthropic Only**
```bash
python3 -m adverstorial.cli \
  --prompt "A hero battles a dragon" \
  --rounds 4 \
  --protagonist-system anthropic --protagonist-model claude-3-5-sonnet-20241022 \
  --antagonist-system anthropic --antagonist-model claude-3-5-sonnet-20241022
```

**3. Mixed Systems**
```bash
python3 -m adverstorial.cli \
  --prompt "Time travelers fix paradoxes" \
  --rounds 5 \
  --protagonist-system openai --protagonist-model gpt-4 \
  --antagonist-system anthropic --antagonist-model claude-3-5-sonnet-20241022
```

**4. Save to File**
```bash
python3 -m adverstorial.cli \
  --prompt "Robots gain consciousness" \
  --rounds 4 \
  --protagonist-system openai --protagonist-model gpt-4 \
  --antagonist-system openai --antagonist-model gpt-4 \
  --output story.txt
```

## How It Works

1. 🎲 **Coin Flip**: Randomly determines which character speaks first
2. 🎭 **Character Setup**: Creates protagonist and antagonist with their LLMs
3. 📝 **Round 1**: Both characters describe themselves
4. 📋 **Round 2**: Both characters develop the plot together
5. ✨ **Rounds 3-N-1**: Characters add details and enhance their parts
6. 📖 **Round N**: The second speaker writes the complete story
7. ✅ **Output**: Story displayed on screen (and optionally saved to file)

## Testing

```bash
# Run unit tests
python3 tests/test_adverstorial.py

# Run demo (no API keys needed)
python3 demo.py

# View examples
python3 examples.py
```

## Supported Models

### OpenAI
- `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`

### Anthropic  
- `claude-3-5-sonnet-20241022`
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`

## Tips

- **Rounds**: Minimum 4 rounds required (for all phases of story creation)
- **Prompt**: Be specific but leave room for creativity
- **Models**: Mix different models for varied perspectives
- **Systems**: OpenAI and Anthropic can be mixed freely

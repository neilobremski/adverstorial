#!/usr/bin/env bash
# Shell script run by cron to execute the adverstorial.py script
# using wordlists stored in the parent directory.

# get current directory of the script
ADVERSTORIAL_DIR="$(cd "$(dirname "$0")" && pwd)"
WORDLISTS_DIR="$ADVERSTORIAL_DIR/wordlists"
echo "Wordlists directory: $WORDLISTS_DIR"

# for loop 5 times to generate 5 words
prompt="$1"
if [ -n "$prompt" ]; then
  echo "Using prompt from first argument: $prompt"
else
  echo "Generating prompt from random words"
  for i in {1..5}; do
    # pick a random file from the wordlists directory
    WORDLIST_FILE=$(find "$WORDLISTS_DIR" -type f | shuf -n 1)

    # pick a random word from the selected file
    RANDOM_WORD=$(shuf -n 1 "$WORDLIST_FILE")

    if [ -z "$prompt" ]; then
      prompt="$RANDOM_WORD"
    else
      prompt="$prompt $RANDOM_WORD"
    fi
  done
fi
echo "Prompt: $prompt"

if [ -n "$ADVERSARIES" ]; then
  # pick adversaries from ADVERSARIES env var if set (as comma-separated list)
  IFS=',' read -r -a adversaries_array <<< "$ADVERSARIES"
  protagonist=${adversaries_array[$RANDOM % ${#adversaries_array[@]}]}
  antagonist=${adversaries_array[$RANDOM % ${#adversaries_array[@]}]}
else
  # pick random antagonist and protagonist from $ADVERSTORIAL_DIR/adversaries.txt file
  protagonist=$(shuf -n 1 "$ADVERSTORIAL_DIR/adversaries.txt")
  antagonist=$(shuf -n 1 "$ADVERSTORIAL_DIR/adversaries.txt")
fi
echo "Protagonist: $protagonist"
echo "Antagonist: $antagonist"

# pick a random temperature between 0.1 and 0.8
temperature=$(awk -v min=0.1 -v max=0.8 'BEGIN{srand(); print sprintf("%.1f", min+rand()*(max-min))}')

# pick a random number of rounds between 2 and 4
rounds=$(shuf -i 2-4 -n 1)

# echo "Generated words: $words"
python3 "$ADVERSTORIAL_DIR/python-cli/adverstorial.py" "$prompt" \
  --antagonist "$antagonist" \
  --protagonist "$protagonist" \
  --temperature "$temperature" \
  --rounds "$rounds"

# if "ADVERSTORIAL_DIR" is a git repo and on branch "main" then pull latest
if [ -d "$ADVERSTORIAL_DIR/.git" ]; then
  cd "$ADVERSTORIAL_DIR" || exit
  current_branch=$(git rev-parse --abbrev-ref HEAD)
  if [ "$current_branch" = "main" ]; then
    echo "On main branch, pulling latest changes"
    git pull origin main
  fi
fi

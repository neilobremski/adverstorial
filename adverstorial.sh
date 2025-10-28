#!/usr/bin/env bash
# Shell script run by cron to execute the adverstorial.py script
# using wordlists stored in the parent directory.

# get current directory of the script
ADVERSTORIAL_DIR="$(cd "$(dirname "$0")" && pwd)"

# for loop 5 times to generate 5 words
prompt="$1"
if [ -n "$prompt" ]; then
  echo "Using prompt from first argument: $prompt"
else
  echo "Generating prompt from random words"
  prompt="$($ADVERSTORIAL_DIR/seed-prompt.sh)"
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

rounds=$ROUNDS
if [ -n "$ROUNDS" ]; then
  echo "Using rounds from ROUNDS env var"
else
  echo "Picking random number of rounds between 2 and 4"
  rounds=$(shuf -i 2-4 -n 1)
fi
echo "Rounds: $rounds"

pushd "$ADVERSTORIAL_DIR/python-cli" || exit
python3 "adverstorial.py" "$prompt" \
  --antagonist "$antagonist" \
  --protagonist "$protagonist" \
  --temperature "$temperature" \
  --rounds "$rounds"
popd || exit

# if "ADVERSTORIAL_DIR" is a git repo and on branch "main" then pull latest
if [ -d "$ADVERSTORIAL_DIR/.git" ]; then
  cd "$ADVERSTORIAL_DIR" || exit
  current_branch=$(git rev-parse --abbrev-ref HEAD)
  if [ "$current_branch" = "main" ]; then
    echo "On main branch, pulling latest changes"
    git pull origin main
  fi
fi

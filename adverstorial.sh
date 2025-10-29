#!/usr/bin/env bash
# Shell script run by cron to execute the adverstorial.py script
# using wordlists stored in the parent directory.

# get current directory of the script
ADVERSTORIAL_DIR="$(cd "$(dirname "$0")" && pwd)"

# check for .env and load it if it exists
ENV_FILE="${ENV_FILE:-$ADVERSTORIAL_DIR/.env}"
if [ -f "$ENV_FILE" ]; then
  echo "Using environment file: $ENV_FILE"
  set -a # Enable automatic export of variables
  source "$ENV_FILE"
  set +a # Disable automatic export of variables
fi

# for loop 5 times to generate 5 words
prompt="$1"
if [ -n "$prompt" ]; then
  echo "Using prompt from first argument: $prompt"
else
  echo "Generating prompt from random words"
  prompt="$($ADVERSTORIAL_DIR/seed-prompt.sh)"
fi
echo "Prompt: $prompt"

protagonist="${PROTAGONIST}"
antagonist="${ANTAGONIST}"
if [ -n "$ADVERSARIES" ]; then
  # pick adversaries from ADVERSARIES env var if set (as comma-separated list)
  IFS=',' read -r -a adversaries_array <<< "$ADVERSARIES"
  protagonist=${protagonist:-adversaries_array[$RANDOM % ${#adversaries_array[@]}]}
  antagonist=${antagonist:-adversaries_array[$RANDOM % ${#adversaries_array[@]}]}
else
  # pick random antagonist and protagonist from $ADVERSTORIAL_DIR/adversaries.txt file
  protagonist=${protagonist:-$(sort -R "$ADVERSTORIAL_DIR/adversaries.txt" | head -n 1)}
  antagonist=${antagonist:-$(sort -R "$ADVERSTORIAL_DIR/adversaries.txt" | head -n 1)}
fi
echo "Protagonist: $protagonist"
echo "Antagonist: $antagonist"

# pick a random temperature between 0.1 and 0.8
temperature=$(awk -v min=0.1 -v max=0.8 'BEGIN{srand(); print sprintf("%.6f", min+rand()*(max-min))}')

rounds=$ROUNDS
if [ -n "$ROUNDS" ]; then
  echo "Using rounds from ROUNDS env var"
else
  echo "Picking random number of rounds between 2 and 4"
  rounds=$(seq 2 4 | sort -R | head -n 1)
fi
echo "Rounds: $rounds"

if [ "$BLOB_STORAGE_TOKEN" = "auto" ]; then
  echo "Obtaining BLOB_STORAGE_TOKEN using az CLI"
  export BLOB_STORAGE_TOKEN="$(az account get-access-token --resource https://storage.azure.com/ --query accessToken -o tsv)"
fi

pushd "$ADVERSTORIAL_DIR" || exit
python3 "adverstorial.py" "$prompt" \
  --antagonist "$antagonist" \
  --protagonist "$protagonist" \
  --temperature "$temperature" \
  --rounds "$rounds"
exit_code=$?
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

if [ $exit_code -ne 0 ]; then
  echo "adverstorial.py exited with code $exit_code"
  exit $exit_code
else
  echo "adverstorial.py completed successfully"
fi

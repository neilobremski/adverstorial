#!/usr/bin/env bash
# Generate a random seed prompt using wordlists

# get current directory of the script
ADVERSTORIAL_DIR="$(cd "$(dirname "$0")" && pwd)"
WORDLISTS_DIR="$ADVERSTORIAL_DIR/wordlists"
echo "Wordlists directory: $WORDLISTS_DIR" >&2

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

echo "$prompt"

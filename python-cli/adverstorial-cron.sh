#!/usr/bin/env bash
# Shell script run by cron to execute the adverstorial.py script
# using wordlists stored in the parent directory.

# get current directory of the script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
WORDLISTS_DIR="$PARENT_DIR/wordlists"
echo "Wordlists directory: $WORDLISTS_DIR"

# for loop 5 times to generate 5 words
words=""
for i in {1..5}; do
  # pick a random file from the wordlists directory
  WORDLIST_FILE=$(find "$WORDLISTS_DIR" -type f | shuf -n 1)

  # pick a random word from the selected file
  RANDOM_WORD=$(shuf -n 1 "$WORDLIST_FILE")

  if [ -z "$words" ]; then
    words="$RANDOM_WORD"
  else
    words="$words $RANDOM_WORD"
  fi
done

# pick random antagonist and protagonist from $PARENT_DIR/adversaries.txt file
protagonist=$(shuf -n 1 "$PARENT_DIR/adversaries.txt")
antagonist=$(shuf -n 1 "$PARENT_DIR/adversaries.txt")

# pick a random temperature between 0.1 and 0.8
temperature=$(awk -v min=0.1 -v max=0.8 'BEGIN{srand(); print sprintf("%.1f", min+rand()*(max-min))}')

# pick a random number of rounds between 2 and 4
rounds=$(shuf -i 2-4 -n 1)

# echo "Generated words: $words"
python3 "$SCRIPT_DIR/adverstorial.py" "$words" \
  --antagonist "$antagonist" \
  --protagonist "$protagonist" \
  --temperature "$temperature" \
  --rounds "$rounds"

# get latest code (after running so that any changes don't affect this run)
pushd "$PARENT_DIR"; git pull; popd

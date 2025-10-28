#!/usr/bin/env bash
# Generate a random seed prompt using wordlists
ADVERSTORIAL_DIR="$(cd "$(dirname "$0")" && pwd)"
WORDLISTS_DIR="$ADVERSTORIAL_DIR/wordlists"
max_words=${1:-5}
words=$(cat $ADVERSTORIAL_DIR/wordlists/*.txt | shuf | head -n $max_words)
prompt=$(echo "$words" | tr '\n' ' ' | sed 's/ $//')
echo "$prompt"

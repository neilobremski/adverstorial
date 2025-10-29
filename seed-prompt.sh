#!/usr/bin/env bash
# Generate a random seed prompt using wordlists
ADVERSTORIAL_DIR="$(cd "$(dirname "$0")" && pwd)"
WORDLISTS_DIR="$ADVERSTORIAL_DIR/wordlists"
max_words=${1:-5}

# shuf is not available on macOS by default, so using sort -R as an alternative
# (Linux has sort -R as part of GNU coreutils)

words=$(cat $ADVERSTORIAL_DIR/wordlists/*.txt | sort -R | head -n $max_words)
prompt=$(echo "$words" | tr '\n' ' ' | sed 's/ $//')
echo "$prompt"

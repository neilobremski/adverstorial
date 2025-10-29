#!/usr/bin/env bash
# Generate a random seed prompt using wordlists
ADVERSTORIAL_DIR="$(cd "$(dirname "$0")" && pwd)"
WORDLISTS_DIR="$ADVERSTORIAL_DIR/wordlists"

# shuf is not available on macOS by default, so using sort -R as an alternative
# (Linux has sort -R as part of GNU coreutils)
function random_word() {
  sort -R $1 | head -n 1
}

pushd "$WORDLISTS_DIR" > /dev/null || exit 1
random_word1=$(random_word "*.txt")
random_word2=$(random_word "*.txt")
adjective="$(random_word "adjectives.csv" | cut -d',' -f1)"
noun1="$(random_word "nouns.csv" | cut -d',' -f1)"
noun2="$(random_word "nouns.csv" | cut -d',' -f1)"
adverb="$(random_word "adverbs.csv" | cut -d',' -f1)"
verb="$(sort -R verbs.csv | head -n 1 | cut -d',' -f1)"
popd > /dev/null || exit 1

prompt="${random_word1} ${adjective} ${noun1} ${adverb} ${verb} ${noun2} ${random_word2}"

# replace \t\r\n with single spaces and trim multiple spaces
prompt=$(echo "$prompt" | tr '\t\r\n' ' ' | tr -s ' ')

echo "$prompt"

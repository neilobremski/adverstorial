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

# parse all arguments started with -- and set those as variables
# if it includes = then set that as the value, otherwise set to true
prompt=""
for arg in "$@"; do
  if [[ "$arg" == --* ]]; then
    key="${arg%%=*}"
    key="${key#--}"
    if [[ "$arg" == *=* ]]; then
      value="${arg#*=}"
    else
      value=true
    fi
    export "$key"="$value"
    echo "Set variable from argument: $key=$value"
  elif [ -z "$prompt" ]; then
    prompt="$arg"
  else
    prompt="$prompt $arg"
  fi
done
if [ -z "$prompt" ]; then
  prompt="$PROMPT"
fi

# use specified prompt or generate one
if [ -n "$prompt" ]; then
  echo "Using prompt from first argument: $prompt"
else
  echo "Generating prompt from random words"
  prompt="$($ADVERSTORIAL_DIR/seed-prompt.sh)"
fi
echo "Prompt: $prompt"

build_list_from_env() {
  local env_name="$1"
  local array_name="$2"
  local raw_value="${!env_name}"
  local -a items=()
  if [ -n "$raw_value" ]; then
    IFS=',' read -r -a items <<< "$raw_value"
  fi
  local filtered=()
  for entry in "${items[@]}"; do
    local trimmed="${entry#"${entry%%[![:space:]]*}"}"
    trimmed="${trimmed%"${trimmed##*[![:space:]]}"}"
    if [ -n "$trimmed" ]; then
      filtered+=("$trimmed")
    fi
  done
  eval "$array_name=(\"\${filtered[@]}\")"
}

protagonist="${PROTAGONIST}"
antagonist="${ANTAGONIST}"
build_list_from_env "PROTAGONISTS" protagonists_array
build_list_from_env "ANTAGONISTS" antagonists_array
build_list_from_env "ADVERSARIES" adversaries_array

if [ -z "$protagonist" ]; then
  if [ "${#protagonists_array[@]}" -gt 0 ]; then
    random_protagonist=${protagonists_array[$RANDOM % ${#protagonists_array[@]}]}
    protagonist=$random_protagonist
    echo "Random protagonist selected from \$PROTAGONISTS: $protagonist"
  elif [ "${#adversaries_array[@]}" -gt 0 ]; then
    random_protagonist=${adversaries_array[$RANDOM % ${#adversaries_array[@]}]}
    protagonist=$random_protagonist
    echo "Random protagonist selected from \$ADVERSARIES: $protagonist"
  else
    echo "No protagonist sources configured; set PROTAGONIST, PROTAGONISTS, or ADVERSARIES env vars"
    exit 1
  fi
fi

if [ -z "$antagonist" ]; then
  if [ "${#antagonists_array[@]}" -gt 0 ]; then
    random_antagonist=${antagonists_array[$RANDOM % ${#antagonists_array[@]}]}
    antagonist=$random_antagonist
    echo "Random antagonist selected from \$ANTAGONISTS: $antagonist"
  elif [ "${#adversaries_array[@]}" -gt 0 ]; then
    random_antagonist=${adversaries_array[$RANDOM % ${#adversaries_array[@]}]}
    antagonist=$random_antagonist
    echo "Random antagonist selected from \$ADVERSARIES: $antagonist"
  else
    echo "No antagonist sources configured; set ANTAGONIST, ANTAGONISTS, or ADVERSARIES env vars"
    exit 1
  fi
fi

echo "Protagonist: $protagonist"
echo "Antagonist: $antagonist"

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
  --rounds "$rounds"
exit_code=$?
popd || exit

if [ $exit_code -ne 0 ]; then
  exit $exit_code
fi

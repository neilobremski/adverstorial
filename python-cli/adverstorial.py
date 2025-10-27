import argparse
from dataclasses import dataclass
import json
import os
import random
import requests
import dotenv
from urllib.parse import urljoin

dotenv.load_dotenv()

# get main directory as one level up from this one
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAYI_PROXY_URL = os.environ["PAYI_PROXY_URL"]

MAX_OUTPUT_TOKENS = int(os.environ.get("MAX_OUTPUT_TOKENS", "5000"))
REASONING_EFFORT = os.environ.get("REASONING_EFFORT", "minimal")

# read instructions from the "## Instructions" section of README.md
instructions = ""
with open(os.path.join(BASE_DIR, "README.md"), "r") as f:
  lines = f.readlines()
  in_instructions = False
  for line in lines:
    if line.startswith("## Instructions"):
      in_instructions = True
      continue
    if in_instructions:
      if line.startswith("# ") or line.startswith("## "):
        break
      instructions += line

print(instructions)

@dataclass(frozen=True)
class Role:
  provider: str
  model: str
  type: str  # either "protagonist" or "antagonist"

def parse_role(value: str, type: str) -> Role:
  provider, sep, model = value.partition(".")
  if not sep or not provider or not model:
    raise argparse.ArgumentTypeError("expected PROVIDER.MODEL (e.g., openai.gpt-5)")
  role = Role(provider=provider, model=model, type=type)
  return role


def game_loop(prompt, protagonist: Role, antagonist: Role, rounds: int):
  order = [protagonist, antagonist]
  random.shuffle(order)
  current_story = ""
  # generate a new UUID for this game session
  game_id = os.urandom(16).hex()

  # loop through each round
  for round_num in range(1, rounds + 1):
    print("")
    print(f"--- Round {round_num} ---")

    for role in order:
      print("")
      print(f"Round {round_num} {role.type.capitalize()}'s turn:")
      current_prompt = current_story or f"""You are writing on the side of the {role.type} and
      you won the coin toss so you go first: {prompt}"""
      current_story = write_story(role, current_prompt, id=game_id)
      print(current_story)

def write_story(role: Role, prompt: str, id: str = "") -> str:
  # combine PAYI_PROXY_URL with role.provider using proper URL joining
  
  if role.provider == "openai":
    proxy_url = urljoin(PAYI_PROXY_URL, os.path.join(role.provider, "v1/responses"))
    headers = {
      "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']} {os.environ['PAYI_API_KEY']}",
      "Content-Type": "application/json",
      "xProxy-UseCase-Name": "Story",
    }
    if id:
      headers["xProxy-UseCase-ID"] = id
    request = {
      "input": prompt,
      "instructions": instructions,
      "model": role.model,
      "max_output_tokens": MAX_OUTPUT_TOKENS,
      "reasoning": {
        "effort": REASONING_EFFORT,
      }
    }
    # curl $proxy_url -H "Content-Type: application/json" -d "${request_json}"
    response = requests.post(proxy_url, headers=headers, json=request)
    json_response = response.json()
    if response.status_code == 200:
      return deep_string(json_response, "text")
    else:
      raise Exception(f"Error {response.status_code}: {response.text}")
  else:
    raise NotImplementedError(f"Provider {role.provider} is not implemented yet.")

def deep_string(obj, key):
  """Recursively search for all string properties with the given key in a nested dict/list structure and concatenate them."""
  result = ""
  if isinstance(obj, dict):
    for k, v in obj.items():
      if k == key and isinstance(v, str):
        result += v
      result += deep_string(v, key)
  elif isinstance(obj, list):
    for item in obj:
      result += deep_string(item, key)
  return result

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("prompt", nargs="?", help="Prompt for the game loop")
  parser.add_argument("--prompt", dest="prompt_arg", help="Prompt for the game loop")
  parser.add_argument(
      "--protagonist",
      "-P",
      required=True,
      type=lambda v: parse_role(v, "protagonist"),
      metavar="PROVIDER.MODEL",
      help="Protagonist provider/model (e.g., openai.gpt-5)",
  )
  parser.add_argument(
      "--antagonist",
      "-A",
      required=True,
      type=lambda v: parse_role(v, "antagonist"),
      metavar="PROVIDER.MODEL",
      help="Antagonist provider/model (e.g., anthropic.claude-3-opus)",
  )
  parser.add_argument(
      "--rounds",
      "-r",
      type=int,
      default=1,
      help="Number of rounds to play (default: 1)",
  )
  parsed = parser.parse_args()

  prompt = parsed.prompt_arg if parsed.prompt_arg is not None else parsed.prompt
  if prompt is None or prompt == "":
    parser.error("the following arguments are required: prompt")

  if parsed.rounds is None or parsed.rounds <= 0:
    parser.error("rounds must be a positive integer")

  game_loop(prompt, parsed.protagonist, parsed.antagonist, parsed.rounds)

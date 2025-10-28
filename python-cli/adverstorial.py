import argparse
from dataclasses import dataclass
import json
import os
import logging
import random
import uuid
import requests
import re
import dotenv
from urllib.parse import urljoin
from typing import Optional, List

dotenv.load_dotenv()
logger = logging.getLogger(__name__)

# get main directory as one level up from this one
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAYI_PROXY_URL = os.environ["PAYI_PROXY_URL"]

MAX_OUTPUT_TOKENS = int(os.environ.get("MAX_OUTPUT_TOKENS", "5000"))
REASONING_EFFORT = os.environ.get("REASONING_EFFORT", "minimal")
ROUNDS = int(os.environ.get("ROUNDS", "1"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.7"))
DEFAULT_PROTAGONIST = os.environ.get("PROTAGONIST", "openai.gpt-5")
DEFAULT_ANTAGONIST = os.environ.get("ANTAGONIST", "anthropic.claude-3-opus")

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


@dataclass(frozen=True)
class Story:
  title: str
  content: str
  lines: List[str]
  def __str__(self):
    return f"Title: {self.title}\n\n{self.content}\n\nThe End\n"

def parse_role(value: str, type: str) -> Role:
  provider, sep, model = value.partition(".")
  if not sep or not provider or not model:
    raise argparse.ArgumentTypeError("expected PROVIDER.MODEL (e.g., openai.gpt-5)")
  role = Role(provider=provider, model=model, type=type)
  return role


def parse_story(raw: str) -> Optional[Story]:
  """Look for a line starting with 'Title:' and then a line ending with 'The End'. Everything in between is the content."""
  if not raw:
    return None
  lines = raw.strip().splitlines()
  if not lines:
    logger.warning("No lines found in story")
    return None

  # find first line starting with "Title:" (case-insensitive, may have preceding MD code)
  bi = 0
  while bi < len(lines) and not re.match(r"^[^\w]*title:", lines[bi], re.IGNORECASE):
    bi += 1
  if bi == len(lines):
    logger.warning("No title found in story")
    return None

  # find first line after Title that is "The End"
  # this should match "The End" or "the end" or "**The End**" etc.
  ei = bi + 1
  while ei < len(lines) and not re.match(r"^[^\w]*the end[\w]*$", lines[ei], re.IGNORECASE):
    ei += 1
  if ei == len(lines):
    logger.warning("No 'The End' found in story")
    return None

  # verify that there is at least 1 line of content between Title and The End
  if ei - bi < 2:
    logger.warning("No content found in story")
    return None

  title = lines[bi].strip()[len("Title:"):].strip()
  content = "\n".join(lines[bi + 1 : ei]).strip()
  return Story(title=title, content=content, lines=lines)


def game_loop(prompt, protagonist: Role, antagonist: Role, rounds: int):
  global instructions
  order = [protagonist, antagonist]
  random.shuffle(order)
  story: Optional[Story] = None
  game_id = uuid.uuid4().hex

  for round_num in range(1, rounds + 1):
    for role in order:
      logger.info("")
      logger.info(f"### Round {round_num} of {rounds} / Turn {order.index(role) + 1} of 2")

      other_role = order[1] if role == order[0] else order[0]
      current = [
        f"* Coin toss winner: {order[0].type}",
        f"* Seed prompt: {prompt}",
        f"* It is round {round_num} of {rounds}.",
        f"* I am writing on the side of the {other_role.type}.",
        f"* You are writing on the side of the {role.type}.",
      ]

      if story:
        current.append(f"* Story Title: {story.title}")
      if round_num > 1:
        current.append("* Previous round data has been truncated for brevity.")

      if not story:
        request = f"You won the coin toss so you go first: {prompt}"
      else:
        request = str(story)

      kwargs = {
        "role": role,
        "message": "\n".join(current) + "\n\n" + request,
        "id": game_id,
        "instructions": instructions,
      }

      print(kwargs["message"])

      response = write_story(**kwargs)
      print(response)
      new_story = parse_story(response)
      if not new_story:
        logger.warning("Failed to parse story output, retrying...")
        response = write_story(**kwargs)
        print(response)
        new_story = parse_story(response)
      if not new_story:
        raise ValueError("Failed to parse story output after two attempts")
      story = new_story

  return story
    

def write_story(role: Role, message: str, id: str = "", instructions: str = "") -> str:
  temperature = TEMPERATURE + (random.random() * (TEMPERATURE / 100)) - (random.random() * (TEMPERATURE / 100))

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
      "input": message,
      "instructions": instructions,
      "model": role.model,
      "max_output_tokens": MAX_OUTPUT_TOKENS,
      "temperature": temperature,
    }
    if role.model.startswith("gpt-5") or role.model.startswith("o"):
      request["reasoning"] = {"effort": REASONING_EFFORT}
  elif role.provider == "anthropic":
    proxy_url = urljoin(PAYI_PROXY_URL, os.path.join(role.provider, "v1/messages"))
    headers = {
      "anthropic-version": "2023-06-01",
      "Content-Type": "application/json",
      "x-api-key": f"Bearer {os.environ['ANTHROPIC_API_KEY']} {os.environ['PAYI_API_KEY']}",
      "xProxy-UseCase-Name": "Story",
    }
    if id:
      headers["xProxy-UseCase-ID"] = id
    request = {
      "model": role.model,
      "max_tokens": MAX_OUTPUT_TOKENS,
      "temperature": temperature,
      "system": instructions,
      "messages": [
        {
          "role": "user",
          "content": message,
        }
      ],
    }
  else:
    raise NotImplementedError(f"Provider {role.provider} is not implemented yet.")

  try:
    response = requests.post(proxy_url, headers=headers, json=request)
  except Exception as e:
    logger.error(f"Error making request to {proxy_url}: {e}")
    return ""
  logger.info(f"Response status code: {response.status_code}: {response.text}")

  try:
    json_response = response.json()
  except Exception as e:
    logger.error(f"Error decoding JSON response: {response.text} ({e})")
    return ""

  if response.status_code != 200:
    logger.error(f"Error {response.status_code}: {response.text}")
    return ""

  return deep_string(json_response, "text")


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
      type=lambda v: parse_role(v, "protagonist"),
      metavar="PROVIDER.MODEL",
      help=f"Protagonist provider/model (default: ${DEFAULT_PROTAGONIST})",
  )
  parser.add_argument(
      "--antagonist",
      "-A",
      type=lambda v: parse_role(v, "antagonist"),
      metavar="PROVIDER.MODEL",
      help=f"Antagonist provider/model (default: ${DEFAULT_ANTAGONIST})",
  )
  parser.add_argument(
      "--rounds",
      "-r",
      type=int,
      default=ROUNDS,
      help=f"Number of rounds to play (default: ${ROUNDS})",
  )
  parser.add_argument(
      "--max-output-tokens",
      type=int,
      dest="max_output_tokens",
      help=f"Override maximum output tokens (default: ${MAX_OUTPUT_TOKENS})",
  )
  parser.add_argument(
      "--reasoning-effort",
      dest="reasoning_effort",
      help=f"Override reasoning effort level (default: ${REASONING_EFFORT})",
  )
  parser.add_argument(
      "--temperature",
      type=float,
      default=TEMPERATURE,
      dest="temperature",
      help=f"Override sampling temperature (default: ${TEMPERATURE})",
  )
  parsed = parser.parse_args()

  prompt = parsed.prompt_arg if parsed.prompt_arg is not None else parsed.prompt
  if prompt is None or prompt == "":
    parser.error("the following arguments are required: prompt")

  if parsed.rounds is None or parsed.rounds <= 0:
    parser.error("rounds must be a positive integer")

  if parsed.max_output_tokens is not None:
    if parsed.max_output_tokens <= 0:
      parser.error("max-output-tokens must be a positive integer")
    MAX_OUTPUT_TOKENS = parsed.max_output_tokens
  if parsed.reasoning_effort is not None:
    REASONING_EFFORT = parsed.reasoning_effort
  if parsed.temperature is not None:
    TEMPERATURE = parsed.temperature

  try:
    protagonist = parsed.protagonist or parse_role(DEFAULT_PROTAGONIST, "protagonist")
  except argparse.ArgumentTypeError as exc:
    parser.error(f"invalid default protagonist: {exc}")
  try:
    antagonist = parsed.antagonist or parse_role(DEFAULT_ANTAGONIST, "antagonist")
  except argparse.ArgumentTypeError as exc:
    parser.error(f"invalid default antagonist: {exc}")

  game_loop(prompt, protagonist, antagonist, parsed.rounds)

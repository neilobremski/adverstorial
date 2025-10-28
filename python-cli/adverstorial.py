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
PAYI_API_URL = os.environ.get("PAYI_API_URL", "")
PAYI_PROXY_URL = os.environ["PAYI_PROXY_URL"]
if not PAYI_API_URL:
  from urllib.parse import urlparse
  parsed_url = urlparse(PAYI_PROXY_URL)
  PAYI_API_URL = f"{parsed_url.scheme}://{parsed_url.netloc.replace('developer.', 'api.')}/"

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


def parse_marker_line(line: str, marker: str) -> Optional[str]:
  """Extract a marked value from a markdown line. Returns None if not found.
  Examples:
  parse_marker_line("```Title: My Story```", "Title") -> "My Story"
  parse_marker_line("`Title: My Story`", "Title") -> "My Story"
  parse_marker_line("## Title: My Story", "Title") -> "My Story"
  """
  pattern = rf"^[^\w]*{re.escape(marker)}[^\w]*(.*?)[^\w]*$"
  match = re.match(pattern, line, re.IGNORECASE)
  if match:
    return match.group(1).strip()
  return None

def parse_story(raw: str) -> Optional[Story]:
  """Look for a line starting with 'Title:' and then a line ending with 'The End'. Everything in between is the content."""
  if not raw:
    return None
  lines = raw.strip().splitlines()
  if not lines:
    logger.warning("No lines found in story")
    return None

  # find the line for "Title:"
  # (case-insensitive, may be wrapped in markdown code characters)
  bi = 0
  title = None
  while bi < len(lines):
    title = parse_marker_line(lines[bi], "Title")
    bi += 1
    if title:
      break
  if not title:
    logger.warning("No title found in story")
    return None

  # find the line for "The End"
  # (case-insensitive, may be wrapped in markdown code characters)
  ei = bi
  the_end = None
  while ei < len(lines):
    the_end = parse_marker_line(lines[ei], "The End")
    ei += 1
    if the_end is not None:
      break

  if the_end is None:
    logger.warning("No 'The End' found in story")
    return None

  content = "\n".join(lines[bi : ei]).strip()
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
    }
    if role.model.startswith("gpt-5") or role.model.startswith("o"):
      request["reasoning"] = {"effort": REASONING_EFFORT}
    else:
      request["temperature"] = temperature
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

  if response.status_code != 200:
    logger.error(f"Error {response.status_code}: {response.text}")
    return ""

  try:
    json_response = response.json()
  except Exception as e:
    logger.error(f"Error decoding JSON response: {response.text} ({e})")
    return ""

  request_id = parse_request_id(role, json_response)
  if request_id:
    add_property(request_id, "role", role.type)

  return deep_string(json_response, "text")


def payi(uri, json_body=None, method=None):
  """Call Pay-i API with the given URI."""
  url = urljoin(PAYI_API_URL, uri)
  headers = {
    "accept": "application/json",
    "xProxy-api-key": os.environ["PAYI_API_KEY"],
  }
  if method is None:
    method = "PUT" if json_body is not None else "GET"
  response = requests.request(method, url, headers=headers, json=json_body)
  if response.status_code != 200:
    logger.error(f"Error {response.status_code}: {response.text}")
    return None
  try:
    return response.json()
  except Exception as e:
    logger.error(f"Error decoding JSON response: {response.text} ({e})")
    return None


def parse_request_id(role, json_response):
  """Parse the request ID from the JSON response."""
  provider_response_id = deep_string(json_response, "id")
  # GET /api/v1/requests/provider/{category}/{provider_response_id}/result
  r = payi(f"api/v1/requests/provider/system.{role.provider}/{provider_response_id}/result")
  if r is None:
    return None
  return deep_string(r, "request_id")


def add_property(request_id, key, value):
  """Add Pay-i Request property based on ID in the response JSON."""
  # PUT /api/v1/requests/{request_id}/properties
  payi(f"api/v1/requests/{request_id}/properties", json_body={
    "properties": {
      key: value
    }
  }, method="PUT")


def deep_list(obj, key):
  """Recursively search for all string properties with the given key in a nested dict/list structure and concatenate them."""
  result = []
  if isinstance(obj, dict):
    for k, v in obj.items():
      if k == key and isinstance(v, str):
        result.append(v)
      result.extend(deep_list(v, key))
  elif isinstance(obj, list):
    for item in obj:
      result.extend(deep_list(item, key))
  return result

def deep_string(obj, key, max=1) -> str:
  """Recursively search for all string properties with the given key in a nested dict/list structure and concatenate them."""
  a = deep_list(obj, key)
  keep = []
  for s in a:
    if s:
      keep.append(s)
      max -= 1
      if max == 0:
        break
  return "".join(keep)

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

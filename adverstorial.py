import argparse
import cast_str
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
import logging
import random
import uuid
import requests
import re
from urllib.parse import urljoin
from typing import Optional, List

# if python-dotenv is installed, load .env file
try:
  import dotenv
  dotenv.load_dotenv()
except ImportError:
  pass

logger = logging.getLogger(__name__)

# get main directory as one level up from this one
ADVERSTORIAL_DIR = os.path.dirname(os.path.abspath(__file__))
PAYI_API_URL = os.environ.get("PAYI_API_URL", "")
PAYI_PROXY_URL = os.environ["PAYI_PROXY_URL"]
if not PAYI_API_URL:
  from urllib.parse import urlparse
  parsed_url = urlparse(PAYI_PROXY_URL)
  PAYI_API_URL = f"{parsed_url.scheme}://{parsed_url.netloc.replace('developer.', 'api.')}/"

MAX_OUTPUT_TOKENS = cast_str.to_int(os.environ.get("MAX_OUTPUT_TOKENS", "5000"))
REASONING_EFFORT = os.environ.get("REASONING_EFFORT", "minimal")
ROUNDS = cast_str.to_int(os.environ.get("ROUNDS", "1"))
TEMPERATURE = cast_str.to_float(os.environ.get("TEMPERATURE", "0.7"))
PAYI_VERIFY_SSL = True
if os.environ.get("PAYI_VERIFY_SSL"):
  PAYI_VERIFY_SSL = cast_str.to_bool(os.environ.get("PAYI_VERIFY_SSL"), True)
else:
  PAYI_VERIFY_SSL = False if "localhost" in PAYI_API_URL or "localhost" in PAYI_PROXY_URL else True

BLOB_STORAGE_PATH = os.environ.get("BLOB_STORAGE_PATH", "")

DEFAULT_ACCOUNT_NAME = os.environ.get("DEFAULT_ACCOUNT_NAME", "")
DEFAULT_USER_ID = os.environ.get("DEFAULT_USER_ID", "")
DEFAULT_PROTAGONIST = os.environ.get("PROTAGONIST", "")
DEFAULT_ANTAGONIST = os.environ.get("ANTAGONIST", "")

# read instructions from the "## Instructions" section of README.md
instructions = ""
with open(os.path.join(ADVERSTORIAL_DIR, "README.md"), "r") as f:
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
  resource: str  # for Azure OpenAI (reference model)
  type: str  # either "protagonist" or "antagonist"

  # make a getter called `category` that processes the provider to return the category
  @property
  def category(self) -> str:
    if self.provider == "azure.openai":
      return "system.azureopenai"
    return f"system.{self.provider}"

@dataclass(frozen=True)
class Story:
  title: str
  content: str
  lines: List[str]
  request_id: Optional[str] = None

  def __str__(self):
    return f"Title: {self.title}\n\n{self.content}\n\nThe End\n"

def parse_role(value: str, type: str) -> Role:
  known_providers = {"openai", "azure.openai", "anthropic"}
  model = ""
  provider = ""
  for known_provider in known_providers:
    if value.startswith(f"{known_provider}."):
      provider = known_provider
      model = value[len(known_provider) + 1 :]
      break
  if not provider or not model:
    raise argparse.ArgumentTypeError(f"unknown provider in {value}, expected one of: {', '.join(known_providers)}")
  resource = ""
  if "/" in model:
    parts = model.split("/")
    model = parts[0]
    resource = parts[1]
  role = Role(provider=provider, model=model, resource=resource, type=type)
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

def parse_story(raw: str, request_id: Optional[str] = None) -> Optional[Story]:
  """Look for a line starting with 'Title:' and then a line ending with 'The End'. Everything in between is the content."""
  if not raw:
    raise ValueError("Empty story content")
  lines = raw.strip().splitlines()
  if not lines:
    raise ValueError("No lines found in story")

  # find the line for "Title:"
  # (case-insensitive, may be wrapped in markdown code characters)
  bi = 0
  title = None
  while bi < len(lines):
    title = parse_marker_line(lines[bi], "Title")
    bi += 1  # don't include the "Title:" line
    if title:
      break
  if not title:
    raise ValueError("Missing 'Title:'")

  # find the line for "The End"
  # (case-insensitive, may be wrapped in markdown code characters)
  ei = bi
  the_end = None
  while ei < len(lines):
    the_end = parse_marker_line(lines[ei], "The End")
    if the_end is not None:
      break
    ei += 1  # don't include the "The End" line

  if the_end is None:
    raise ValueError("Missing 'The End'")

  content = "\n".join(lines[bi : ei]).strip()
  return Story(title=title, content=content, lines=lines, request_id=request_id)


def game_loop(prompt, protagonist: Role, antagonist: Role, rounds: int):
  global instructions
  order = [protagonist, antagonist]
  random.shuffle(order)
  story: Optional[Story] = None
  game_id = uuid.uuid4().hex

  # make sure the sentinel type exists and otherwise create it
  if not deep_string(payi("api/v1/categories/adverstorial/resources/sentinel"), 'resource', 1):
    # POST /api/v1/categories/{category}/resources/{resource} Create a Resource
    payi(f"api/v1/categories/adverstorial/resources/sentinel", json_body={
      "max_input_units": 0,
      "max_output_units": 0,
      "units": {
        "text": {
          "input_price": 0,
          "output_price": 0,
        }
      }
    }, method="POST")

  # ingest a "sentinel" to mark the start of the game
  # POST /api/v1/ingest Ingest an Event
  payi("api/v1/ingest", json_body={
    "category": "adverstorial",
    "resource": "sentinel",
    "units": {
      "text": {
        "input": 1,
        "output": 1
      }
    },
    "use_case_properties": {
      "antagonist": f"{antagonist.provider}.{antagonist.model}",
      "protagonist": f"{protagonist.provider}.{protagonist.model}",
      "rounds": str(rounds),
      "seed_prompt": prompt,
      "order": f"{order[0].type},{order[1].type}",
    },
  }, method="POST", headers={
    "xProxy-UseCase-Name": "Story",
    "xProxy-UseCase-ID": game_id,
  })

  for round_num in range(1, rounds + 1):
    for role in order:
      logger.info("")
      logger.info(f"### Round {round_num} of {rounds} / Turn {order.index(role) + 1} of 2")

      use_case_step = f"round-{round_num}-turn-{order.index(role) + 1}-write"
      other_role = order[1] if role == order[0] else order[0]
      current = [
        f"* Coin toss winner: {order[0].type}",
        f"* Seed prompt: {prompt}",
        f"* It is round {round_num}, turn {order.index(role) + 1} of 2.",
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
        "use_case_step": use_case_step,
      }

      print(kwargs["message"])

      new_story = write_story(**kwargs)
      print(new_story)
      if new_story != "" and not new_story:
        logger.warning("Failed to parse story output, retrying...")
        new_story = write_story(**kwargs)
        print(new_story)
      if not new_story:
        add_game_property(game_id, "system.failure", "parse_story")
        raise ValueError("Failed to parse story output")
      story = new_story

  if story and story.title:
    add_game_property(game_id, "story.title", story.title)

  print(f"Game Over: {game_id}")
  return story
    

def write_story(role: Role, message: str, id: str = "", instructions: str = "", use_case_step: str = "") -> Story | None:
  params = {}
  temperature = TEMPERATURE + (random.random() * (TEMPERATURE / 100)) - (random.random() * (TEMPERATURE / 100))

  # OpenAI
  if role.provider == "openai":
    proxy_url = urljoin(PAYI_PROXY_URL, os.path.join(role.provider, "v1/responses"))
    headers = {
      "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']} {os.environ['PAYI_API_KEY']}",
    }

  # Azure
  if role.provider == "azure.openai":
    params["ingest"] = True
    proxy_url = urljoin(PAYI_PROXY_URL, os.path.join(role.provider, "openai/v1/responses"))
    headers = {
      "api-key": f"{os.environ['AZURE_OPENAI_API_KEY']} {os.environ['PAYI_API_KEY']}",
      "xProxy-PriceAs-Resource": role.resource,
      "xProxy-Provider-BaseUri": os.environ["AZURE_OPENAI_BASE_URI"],
    }
  
  # OpenAI and Azure OpenAI share the same request format
  if role.provider.endswith("openai"):
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

  # Anthropic
  if role.provider == "anthropic":
    proxy_url = urljoin(PAYI_PROXY_URL, os.path.join(role.provider, "v1/messages"))
    headers = {
      "anthropic-version": "2023-06-01",
      "x-api-key": f"Bearer {os.environ['ANTHROPIC_API_KEY']} {os.environ['PAYI_API_KEY']}",
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

  if role.provider not in {"openai", "azure.openai", "anthropic"}:
    raise NotImplementedError(f"Provider {role.provider} is not implemented yet.")

  headers["Content-Type"] = "application/json"
  headers["xProxy-UseCase-Name"] = "Story"
  if id:
    headers["xProxy-UseCase-ID"] = id

  # Enable shadowing to Azure Blob Storage if configured
  if BLOB_STORAGE_PATH:
    # use YYYY/MM/DD/id as the blob path
    now = datetime.now(timezone.utc)
    date_path = now.strftime("%Y/%m/%d")
    relpath = f"{date_path}/{id}"
    headers["X-Shadow"] = f"{BLOB_STORAGE_PATH}/{relpath} {os.environ['BLOB_STORAGE_TOKEN']}"

  try:
    response = requests.post(proxy_url, headers=headers, json=request, params=params)
  except Exception as e:
    logger.error(f"Error making request to {proxy_url}: {e}")
    return None
  logger.info(f"Response status code: {response.status_code}: {response.text}")

  if not response.ok:
    add_game_property(id, "system.failure", f"http_{response.status_code}")
    add_game_property(id, "system.failure.description", response.text)
    logger.error(f"Error {response.status_code}: {response.text}")
    return None

  try:
    json_response = response.json()
  except Exception as e:
    logger.error(f"Error decoding JSON response: {response.text} ({e})")
    return None

  request_id = parse_request_id(role, json_response)
  if request_id:
    add_property(request_id, "role", role.type)
    add_property(request_id, "system.user_id",
                 parse_user_id(role, response, json_response))
    add_property(request_id, "system.account_name",
                 parse_account_name(role, response, json_response))
    add_property(request_id, "system.use_case_step", use_case_step)

  text = deep_string(json_response, "text")
  try:
    story = parse_story(text, request_id=request_id)
  except Exception as e:
    add_property(request_id, "system.failure", "parse_story")
    add_property(request_id, "system.failure.description", str(e))
  return story


def parse_user_id(role: Role, response: requests.Response, json_response: dict) -> str:
  """Parse the user ID from the response or JSON response."""
  if role.provider == "openai":
    return deep_string(json_response, "user") or DEFAULT_USER_ID
  return DEFAULT_USER_ID


def parse_account_name(role: Role, response: requests.Response, json_response: dict) -> str:
  """Parse organization or account name from the response or JSON response."""
  if role.provider == "openai":
    return response.headers.get("OpenAI-Organization") or DEFAULT_ACCOUNT_NAME
  if role.provider == "anthropic":
    return response.headers.get("Anthropic-Organization-ID") or DEFAULT_ACCOUNT_NAME
  return DEFAULT_ACCOUNT_NAME


def payi(uri, json_body=None, method=None, headers=None):
  """Call Pay-i API with the given URI."""
  url = urljoin(PAYI_API_URL, uri)
  headers = dict(headers or {})  # clone headers to prevent mutation
  headers.update({
    "accept": "application/json",
    "xProxy-api-key": os.environ["PAYI_API_KEY"],
  })
  if method is None:
    method = "PUT" if json_body is not None else "GET"
  response = requests.request(
    method, url,
    headers=headers,
    json=json_body,
    verify=PAYI_VERIFY_SSL)
  if not response.ok:
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
  r = payi(f"api/v1/requests/provider/{role.category}/{provider_response_id}/result")
  if r is None:
    return None
  return deep_string(r, "request_id")


def add_property(request_id, key, value):
  """Add Pay-i Request property based on ID in the response JSON."""
  if not value:  # don't set empty values
    return
  # PUT /api/v1/requests/{request_id}/properties
  payi(f"api/v1/requests/{request_id}/properties", json_body={
    "properties": {
      key: value
    }
  }, method="PUT")


def add_game_property(game_id, key, value):
  """Add Pay-i Use Case property based on Game ID."""
  if not value:  # don't set empty values
    return
  # PUT /api/v1/use_cases/instances/{use_case_id}/properties
  payi(f"api/v1/use_cases/instances/{game_id}/properties", json_body={
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

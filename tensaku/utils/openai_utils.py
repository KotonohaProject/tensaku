import openai
from dataclasses import dataclass
import os
from typing import Optional, Callable
import subprocess
import json
from datetime import datetime
from retry import retry


MODELS = [
        {"name": "gpt-4", "azure_name": "gpt-4", "cost_prompt_per_k": 0.03, "cost_completion_per_k": 0.06},
        {"name": "gpt-3.5-turbo", "azure_name": "gpt-35", "cost_prompt_per_k": 0.0015, "cost_completion_per_k": 0.002},
    ]

@dataclass
class GPTConfig():
    model: str = "gpt-4"
    temperature: float = 0
    max_tokens: int = 500
    top_p: float = 1
    presence_penalty: float = 0
    frequency_penalty: float = 0



    def __post_init__(self):
        assert self.model in [m["name"] for m in MODELS], f"model {self.model} is not supported"

    def get_azure_deployment_id(self, model: str) -> str:
        for m in MODELS:
            if m["name"] == model:
                return m["azure_name"]

@dataclass
class InferenceLog():
    prompt_tokens: int
    completion_tokens: int
    model: str

class TokenLogger():
    logs: list[InferenceLog] = []

    def get_total_cost(self):
        total_cost = 0
        for log in self.logs:
            cost_prompt_per_k = next(m["cost_prompt_per_k"] for m in MODELS if m["name"] == log.model)
            cost_completion_per_k = next(m["cost_completion_per_k"] for m in MODELS if m["name"] == log.model)
            total_cost += log.prompt_tokens * cost_prompt_per_k
            total_cost += log.completion_tokens * cost_completion_per_k

    def log(self, prompt_tokens: int, completion_tokens: int, model: str):
        self.logs.append(InferenceLog(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, model=model))


class ParsingError(Exception):
    pass

class JsonParsingError(Exception):
    pass


@retry(tries=3, delay=5, backoff=2)
def create_completion(prompt,
                      print_prompt=False,
                      gpt_config: GPTConfig = GPTConfig(),
                      clean_output = True,
                      token_logger: TokenLogger = None):
    if print_prompt:
      print(prompt)
    result = openai.Completion.create(
      prompt=prompt,
      model=gpt_config.model if openai.api_type == "open_ai" else None,
      deployment_id = gpt_config.get_azure_deployment_id(gpt_config.model) if openai.api_type == "azure" else None,
      top_p=gpt_config.top_p,
      presence_penalty=gpt_config.presence_penalty,
      frequency_penalty=gpt_config.frequency_penalty,
      max_tokens=gpt_config.max_tokens,
      temperature=gpt_config.temperature
    )

    if token_logger:
        prompt_tokens = result["usage"]["prompt_tokens"]
        completion_tokens = result["usage"]["completion_tokens"]
        token_logger.log(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, model=gpt_config.model)

    if clean_output:
      return result['choices'][0]['text'].strip()
    else:
      return result['choices'][0]['text']

@retry(tries=3, delay=5, backoff=2)
def create_chat(messages,
                gpt_config: GPTConfig = GPTConfig(model="gpt-4"),
                functions = None,
                function_call = "auto",
                clean_output = True,
                token_logger: TokenLogger = None):
    print("------------------------------------")
    print(messages)
    print("------------------------------------")

    if functions:
        result = openai.ChatCompletion.create(
        messages=messages,
        model=gpt_config.model if openai.api_type == "open_ai" else None,
        function_call=function_call,
        functions=functions,
        deployment_id = gpt_config.get_azure_deployment_id(gpt_config.model) if openai.api_type == "azure" else None,
        top_p=gpt_config.top_p,
        presence_penalty=gpt_config.presence_penalty,
        frequency_penalty=gpt_config.frequency_penalty,
        max_tokens=gpt_config.max_tokens,
        temperature=gpt_config.temperature
        )
    else:
        result = openai.ChatCompletion.create(
        messages=messages,
        model=gpt_config.model if openai.api_type == "open_ai" else None,
        deployment_id = gpt_config.get_azure_deployment_id(gpt_config.model) if openai.api_type == "azure" else None,
        top_p=gpt_config.top_p,
        presence_penalty=gpt_config.presence_penalty,
        frequency_penalty=gpt_config.frequency_penalty,
        max_tokens=gpt_config.max_tokens,
        temperature=gpt_config.temperature
        )

    if token_logger:
        prompt_tokens = result["usage"]["prompt_tokens"]
        completion_tokens = result["usage"]["completion_tokens"]
        token_logger.log(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, model=gpt_config.model)

    if result['choices'][0]["message"].get("content") is not None:
        if clean_output:
            return result['choices'][0]["message"]["content"].strip()
        return result['choices'][0]["message"]["content"]

    try:
        result =  json.loads(result['choices'][0]["message"]["function_call"]["arguments"])
    except:
        json_string = result['choices'][0]["message"]["function_call"]["arguments"]
        raise JsonParsingError(f"Failed to parse json. Json string: \n{json_string}")

    return result

def create_chat_and_parse(messages, parsing_function: Callable, gpt_config: GPTConfig = GPTConfig(model="gpt-4"), clean_output = True, max_tries=2, token_logger: TokenLogger = None):
    return generate_and_parse(gpt_function=lambda gpt_config: create_chat(messages, gpt_config, clean_output=clean_output, token_logger=token_logger),
                       parsing_function=parsing_function,
                       gpt_config=gpt_config,
                       max_tries=max_tries)

def create_completion_and_parse(prompt, parsing_function: Callable, gpt_config: GPTConfig = GPTConfig(), clean_output = True, max_tries=2, token_logger: TokenLogger = None):
    return generate_and_parse(gpt_function=lambda gpt_config: create_completion(prompt, gpt_config, clean_output=clean_output, token_logger=token_logger),
                       parsing_function=parsing_function,
                       gpt_config=gpt_config,
                       max_tries=max_tries)

def generate_and_parse(gpt_function: Callable[[GPTConfig], str], parsing_function: Callable[[str], any], gpt_config, max_tries=4):
    # run gpt function until parsable.
    for i in range(max_tries):
        output = gpt_function(gpt_config)
        try:
            parsed_output = parsing_function(output)
            break
        except:
            if gpt_config.temperature < 0.3:
                gpt_config.temperature += 0.1

    else:
        raise ParsingError(f"Failed to parse output. GPT output: \n{output}")

    return parsed_output


def fine_tune(X: list[str], y: list[str], base_model: str, new_model_suffix: str = None):

    TRAIN_FILE_NAME_WITHOUT_EXTENSION = 'train'
    train_file_name = TRAIN_FILE_NAME_WITHOUT_EXTENSION + '.jsonl'
    prepared_file_name = TRAIN_FILE_NAME_WITHOUT_EXTENSION + '_prepared.jsonl'

    prompts_completions = zip(X, y)

    # Open a file for writing
    with open(train_file_name, 'w') as f:
        for prompt, completion in prompts_completions:
            # Create a dictionary with 'prompt' and 'completion' fields
            data = {'prompt': prompt, 'completion': completion}
            # Convert the dictionary to a JSON object and write it to the file
            f.write(json.dumps(data) + '\n')

    subprocess.run(['openai', 'tools', 'fine_tunes.prepare_data', '-f', train_file_name, '-q'])

    response = openai.File.create(
        file=open(prepared_file_name, "rb"),
        purpose='fine-tune'
    )

    cloud_file_name = response['id']

    return openai.FineTune.create(training_file=cloud_file_name,
                           model=base_model,
                           suffix=new_model_suffix)

def get_model_name_by_suffix(model_suffix: str) -> Optional[str]:
    """get finetune model name"""
    models = openai.FineTune.list().data
    # Return the list of models with a name that includes the suffix
    models_with_suffix = [model.fine_tuned_model for model in models if model_suffix in model.fine_tuned_model]

    return models_with_suffix

def get_latest_model_name_by_suffix(model_suffix: str) -> Optional[str]:
    models = get_model_name_by_suffix(model_suffix=model_suffix)
    if models == []:
        return None # no model found


    latest = None
    latest_str = None
    for s in models:
        # Split the string on the prefix
        # Split the remaining string on the hyphen character
        date_time = s.split('-')
        # Extract the date and time parts
        year, month, day, hour, minute, second = date_time[-6], date_time[-5], date_time[-4], date_time[-3], date_time[-2], date_time[-1]
        # Create a datetime object from the date and time parts
        current = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        # If the current date is later than the latest date, set the current date and current string as the latest date and string
        if latest is None or current > latest:
            latest = current
            latest_str = s
    return latest_str

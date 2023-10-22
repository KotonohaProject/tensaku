from tensaku.tensaku_generator import TensakuGenerator
import json
import importlib
from dataclasses import asdict
from dotenv import dotenv_values
import openai
import time
import os

def test_generator():
    tensaku = TensakuGenerator()
    input_text =  'I looked a movie with my friends. It was very fun.'

    env_values = dotenv_values("tests/.env.openai")
    openai.api_type = "open_ai"
    openai.api_key = env_values['OPENAI_API_KEY']

    assert openai.api_type == "open_ai"

    start_time_openai = time.time()
    all_tensaku_document_openai = tensaku.generate(input_text, generate_quiz=False)
    end_time_openai = time.time()
    openai_duration = end_time_openai - start_time_openai

    # Time measurement for Azure
    env_values = dotenv_values("tests/.env.azure")
    openai.api_type = "azure"
    openai.api_key = env_values['OPENAI_API_KEY']
    openai.api_base = env_values['OPENAI_API_BASE']
    openai.api_version = env_values['OPENAI_API_VERSION']

    assert openai.api_type == "azure"

    start_time_azure = time.time()
    all_tensaku_document_azure = tensaku.generate(input_text, generate_quiz=False)
    end_time_azure = time.time()
    azure_duration = end_time_azure - start_time_azure

    # Show the time results
    print(f"Time taken with OpenAI: {openai_duration} seconds")
    print(f"Time taken with Azure: {azure_duration} seconds")


    all_tensaku_document_azure.native_explanation.generate_html()
    result_dictionary = all_tensaku_document_azure.generate_dict()
    result_dicionatry = asdict(all_tensaku_document_azure)
    result_json_string = json.dumps(result_dictionary)
    print(result_json_string)

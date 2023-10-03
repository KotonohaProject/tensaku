from tensaku.tensaku_generator import TensakuGenerator
import json
import importlib
from dataclasses import asdict
from dotenv import load_dotenv
import openai
import time

def test_generator():
    tensaku = TensakuGenerator()
    input_text =  'I looked a movie with my friends. It was very fun.'
    
    load_dotenv(".env.openai", override=True)
    importlib.reload(openai)
    
    start_time_openai = time.time()
    all_tensaku_document_openai = tensaku.generate(input_text, generate_quiz=False)
    end_time_openai = time.time()
    openai_duration = end_time_openai - start_time_openai
    
    # Time measurement for Azure
    load_dotenv(".env.azure", override=True)
    importlib.reload(openai)
    
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
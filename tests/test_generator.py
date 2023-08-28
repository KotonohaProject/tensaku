from tensaku.tensaku_generator import TensakuGenerator
import json

def test_generator():
    tensaku = TensakuGenerator()
    input =  'I looked a movie with my friends.'

    all_tensaku_document = tensaku.generate(input, generate_quiz=False)
    result_dictionary = all_tensaku_document.generate_dict()
    result_json_string = json.dumps(result_dictionary)
    print(result_json_string)
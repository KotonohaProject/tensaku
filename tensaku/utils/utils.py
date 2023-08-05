import re
from typing import List, Callable
from tensaku.utils.openai_utils import GPTConfig

def concat_examples(examples: List[str], example_index: List[int]=None, separator: str ='\n\n') -> str:
    if example_index == None:
        example_index = range(len(examples))
    
    final_examples = ""
    n_examples = len(example_index)
    for index in example_index:
        final_examples += examples[index]
        if index != n_examples-1:
            final_examples += separator
    return final_examples

def paragraph2sentences(paragraph: str) -> List[str]:
    sentences = re.findall(r'[^.!?]+[.!?]', paragraph)
    sentences = [sentence.strip() for sentence in sentences]
    return sentences

def run_function_in_small_batches(function, input_list, batch_size=100):
    outputs = []
    for i in range(0, len(input_list), batch_size):
        batch = input_list[i:i+batch_size]
        batch_outputs = function(batch)
        outputs.extend(batch_outputs)
    return outputs

#protocal for gpt function. it only takes gpt_config as argument
    


    
if __name__ == '__main__':
    function = lambda x: x
    output = run_function_in_small_batches(function, range(10), batch_size=4)
    print(output)
    
    
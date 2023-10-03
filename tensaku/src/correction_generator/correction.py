import re

from tensaku.utils.openai_utils import create_completion, create_chat, GPTConfig, create_chat_and_parse
from tensaku.src.essay import Essay, split_into_sentences
from tensaku.utils.utils import concat_examples

class CorrectionGenerator():
    initial_conversation = [
        {"role": "system", "content": "If the sentence, taken from the paragraph, sounds unnatural corrected it. If the sentence sounds natural as it is, keep the original sentence. The sentence can be formal or casual. Abbreviations, slang, and contractions does not have to be corrected, and should be kept both when used or not used. Correct one sentence at a time. You must write the original sentence first and then the corrected sentence below."},
        {"role": "user", "content": "I’m going help you."},
        {"role": "assistant", "content": "I’m going help you.\nI’m going to help you."},
        {"role": "user", "content": """Phosphorus is one of the important elements of fertilizers. Recently the prices of Phosphorus is rising because import restrictions by China. Compost from sewage is expected to resolve situation."""},
    {"role": "assistant", "content": """Phosphorus is one of the important elements of fertilizers.
Phosphorus is one of the important elements of fertilizers.

Recently the prices of Phosphorus is rising because import restrictions by China.
Recently the price of Phosphorus has been rising because of import restrictions by China.

Compost from sewage is expected to resolve situation.
Compost from sewage is expected to resolve this situation."""},
    {"role": "user", "content": """It's heavy snow in Niigata prefecture. Some people is remaining in their car due to heavy snow. They need a rescue, so goverment in Niigata ask disaster relief to JGSDF."""},
    {"role": "assistant", "content": """It's heavy snow in Niigata prefecture.
There is heavy snow in Niigata prefecture.

Some people is remaining in their car due to heavy snow.
Some people are remaining in their car due to the heavy snow.

They need a rescue, so goverment in Niigata ask disaster relief to JGSDF.
They need a rescue, so the government of Niigata asked for disaster relief from JGSDF."""},
    ]
    
    initial_conversation_one_sentence = [
        {"role": "system", "content": "If the sentence, taken from the paragraph, sounds unnatural corrected it. If the sentence sounds natural as it is, keep the original sentence. The sentence can be formal or casual. Abbriviations, slang, and contractions does not have to be corrected, and should be kept both when used or not used."},
        {"role": "user", "content": "I'm going help you."},
        {"role": "assistant", "content": "I'm going to help you."},
        {"role": "user", "content": "Recently the prices of Phosphorus is rising because import restrictions by China."},
        {"role": "assistant", "content": "Recently the price of Phosphorus has been rising because of import restrictions by China."},
    ]
    
    gpt_config = GPTConfig(model="gpt-4")
    
    def __init__(self, print_prompt = False):
        self.print_prompt = print_prompt
        
    def generate(self, essay_text: str) -> tuple[Essay, Essay]:
        #count the number of periods
        periods = re.findall(r"\.", essay_text)
        if len(periods) <= 1:
            # when there is only one sentence, use the one sentence prompt to avoid parsing error.
            messages = self.initial_conversation_one_sentence + [{
            "role": "user", "content": essay_text
            }]
            sentences_1 = [essay_text]
            sentences_2 = [create_chat(messages=messages, gpt_config=self.gpt_config)]
        else:
            
            messages = self.initial_conversation + [{
                "role": "user", "content": essay_text
            }]
            
            def parsing_function(output: str) -> tuple[str, str]:
                lines = output.strip().split('\n\n')
                sentences_1 = []
                sentences_2 = []
                for line in lines:
                    line = line.split('\n')
                    sentences_1.append(line[0])
                    sentences_2.append(line[1])
                return sentences_1, sentences_2
        
            sentences_1, sentences_2 = create_chat_and_parse(messages=messages, gpt_config=self.gpt_config, parsing_function=parsing_function)
        
        essay = Essay(sentences_1)
        corrected_essay = Essay(sentences_2)
        
        return essay, corrected_essay

class NativeGenerator():
    def __init__(self, print_prompt = False):
        self.print_prompt = print_prompt
        
    def generate(self, essay: Essay) -> Essay:
        order_prompt = "Make the paragraph sound more natural. Use many words that are not in the original paragraph. Do not make it too complex."
        
        messages = [{"role": "user", "content": f"{order_prompt}\n\n{essay.paragraph}\n\n"}]
        native_paragraph = create_chat(messages=messages)
        return Essay(split_into_sentences(native_paragraph))
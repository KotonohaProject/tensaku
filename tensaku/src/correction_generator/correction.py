import re

from tensaku.utils.openai_utils import (
    create_completion,
    create_chat,
    GPTConfig,
    create_chat_and_parse,
)
from tensaku.src.essay import Essay, split_into_sentences
from tensaku.utils.utils import concat_examples
from tensaku.utils.openai_utils import TokenLogger


class CorrectionGenerator():
    initial_conversation = [
        {"role": "system", "content": """If the sentence, taken from the paragraph, sounds unnatural corrected it. If the sentence sounds natural as it is, keep the original sentence. The sentence can be formal or casual. Abbreviations, slang, and contractions does not have to be corrected, and should be kept both when used or not used. Correct one sentence at a time, and count. Strictly follow the examples below as the output will be directly parsed programatically.

Input: Phosphorus is one of the important elements of fertilizers. Recently the prices of Phosphorus is rising because import restrictions by China. Compost from sewage is expected to resolve situation.
Output: 1-a Phosphorus is one of the important elements of fertilizers.
1-b Phosphorus is one of the important elements of fertilizers.

2-a Recently the prices of Phosphorus is rising because import restrictions by China.
2-b Recently the price of Phosphorus has been rising because of import restrictions by China.

3-a Compost from sewage is expected to resolve situation.
3-b Compost from sewage is expected to resolve this situation.

Input: It's heavy snow in Niigata prefecture. Some people is remaining in their car due to heavy snow. They need a rescue, so goverment in Niigata ask disaster relief to JGSDF.
Output: 1-a It's heavy snow in Niigata prefecture.
1-b There is heavy snow in Niigata prefecture.

2-a Some people is remaining in their car due to heavy snow.
2-b Some people are remaining in their car due to the heavy snow.

3-a They need a rescue, so goverment in Niigata ask disaster relief to JGSDF.
3-b They need a rescue, so the government of Niigata asked for disaster relief from JGSDF."""},
    ]

    gpt_config = GPTConfig(model="gpt-4")

    def __init__(self, print_prompt = False):
        self.print_prompt = print_prompt

    def generate(self, essay_text: str, token_logger: TokenLogger = None) -> tuple[Essay, Essay]:

        messages = self.initial_conversation + [{
            "role": "user", "content": essay_text
        }]

        def parsing_function(output: str) -> tuple[str, str]:
            lines = output.strip().split('\n\n')
            sentences_1 = []
            sentences_2 = []
            for line in lines:
                line = line.split('\n')
                sentences_1.append(line[0][4:])
                sentences_2.append(line[1][4:])
            return sentences_1, sentences_2

        sentences_1, sentences_2 = create_chat_and_parse(messages=messages, gpt_config=self.gpt_config, parsing_function=parsing_function, token_logger=token_logger)

        essay = Essay(sentences_1)
        corrected_essay = Essay(sentences_2)

        return essay, corrected_essay


class NativeGenerator:
    def __init__(self, print_prompt=False):
        self.print_prompt = print_prompt

    def generate(self, essay: Essay, token_logger: TokenLogger = None) -> Essay:
        order_prompt = "Make the paragraph sound more natural. Use many words that are not in the original paragraph. Do not make it too complex, and keep the essay simple. The essay should be elementary school level."

        messages = [
            {"role": "user", "content": f"{order_prompt}\n\n{essay.paragraph}\n\n"}
        ]
        native_paragraph = create_chat(messages=messages, token_logger=token_logger)
        return Essay(split_into_sentences(native_paragraph))

if __name__ == "__main__":
    essay_text = "I looked a movie."
    essay, corrected_essay = CorrectionGenerator().generate(essay_text)
    print(corrected_essay.paragraph)

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


class CorrectionGenerator:
    initial_conversation = [
        {
            "role": "system",
            "content": """
If the sentence, taken from the paragraph, sounds unnatural corrected it. If the sentence sounds natural as it is, keep the original sentence. The sentence can be formal or casual. Abbreviations, slang, and contractions does not have to be corrected, and should be kept both when used or not used. Correct one sentence at a time.
Call the answer function for output.

Examples
Input: hosphorus is one of the important elements of fertilizers. Recently the prices of Phosphorus is rising because import restrictions by China. Compost from sewage is expected to resolve situation.
{
  "answer": [
    {
      "original": "Phosphorus is one of the important elements of fertilizers.",
      "corrected": "Phosphorus is one of the important elements of fertilizers."
    },
    {
      "original": "Recently the prices of Phosphorus is rising because import restrictions by China.",
      "corrected": "Recently the price of Phosphorus has been rising because of import restrictions by China."
    },
    {
      "original": "Compost from sewage is expected to resolve situation.",
      "corrected": "Compost from sewage is expected to resolve this situation."
    }
  ]
}

Input: It's heavy snow in Niigata prefecture. Some people is remaining in their car due to heavy snow. They need a rescue, so goverment in Niigata ask disaster relief to JGSDF.
{
  "answer": [
    {
      "original": "It's heavy snow in Niigata prefecture.",
      "corrected": "There is heavy snow in Niigata prefecture."
    },
    {
      "original": "Some people is remaining in their car due to heavy snow.",
      "corrected": "Some people are remaining in their car due to the heavy snow."
    },
    {
      "original": "They need a rescue, so goverment in Niigata ask disaster relief to JGSDF.",
      "corrected": "They need a rescue, so the government of Niigata asked for disaster relief from JGSDF."
    }
  ]
}""",
        },
    ]

    functions = [
        {
            "name": "answer",
            "parameters": {
                "type": "object",
                "required": ["answer"],
                "properties": {
                    "answer": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["original", "corrected"],
                            "properties": {
                                "original": {"type": "string"},
                                "corrected": {"type": "string"},
                            },
                        },
                    }
                },
            },
        }
    ]

    gpt_config = GPTConfig(model="gpt-4")

    def __init__(self, print_prompt=False):
        self.print_prompt = print_prompt

    def generate(self, essay_text: str, token_logger: TokenLogger = None) -> tuple[Essay, Essay]:
        # count the number of periods

        messages = self.initial_conversation + [{"role": "user", "content": essay_text}]

        output = create_chat(
            messages=messages,
            gpt_config=self.gpt_config,
            function_call={"name": "answer"},
            functions=self.functions,
            token_logger=token_logger,
        )
        print(output)

        original_sentences = []
        corrected_sentences = []
        for sentence in output["answer"]:
            original_sentences.append(sentence["original"])
            corrected_sentences.append(sentence["corrected"])

        essay = Essay(original_sentences)
        corrected_essay = Essay(corrected_sentences)

        return essay, corrected_essay


class NativeGenerator:
    def __init__(self, print_prompt=False):
        self.print_prompt = print_prompt

    def generate(self, essay: Essay) -> Essay:
        order_prompt = "Make the paragraph sound more natural. Use many words that are not in the original paragraph. Do not make it too complex, and keep the essay simple. The essay should be elementary school level."

        messages = [
            {"role": "user", "content": f"{order_prompt}\n\n{essay.paragraph}\n\n"}
        ]
        native_paragraph = create_chat(messages=messages)
        return Essay(split_into_sentences(native_paragraph))

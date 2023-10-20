from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Type, List
import re
from enum import Enum, auto


from tensaku.utils.openai_utils import create_chat, GPTConfig, TokenLogger
from tensaku.utils.utils import concat_examples
from tensaku.utils.utils import paragraph2sentences
from tensaku.src.essay import Essay


class MistakeType(str, Enum):
    WORD_CHOICE = 'Word Choice'
    UNNATURAL = 'Unnatural Expression'
    SENTENCE_STRUCTURE = 'Sentence Structure'
    SPELLING = 'Spelling'
    Grammar = 'Grammar'

    @classmethod
    def from_completion_text(cls, completion_text):
        completion_pair = {
            'Word Choice': cls.WORD_CHOICE,
            'Unnatural Expression': cls.UNNATURAL,
            'Sentence Structure': cls.SENTENCE_STRUCTURE,
            'Spelling': cls.SPELLING,
            'Grammar': cls.Grammar
        }
        return completion_pair.get(completion_text)

@dataclass
class Change(ABC):
    @abstractmethod
    def get_change_prompt(self):
        pass

@dataclass
class ChangeReplace(Change):
    before: str
    after: str
    def get_change_prompt(self):
        return f"{self.before} -> {self.after}"

@dataclass
class Mistake():
    original_sentence: str
    corrected_sentence: str
    type: MistakeType
    change: ChangeReplace #TODO convert it to union when you add more change types

    def get_change_prompt(self):
        return self.change.get_change_prompt()

class Classifier():
    initial_conversation = [
        {"role": "system", "content": "You are a English teacher. Classify student's mistakes. Try to split the mistake into small chunks as much as possible. Detect all the mistakes."},
        {"role": "user", "content":
        """Please classify the mistakes in to the following categories.
Grammar, Word Choice, Spelling, Unnatural Expression, Sentence
Strictly follow the format below.

Original: I feels I am acquiring information in English more fast.
Edited: I feel I am acquiring knowledge in English faster.
feels -> feel (Grammar)
information -> knowledge (Word Choice)
more fast -> faster (Grammar)

Original: I looked a moovie with my friends.
Edited: I watched a movie with my friends.
looked -> watched (Word Choice)
moovie -> movie (Spelling)

Original: I went for a walk with my dog, who is a 2-year-old toy poodle because I worked at home yesterday.
Edited: Because I worked from home, I walked my dog, who is a 2-year-old toy poodle.
went for a walk -> walked (Unnatural Expression)
at home -> from home (Word Choice)
because I worked at home yesterday -> because I worked from home (Sentence Structure)

Original: Fun is English.
Edited: English is fun.
Fun is English -> English is fun (Sentence Structure)

Original: Yesterday, I was able to know what is not good in my habit daily.
Edited: Yesterday, I was able to recognize a mistake in my daily habits.
know -> recognize (Word Choice)
what is not good -> a mistake (Unnatural Expression)
habit daily -> daily habits (Unnatural Expression),"""},
        {"role": "user", "content": """Original: This movie is knowing to everyone in Japan.
Edited: This movie is known to everyone in Japan."""},
        {"role": "assistant", "content": """is knowing -> is known (Grammar)"""}
    ]

    def __init__(self):
        return


    def classify(self, original_sentence: str, corrected_sentence: str, print_prompt = False, token_logger: TokenLogger = None) -> List[Type[Mistake]]:

        messages = self.initial_conversation + [{"role": "user", "content": f"Original: {original_sentence}\nEdited: {corrected_sentence}"}]
        completion = create_chat(messages=messages, gpt_config = GPTConfig(model="gpt-4"), token_logger=token_logger)
        mistakes = self._gptoutput2mistakes(completion, original_sentence, corrected_sentence)

        return mistakes

    def _gptoutput2mistakes(self, gpt_output, original_sentence, corrected_sentence):

        mistakes = []

        for match in re.finditer(r'(.+?)\s*->\s*(.+?)\s*\((.+?)\)', gpt_output):
            before = match.group(1)
            after = match.group(2)
            type = match.group(3)

            mistake_type = MistakeType.from_completion_text(type)
            change = ChangeReplace(before,  after)

            if mistake_type != None:
                mistake = Mistake(original_sentence=original_sentence,
                                        corrected_sentence=corrected_sentence,
                                        type=mistake_type,
                                        change=change)

                mistakes.append(mistake)


        return mistakes

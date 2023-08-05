from tensaku.utils.openai_utils import create_completion
from tensaku.utils.utils import concat_examples
from tensaku.src.explanation_generator.generatorbase import ExplanationGenerator
from tensaku.src.documents import MistakeExplanationDocument

from typing import List

class GrammarGenerator(ExplanationGenerator):
    
    examples = ["""Original: A dog is cute.
Edited: Dogs are cute.
a dog -> dogs

When we are talking about things in general, in other words, not specific things, we always use the plural form of countable nouns. In this case, the plural form of the noun "dog" should be used instead of the singular form, because we are talking about all dogs in general.

Example:
- Planes are faster than cars.
- Japanese people study very hard."""]
    
    order_prompt = "Explain the grammar mistake and give examples in various contexts."
    
    def __init__(self, japanese: bool, print_prompt: bool = False, example_index: List[int]=None) -> None:
        self.japanese = japanese
        self.print_prompt = print_prompt
        if example_index == None:
            self.example_index = range(len(self.examples))
        else:
            self.example_index = example_index
    
    def generate(self, original: str, edited: str, change: str) -> MistakeExplanationDocument:
        examples_prompt = concat_examples(self.examples, self.example_index)
        
        prompt = self.order_prompt + "\n\n" + examples_prompt + "\n\n" + f"Original: {original}\nEdited: {edited}\n{change}"
        if self.print_prompt:
            print(prompt)
        result = create_completion(prompt, max_tokens=400)
        if self.japanese:
            return MistakeExplanationDocument('Grammar', f"[grammar japanese not implemented yet. showing English version]\n\n{result}", self.japanese)
        return MistakeExplanationDocument('Grammar', result, self.japanese)
    
from tensaku.utils.openai_utils import create_completion
from tensaku.utils.utils import concat_examples
from tensaku.src.explanation_generator.generatorbase import ExplanationGenerator
from tensaku.src.documents import MistakeExplanationDocument
from tensaku.utils.translation import Translator

from typing import Type

class WordChoiceGenerator(ExplanationGenerator):
    
    examples = ["""Original: There is a new home next to the station.
Edited: There is a new house next to the station.
home -> house

'Home' is a place where one lives, especially with one's family. It can also be a place that one feels is a safe place. A 'house' is a building that is made for people to live in.

House:
- I'm going to go to the house on the corner.
- The house is on fire! 

Home:
- After a long day of work, I just want to go home. 
- This is my home now.

In this context, the word "house" is more appropriate because it is stating that the physical building is located next to the station.""",
        """Original: Recently the gas prices are rising because import restrictions.
Edited: Recently the gas prices have been rising due to import restrictions.
is rising -> have been rising

The verb ‘is rising' is present continuous. You use the present continuous to talk about action happening now. The verb ‘have been rising’ is present perfect continuous. You use present perfect continuous to talk about past action still-continuing.

Present Continuous:
- She is running to the store.
- The sun is shining brightly.

Present Perfect Continuous:
- I have been studying for the exam all day.
- She has been working on the project for weeks.

In this context, the verb ‘have been rising’ is more appropriate because the prices are rising continuously since import restrictions have started.""",
        """Original: Recently the gas prices are rising because import restrictions.
Edited: Recently the gas prices have been rising due to import restrictions.
because -> because of

‘Because of’ is a preposition. it is generally followed by a verb+ing or a noun. ‘Because’ is a conjunction. it is followed by a subject and a verb.

Because:
- I went to the store because I was out of milk.
- He wasn’t able to get the job because he didn’t have enough experience.

Because of:
- She was late to work because of the traffic.
- He wasn’t able to get the job because of his lack of experience.

In this context, the phrase ‘because of’ is more appropriate because 'import restrictions' is a noun phrase.""",
        """I had a Christmas party with relatives yesterday.
I had a Christmas party with my relatives yesterday.
relatives -> my relatives

The word ‘relatives’ refers to a person’s family members in general. The word ‘my relatives’ refers specifically to the speaker’s family members.

Relatives:
- I have relatives in California.
- Relatives are always important in our lives.

My Relatives: 
- My relatives are always there to support me. 
- I invited my relatives to the party.

In this context, the word ‘my relatives’ is more appropriate because it is specifying that the speaker is referring to their own family members.""",
    """Kids grow so fast.
Kids grow up so fast.
grow -> grow up
'Grow' is a verb that means to increase in size or amount. 'Grow up' is an phrasal verb that means to become an adult.

Grow:
- I grew 1 cm this year.
- The company has grown significantly over the past year.

Grow up:
- She grew up in a small town.
- She needs to grow up and take responsibility for her actions.

In this context, the phrase ‘grow up’ is more appropriate because it is referring to the process of children becoming adults."""
]
    
    order_prompt = "Explain the the differences between the words, provide example sentences and explain the reason why the words needs to be changed."
    
    def __init__(self, translator: Type[Translator], japanese, print_prompt = False, example_index=[0,1,2], debug=False) -> None:
        self.translator = translator
        self.japanese = japanese
        self.print_prompt = print_prompt
        if example_index == None:
            self.example_index = range(len(self.examples))
        else:
            self.example_index = example_index
        self.debug = debug
    
    def generate(self, original: str, edited: str, change: str) -> MistakeExplanationDocument:
        
        
        examples_prompt = concat_examples(self.examples, self.example_index)
        
        prompt = self.order_prompt + "\n\n" + examples_prompt + "\n\n" + f"Original: {original}\nEdited: {edited}\n{change}\n"
        if self.print_prompt:
            print(prompt)
        result = create_completion(prompt, max_tokens=400)
        
        
        if self.japanese:
            result = self._translate_to_japanese(result)
            return MistakeExplanationDocument('Word Choice', result, self.japanese)
        
        return MistakeExplanationDocument('Word Choice', result, self.japanese)
    
    
    def _translate_to_japanese(self, english_explanation: str) -> str:
        parts = english_explanation.split("\n\n")
        if len(parts) != 4:
            return 'Error: Could not be translated.'
        
        first_explanation = parts[0]
        examples = f"{parts[1]}\n\n{parts[2]}"
        last_explanation = parts[3]
        first_explanation_japanese = self.translator.translate_to_japanese(first_explanation)
        last_explanation_japanese = self.translator.translate_to_japanese(last_explanation)
        
        return f"{first_explanation}\n\n{first_explanation_japanese}\n\n{examples}\n\n{last_explanation}\n\n{last_explanation_japanese}"
    
    
def main():
    from tensaku.utils.translation import TranslatorGPT
    generator = WordChoiceGenerator(translator=TranslatorGPT(), japanese = True, print_prompt=True,debug=True)
    result = generator.generate('I looked a movie with my friends.', 'I looked a watched with my friends.', 'looked -> watched')
    print(result.generate_md())

if __name__ == "__main__":
    main()    
        

from tensaku.utils.openai_utils import create_completion
from tensaku.utils.utils import concat_examples
from tensaku.src.explanation_generator.generatorbase import ExplanationGenerator
from tensaku.src.documents import MistakeExplanationDocument

#TODO improve Egnlish version of examples

class UnnaturalGenerator(ExplanationGenerator):
    examples = {'jp': ["""Original: We cannot avoid feeling the Winter freezing.
Corrected: We cannot avoid feeling cold in the winter.
feeling the Winter freezing -> feeling cold in the winter
feel Winter freezing は少し不自然な表現なため、feel cold in the winter に修正させていただきました。「寒さを感じる」は英語でfeel cold という表現がよく使われます。freezingを形容詞として使って、
We can not avoid freezing winter.
と表現することもできます。
他にも寒さを表現する表現は以下のようなものがあります。
- I am freezing.
- It's so cold outside.
- I feel cold to the bone.""",
    """Original: I got up too late this morning too much.
Corrected: I got up too late this morning.
too much -> delete
Too late と一度書いているので、最後のtoo muchは冗長になります。""",
    """Original: I was able to recognize what is not good in my daily habits.
Edited:  I was able to recognize a mistake in my daily habits.
what is not good -> a mistake
what is not good は抽象的で冗長なので、この文脈では少し不自然です。a mistake とすると、より自然で簡潔な表現となります。"""
    ],
    'en': ["""Original: We cannot avoid feeling the Winter freezing.
Corrected: We cannot avoid feeling cold in the winter.
feeling the Winter freezing -> feeling cold in the winter
feel Winter freezing は不自然な表現なため、feel cold in the winter に修正させていただきました。「寒さを感じる」は英語でfeel cold という表現がよく使われます。freezingを形容詞として使って、
We can not avoid freezing winter.
と表現することもできます。
他にも寒さを表現する表現は以下のようなものがあります。
- I am freezing.
- It's so cold outside.
- I feel cold to the bone.""",
    """Original: I got up too late this morning too much.
Corrected: I got up too late this morning.
too much -> delete
Too late と一度書いているので、最後のtoo muchは冗長になります。""",
    """Original: I was able to recognize what is not good in my daily habits.
Edited:  I was able to recognize a mistake in my daily habits.
what is not good -> a mistake
'what is not good' is verbose and unnnatural. It is clearer to use 'a mistake' in this case."""
    ],
    }
    order = {'jp': "表現のミスを詳細に説明してください。", 'en': 'Explain the mistake in detail'}
    
    def __init__(self, japanese, print_prompt = False):
        self.japanese = japanese
        self.print_prompt = print_prompt
        
        
    def generate(self, original_sentence, edited_sentence, change):
        if self.japanese:
            examples_prompt = concat_examples(self.examples['jp'], range(len(self.examples)))
            order_prompt = self.order['jp']
        else:
            examples_prompt = concat_examples(self.examples['en'], [2])
            order_prompt = self.order['en']
        prompt = f"{order_prompt}\n\n{examples_prompt}\n\nOriginal: {original_sentence}\nEdited: {edited_sentence}\n{change}"
        explanation = create_completion(prompt)
        return MistakeExplanationDocument('Unnatural Expression', explanation, self.japanese)
            
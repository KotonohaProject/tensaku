from abc import ABC, abstractclassmethod
from tensaku.utils.openai_utils import create_completion
from tensaku.utils.utils import concat_examples

class Translator(ABC):
    @abstractclassmethod
    def translate_to_japanese(english_sentence: str) -> str:
        pass
    
class TranslatorGPT(Translator):
    EXAMPLES = ["""There is a grammar mistake in the way you use the verb “ask”. You should use the form “ask A For B”. 
Askの使い方に文法ミスがあります。「AにBを頼む」は "ask for B from A" となります。""",
"""You need to add an “s” to the verb if the subject is third-person singular. However, in this case, the subject is “I”, which is first-person singular, so the verb should be in the singular form.
主語が三人称単数のとき、動詞の最後に「s」をつけるというルールがあります。今回は主語が「I（私）」で一人称単数なので、動詞の単数形を使う必要があります。"""]
    ORDER_PROMPT = "Translate English to Japanese."
    
    def translate_to_japanese(self,english_sentence: str) -> str:
        example_prompt = concat_examples(self.EXAMPLES)
        prompt = f"{self.ORDER_PROMPT}\n\n{example_prompt}\n\n{english_sentence}\n"
        return create_completion(prompt, max_tokens=500)
        
def main():
    translator = TranslatorGPT()
    result = translator.translate_to_japanese("When we are talking about things in general, in other words, not specific things, we always use the plural form of countable nouns. In this case, the plural form of the noun 'dog' should be used instead of the singular form, because we are talking about all dogs in general.")
    print(result)

if __name__ == "__main__":
    main()

#TODO implement TranslationDeepl and compare it with gpt
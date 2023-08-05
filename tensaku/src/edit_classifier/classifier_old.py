from tensaku.utils.openai_utils import create_completion
from tensaku.utils.utils import concat_examples
from tensaku.utils.utils import paragraph2sentences
import re



class Classifier():
    classification_examples = [
        """Original: I feels I am acquiring information in English more fast.
Edited: I feel I am acquiring knowledge in English faster.
feels -> feel (Grammar)
information -> knowledge (Word Choice)
more fast -> faster (Grammar)""",

    """Original: I looked a moovie with my friends.
Edited: I watched a movie with my friends.
looked -> watched (Word Choice)
moovie -> movie (Spelling)""",

    """Original: I went for a walk with my dog, who is a 2-year-old toy poodle because I worked at home yesterday.
Edited: Because I worked from home, I walked my dog, who is a 2-year-old toy poodle.
went for a walk -> walked (Unnatural Expression)
at home -> from home (Word Choice)
because I worked at home yesterday -> because I worked from home (Sentence Structure)""",

    """Original: Fun is English.
Edited: English is fun.
Fun is English -> English is fun (Sentence Structure)""",

    """Original: Yesterday, I was able to know what is not good in my habit daily.
Edited: Yesterday, I was able to recognize a mistake in my daily habits.
know -> recognize (Word Choice)
what is not good -> a mistake (Unnatural Expression)
habit daily -> daily habits (Unnatural Expression)""",

    """Original: This movie is knowing to everyone in Japan.
Edited: This movie is known to everyone in Japan.
is knowing -> is known (Grammar)"""
    ]
    
    def __init__(self):
        return
    
    
    def classify_sentence(self, essay_text, edited_essay_text, example_index = [0,1,2,3,4,5], print_prompt = False):
        order_prompt = """Extract changes."""
        n_examples = len(example_index)

        examples_prompt = concat_examples(self.classification_examples, example_index)
        
        prompt = order_prompt + '\n\n' + examples_prompt + '\n\nOriginal: ' + essay_text + '\nEdited: ' + edited_essay_text + '\n'
        if print_prompt:
            print(prompt)
        gpt_output = create_completion(prompt)
        return self.gptoutput2dictionary(gpt_output)
    
    def classify(self, essay_text, edited_essay_text, print_prompt = False):
        original_sentences = paragraph2sentences(essay_text)
        edited_sentences = paragraph2sentences(edited_essay_text)
        assert len(original_sentences) == len(edited_sentences)
        
        edits = []
        for i in range(len(original_sentences)):
            original_sentence = original_sentences[i]
            edited_sentence = edited_sentences[i]
            
            sentence_info = {}
            sentence_info['original_sentence'] =  original_sentence
            sentence_info['edited_sentence'] =  edited_sentence
            sentence_info['mistakes'] = self.classify_sentence(original_sentence, edited_sentence, print_prompt=print_prompt)
            
            edits.append(sentence_info)
        
        return edits


    def gptoutput2dictionary(self, gpt_output):
        
        results = []

        # Use a regular expression to match each line of the input text
        for match in re.finditer(r'(.+?)\s*->\s*(.+?)\s*\((.+?)\)', gpt_output):
            original = match.group(1)
            edited = match.group(2)
            type = match.group(3)
            results.append({'type': type, 'original': original, 'edited': edited})
        return results

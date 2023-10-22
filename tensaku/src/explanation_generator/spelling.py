from tensaku.utils.openai_utils import create_completion, TokenLogger
from tensaku.utils.utils import concat_examples
from tensaku.src.explanation_generator.generatorbase import ExplanationGenerator
from tensaku.src.documents import MistakeExplanationDocument


class SpellingGenerator(ExplanationGenerator):

    def __init__(self, japanese, print_prompt = False):
        self.japanese = japanese
        self.print_prompt = print_prompt

    def generate(self, original, edited, change, token_logger: TokenLogger = None):
        if self.japanese:
            return MistakeExplanationDocument('Grammar', f"スペルを修正しました。 {change}" , self.japanese)
        else:
            return MistakeExplanationDocument('Grammar', f"There is a spelling mistake. {change}" , self.japanese)

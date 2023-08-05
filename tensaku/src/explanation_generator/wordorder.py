from tensaku.src.explanation_generator.generatorbase import ExplanationGenerator
from tensaku.src.documents import MistakeExplanationDocument

class WordOrderGenerator(ExplanationGenerator):
    
    def __init__(self, japanese):
        self.japanese = japanese
    
    def generate(self, original, edited, change):
        if self.japanese:
            return MistakeExplanationDocument('Word Choice', f"文章の構造が不自然です。{change}", self.japanese)
        else:
            return MistakeExplanationDocument('Word Choice', f"Word order is unnnatural. {change}", self.japanese)
    
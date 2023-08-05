from dataclasses import dataclass, field


import re
from typing import List

@dataclass
class Essay():
    sentences: List[str]
    paragraph: str  = field(init=False)
    
    def __post_init__(self):
        paragraph = ''
        for corrected_sentence in self.sentences:
            paragraph += corrected_sentence + ' '
        
        self.paragraph = paragraph.strip()
    
def split_into_sentences(paragraph: str) -> List[str]:
    sentences = re.findall(r'[^.!?]+[.!?]', paragraph)
    sentences = [sentence.strip() for sentence in sentences]
    return sentences
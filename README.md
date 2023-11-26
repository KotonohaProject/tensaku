## tensaku
Tensaku package.

This package is used for tensaku and cyten(giving scores on essays) only.
Creating UI (HTML, PDF, ...) around the result should be handled somewhere else.

# Installation

1. Set openai api key according to the official documentation
2. Setup ssh authentication, so that your project will have access to this repo. (Using deploy key is recommended)
4. poetry add git+ssh://git@github.com-tensaku:KotonohaProject/tensaku.git#v0.2.0

# Usage

Set the following environmental variables
- OPENAI_API_KEY
- OPENAI_API_TYPE (Only when using azure)
- OPENAI_API_BASE (Only when using azure)
- OPENAI_API_VERSION="2023-07-01-preview"

## Tensaku


```python
from tensaku import TensakuGenerator, score_essay

generator = TensakuGenerator()
essay = "I love learning English"
result = generator.generate(essay_text=essay, generate_quiz=True, generate_comment=True, generate_native_example=True, generate_native_explanation=True)
```

Result returned from TensakuGenerator is a python dataclass. Refer here https://github.com/KotonohaProject/tensaku/blob/main/tensaku/src/documents.py#L495.

## Cyten

```python
from tensaku.cyten import *

score_settings = ScoreSettings(
    topic="Agree or disagree: Animals have the same rights as humans.",
    words_count=WordsCountSettings(
        min=60,
        max=120,
        subtractions=[
            SubtractionWithWordsLessThan(key=0, words_less_than=80, subtract_points=2),
            SubtractionWithWordsLessThan(key=1, words_less_than=70, subtract_points=4),
            SubtractionWithWordsMoreThan(key=2, words_more_than=100, subtract_points=2),
            SubtractionWithWordsMoreThan(key=3, words_more_than=120, subtract_points=4)
        ]
    ),
    score_categories={
        Category.content: ScoreCategorySettings(
            points_allocated=4,
            criteria=[
                Criteria(point=0, content="英文が書かれていない。または、全体を通して出題のテーマから外れたことが書かれている。"),
                Criteria(point=1, content="使える語いが基本的なものに限られている。または、語いの誤りが多く、意図した内容が伝わらない。"),
                Criteria(point=2, content="使える語いが限られている。または、意味理解を妨げるような誤りが見られ、意図した内容が伝わりにくい部分が多くある。"),
                Criteria(point=3, content="必要な語いを使って、簡単な内容を表現することができる。誤りがあっても、意図した内容を伝えることができている。"),
                Criteria(point=4, content="さまざまな語いを使って、自分の考えや物事を詳しく説明することができる。一部誤りがあっても、意図した内容を十分に伝えることができている。")
            ]
        ),
        Category.vocabulary: ScoreCategorySettings(
            points_allocated=3,
            criteria=[
                Criteria(point=0, content="英文が書かれていない。または、全体を通して出題のテーマから外れたことが書かれている。"),
                Criteria(point=1, content="定型表現を使うことや、いくつかの単語を組み合わせることはできる。"),
                Criteria(point=2, content="使える文法が限られている。または、意味理解を妨げるような誤りが見られ、意図した内容が伝わりにくい部分が多くある。"),
                Criteria(point=3, content="基本的な文法に加えて、複雑な文法を使うことができる。一部誤りがあっても、意図した内容を十分に伝えることができている。")
            ]
        ),
        Category.grammar: ScoreCategorySettings(
            points_allocated=3,
            criteria=[
                Criteria(point=0, content="英文が書かれていない。または、全体を通して出題のテーマから外れたことが書かれている。"),
                Criteria(point=1, content="単語や文は書かれているが、内容のつながりが見られない。"),
                Criteria(point=2, content="いくつかのアイデアが書かれているが、内容のつながりが見えにくい。"),
                Criteria(point=3, content="基本的な文法に加えて、複雑な文法を使うことができる。一部誤りがあっても、意図した内容を十分に伝えることができている。")
            ]
        )
    }
)

essay="Animals, while deserving of ethical treatment, cannot have identical rights as humans due to fundamental differences in nature and societal roles. While animals should be protected from cruelty and exploitation, their rights must be contextualized differently. Human rights encompass complex societal, political, and personal freedoms unsuitable for animals. Instead, focusing on animal welfare and humane treatment aligns better with their needs and respects their unique place in our ecosystem."
print(score_essay(essay, score_settings))
# {'message': 'success', 'scores': {'content': 3, 'vocabulary': 3, 'grammar': 2, 'words_penalty': 0, 'total': 8}}
short_essay="hey"
print(score_essay(short_essay, score_settings))
# {'message': 'too few words', 'scores': {'content': 0, 'vocabulary': 0, 'grammar': 0, 'total': 0}}
```

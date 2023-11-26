from tensaku.src.cyten.cyten import *


def test_cyten():
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
    short_essay="hey"
    print(score_essay(short_essay, score_settings))

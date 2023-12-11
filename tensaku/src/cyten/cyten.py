from tensaku.utils.openai_utils import create_chat_and_parse, client, SEED
import json
import yaml
import warnings
from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union
import base64


class Category(str, Enum):
    content = "content"
    vocabulary = "vocabulary"
    grammar = "grammar"


class Criteria(BaseModel):
    point: Optional[int] = None
    content: Optional[str] = None


class ScoreCategorySettings(BaseModel):
    points_allocated: Optional[int] = None
    criteria: Optional[list[Criteria]] = None


class Subtraction(BaseModel):
    key: int


class SubtractionWithWordsLessThan(Subtraction):
    words_less_than: int
    subtract_points: int


class SubtractionWithWordsMoreThan(Subtraction):
    words_more_than: int
    subtract_points: int


class WordsCountSettings(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None
    additional_info: Optional[str] = None
    subtractions: Optional[
        list[Union[SubtractionWithWordsLessThan, SubtractionWithWordsMoreThan]]
    ] = None


class ScoreSettings(BaseModel):
    topic: Optional[str] = None
    words_count: Optional[WordsCountSettings] = None
    score_categories: Optional[dict[Category, ScoreCategorySettings]] = None


def penalty_by_word_count(
    essay: str,
    more_than_subtractions: dict[int:int],
    less_than_subtractions: dict[int:int],
) -> int:
    essay_word_count = len(essay.split(" "))

    more_than = 0
    for limit, subtractions in more_than_subtractions.items():
        if essay_word_count > limit and limit > more_than:
            more_than = limit

    if more_than > 0:
        return more_than_subtractions[more_than]

    less_than = 0
    for limit, subtractions in less_than_subtractions.items():
        if essay_word_count < limit and limit < less_than:
            less_than = limit

    if less_than > 0:
        return less_than_subtractions[less_than]

    return 0  # no penalty


def score_base_on_criteria(
    essay: str,
    points_allocated: int,
    criteria: dict[int:str],
    first_prompt: str,
    essay_topic: str = None,
) -> int:
    if essay_topic:
        topic_prompt = f"エッセイのトピック: {essay_topic}\n"
    else:
        topic_prompt = ""

    criteria_prompt = ""
    # sort the criteria by score
    criteria = {
        score: description
        for score, description in sorted(criteria.items(), key=lambda item: item[0])
    }
    

    for score, description in criteria.items():
        criteria_prompt += f"{score}点: {description}\n"
    criteria_prompt = criteria_prompt.strip()

    schema = {
        "type": "object",
        "properties": {
            "reason": {"type": "string"},
            "score": {"type": "integer", "minimum": 0, "maximum": points_allocated},
        },
        "required": ["reason", "score"],
    }
    schema_string = json.dumps(schema, indent=4)

    prompt = f"""{first_prompt}

{topic_prompt}
採点基準
{points_allocated}点満点
{criteria_prompt}

{essay}

jsonでアウトプットしてください
{schema_string}
"""
    result = client.chat.completions.create(
        model="gpt-4-1106-preview",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        seed=SEED,
    )
    print(prompt)
    return json.loads(result.choices[0].message.content)["score"]



def score_essay(essay: str, scoring_settings: ScoreSettings) -> dict:
    """
    input
    scoring_settings: ScoreSettings
    essay: str
    return dict
    {
        "message": "too many words" or "too few words" or "success",
        "scores": {
            "content": 10,
            "vocabulary": 10,
            "grammar": 10,
            "words_penalty": -2,
            "total": 28
        }
    }
    """
    words_count = len(essay.split(" "))
    if scoring_settings.words_count.min and words_count < scoring_settings.words_count.min:
        scores = {target_skill.value: 0 for target_skill, setting in scoring_settings.score_categories.items()}
        scores["total"] = 0
        return {"message": "too few words", "scores": scores}
    if scoring_settings.words_count.max and words_count > scoring_settings.words_count.max:
        scores = {target_skill.value: 0 for target_skill, setting in scoring_settings.score_categories.items()}
        scores["total"] = 0
        return {"message": "too many words", "scores": scores}

    scores = {}
    for target_skill, settings in scoring_settings.score_categories.items():
        if target_skill == Category.content:
            first_prompt = f"生徒のエッセイの内容と構成を日本語で採点してください。文法と語彙は考慮しないで、内容と構成だけを採点してください。"
        elif target_skill == Category.vocabulary:
            first_prompt = f"生徒のエッセイの語彙を日本語で採点してください。内容と構成、文法は考慮しないで、語彙だけを採点してください。"
        elif target_skill == Category.grammar:
            first_prompt = f"生徒のエッセイの文法を日本語で採点してください。内容と構成、語彙は考慮しないで、文法だけを採点してください。"
        else:
            raise ValueError(f"Invalid target skill: {target_skill}")

        scores[target_skill.value] = score_base_on_criteria(
            essay,
            settings.points_allocated,
            {criteria.point: criteria.content for criteria in settings.criteria},
            first_prompt,
            scoring_settings.topic if target_skill == Category.content else None,
        )

    scores["words_penalty"] = -penalty_by_word_count(
        essay,
        {
            subtraction.words_more_than: subtraction.subtract_points
            for subtraction in scoring_settings.words_count.subtractions
            if isinstance(subtraction, SubtractionWithWordsMoreThan)
        },
        {
            subtraction.words_less_than: subtraction.subtract_points
            for subtraction in scoring_settings.words_count.subtractions
            if isinstance(subtraction, SubtractionWithWordsLessThan)
        },
    )
    scores["total"] = sum(scores.values())

    return {"message": "success", "scores": scores}

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def score_essay_with_vision(essay: str, image_path: str, scoring_settings: ScoreSettings) -> dict:
    # TODO set the seed.
    base64_image = encode_image(image_path)

    skill_prompt = ""
    output_format_prompt = ""
    for target_skill, settings in scoring_settings.score_categories.items():
        if target_skill == Category.content:
            skill_prompt += f"内容と構成({settings.points_allocated}点満点)\n"
            output_format_prompt += "content:\n  reason: 理由\n  score: 整数値\n"
        elif target_skill == Category.vocabulary:
            skill_prompt += f"語彙({settings.points_allocated}点満点)\n"
            output_format_prompt += "grammar:\n  reason: 理由\n  score: 整数値\n"
        elif target_skill == Category.grammar:
            skill_prompt += f"文法({settings.points_allocated}点満点)\n"
            output_format_prompt += "vocabulary:\n  reason: 理由\n  score: 整数値\n"
        else:
            raise ValueError(f"Invalid target skill: {target_skill}")
        criteria = sorted(settings.criteria, key=lambda item: item.point)
        
        for one_criteria in criteria:
            skill_prompt += f"{one_criteria.point}点: {one_criteria.content}\n"  
        skill_prompt += "\n"
        
    if scoring_settings.words_count.additional_info:
        skill_prompt += f"ワードカウント（word_count_textにワードカウントに使う文章を書いてください。）\n{scoring_settings.words_count.additional_info}\n"
        output_format_prompt += "word_count_text: ワードカウントに使う文章"   

    prompt = f"""生徒のエッセイの内容と構成を日本語で採点してください。アウトプットをコードでパースするので、アウトプットのフォーマットに幻覚に従ってください。
OCR結果（誤りがある可能性あり）
{essay}

トピック
{scoring_settings.topic}

採点基準
{skill_prompt}

アウトプットのフォーマット（テキストは""で囲ってください。)
{output_format_prompt}

"""
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                },
            ],
            }
        ],
        max_tokens=300,
        temperature=0,
        seed=SEED,
    )
    print(prompt)
    print(response.choices[0].message.content)
    result_dict = yaml.safe_load(response.choices[0].message.content)
    print(result_dict)
    scores = {}
    
    if scoring_settings.words_count:
        words_count = len(result_dict["word_count_text"].split(" "))
        if scoring_settings.words_count.min and words_count < scoring_settings.words_count.min:
            scores = {target_skill.value: 0 for target_skill, setting in scoring_settings.score_categories.items()}
            scores["total"] = 0
            return {"message": "too few words", "scores": scores}
        if scoring_settings.words_count.max and words_count > scoring_settings.words_count.max:
            scores = {target_skill.value: 0 for target_skill, setting in scoring_settings.score_categories.items()}
            scores["total"] = 0
            return {"message": "too many words", "scores": scores}
    
    scores["words_penalty"] = -penalty_by_word_count(
        essay,
        {
            subtraction.words_more_than: subtraction.subtract_points
            for subtraction in scoring_settings.words_count.subtractions
            if isinstance(subtraction, SubtractionWithWordsMoreThan)
        },
        {
            subtraction.words_less_than: subtraction.subtract_points
            for subtraction in scoring_settings.words_count.subtractions
            if isinstance(subtraction, SubtractionWithWordsLessThan)
        },
    )
    
    del result_dict["word_count_text"]
    scores.update({category: info["score"] for category, info in result_dict.items()})
    scores["total"] = sum(scores.values())
    
    # validate scores
    for category, info in result_dict.items():
        if not (0 <= info["score"] <= scoring_settings.score_categories[category].points_allocated):
            warnings.warn(f"Invalid score for {category}: {info['score']}")
            raise ValueError(f"Invalid score for {category}: {info['score']}")
        
    return scores
    

if __name__ == "__main__":
    score_settings = ScoreSettings(
        topic="Which transportation method do you like?",
        words_count=WordsCountSettings(
            min=10,
            max=120,
            additional_info="最初の'I want to enjoy a day trip by + 交通機関'は語数に含めない。",
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

    essay = "I want to enjoy a day trip by plane / train / car. We can listen to music without the headphone. We can speak big voice, too. I don’t like crowded places, so I don’t have to meet other people. I want to enjoy speaking with my family.。"
    scores = score_essay_with_vision(essay, "tensaku/src/cyten/sample_image.png", score_settings)
    print(scores)

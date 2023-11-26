from tensaku.utils.openai_utils import create_chat_and_parse, client, SEED
import json
import warnings
from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union


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

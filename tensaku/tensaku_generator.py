from .src.correction_generator.correction import CorrectionGenerator, NativeGenerator
from .src.correction_generator.native_explanation import NativeExplanationGenerator


from .src.edit_classifier.classifier import MistakeType, Mistake, Classifier
from .src.explanation_generator.generatorbase import ExplanationGenerator
from .src.explanation_generator.wordchoice import WordChoiceGenerator
from .src.explanation_generator.grammar import GrammarGenerator
from .src.explanation_generator.spelling import SpellingGenerator
from .src.explanation_generator.unnatural import UnnaturalGenerator
from .src.explanation_generator.wordorder import WordOrderGenerator
from .src.explanation_generator.general import GeneralGenerator

from .src.quiz_generator import QuizGenerator

from .src.documents import (
    SentenceExplanationDocument,
    AllTensakuDocument,
    QuizzesDocument,
    NativeExplanationDocument,
)
from .src.essay import Essay


from tensaku.utils.openai_utils import TokenLogger

from typing import Type, List, Any, Union, Optional
from dacite import from_dict, Config
import json
import dataclasses


from .src.comment_generator.comment import create_comment


def validate_text(text: str, max_words=150, min_words=5):
    if text == "":
        return "テキストを入力してください。"
    # check number of words
    if len(text.split()) >= max_words:
        return f"{max_words}ワード以内で入力してください。"

    if len(text.split()) <= min_words:
        return f"{min_words}ワード以上で入力してください。"

    return "OK"


class TensakuGenerator:
    AVAILABLE_EXPLANATION_LANGUAGES = ["ja"]
    AVAILABLE_WRITING_LANGUAGES = ["en"]

    def __init__(
        self, explanation_language: str = "ja", writing_language: str = "en"
    ) -> None:
        assert (
            explanation_language in self.AVAILABLE_EXPLANATION_LANGUAGES
        ), f"explanation_language must be one of {self.AVAILABLE_EXPLANATION_LANGUAGES}"
        assert (
            writing_language in self.AVAILABLE_WRITING_LANGUAGES
        ), f"writing_language must be one of {self.AVAILABLE_WRITING_LANGUAGES}"
        self.explanation_language = explanation_language

        self.japanese = (
            True if explanation_language == "ja" else False
        )  # TODO This is a temporary solution. We need to make this more general.

        self.writing_language = writing_language
        self.all_tensaku_document = None
        self.token_logger = TokenLogger()

    def generate(
        self,
        essay_text: str,
        generate_quiz=False,
        generate_comment=True,
        generate_native_example=True,
        generate_native_explanation=True,
    ) -> AllTensakuDocument:
        # TODO Process emoji and stuff, so that any text can be split into sentences.

        essay_text = self._preprocess(essay_text)

        essay, corrected_essay = CorrectionGenerator().generate(
            essay_text, self.token_logger
        )

        all_mistakes = self._generate_mistakes(essay, corrected_essay)
        all_explanations = self._generate_sentence_explanation_documents(
            essay, corrected_essay, all_mistakes
        )

        #TODO implement token logger for quizes.
        quizzes = (
            self._generate_quizzes(essay, corrected_essay, all_mistakes)
            if generate_quiz
            else []
        )

        native_example = (
            NativeGenerator().generate(essay) if generate_native_example else None
        )

        if generate_native_explanation:
            assert (
                native_example != None
            ), "native_example must be generated if you want to generate native_explanation"
            native_explanation = NativeExplanationGenerator().generate(
                original=corrected_essay.paragraph, edited=native_example.paragraph
            )
        else:
            native_explanation = None

        comment = create_comment(essay.paragraph) if generate_comment else None

        all_tensaku_document = AllTensakuDocument(
            original_paragraph=essay.paragraph,
            edited_paragraph=corrected_essay.paragraph,
            native_paragraph=native_example.paragraph if native_example != None else "",
            native_explanation=native_explanation,
            comment=comment,
            sentence_wise_explanations=all_explanations,
            quizzes=quizzes,
        )
        self.all_tensaku_document = all_tensaku_document

        return all_tensaku_document

    def _preprocess(self, essay_text: str) -> str:
        # remove all the newlines
        essay_text = essay_text.replace("\r", " ").replace("\n", " ")
        return essay_text

    def _generate_quizzes(
        self,
        original_essay: Essay,
        corrected_essay: Essay,
        all_mistakes: List[List[Mistake]],
    ) -> List[QuizzesDocument]:
        generator = QuizGenerator()
        input_dictionary_list = []
        for original_sentence, corrected_sentence, sentence_mistakes in zip(
            original_essay.sentences, corrected_essay.sentences, all_mistakes
        ):
            if sentence_mistakes != []:  # No mistake
                for mistake in sentence_mistakes:
                    input_dictionary_list.append(
                        {
                            "original": original_sentence,
                            "edited": corrected_sentence,
                            "change": mistake.get_change_prompt(),
                        }
                    )
        documents = generator.generate(input_dictionary_list)

        return documents

    def _get_explanation_generator(
        self, mistake_type: MistakeType
    ) -> Optional[Type[ExplanationGenerator]]:
        generator: Optional[Type[ExplanationGenerator]] = None

        if mistake_type == MistakeType.Grammar:
            generator = GeneralGenerator(japanese=self.japanese)
            # generator = WordChoiceGenerator(translator=TranslatorGPT(), japanese=self.japanese)
        elif mistake_type == MistakeType.WORD_CHOICE:
            generator = GeneralGenerator(japanese=self.japanese)
            # generator = WordChoiceGenerator(translator=TranslatorGPT(), japanese=self.japanese)
        elif mistake_type == MistakeType.SPELLING:
            generator = SpellingGenerator(japanese=self.japanese)
        elif mistake_type == MistakeType.UNNATURAL:
            generator = GeneralGenerator(japanese=self.japanese)
            # generator = UnnaturalGenerator(japanese=self.japanese)
        elif mistake_type == MistakeType.SENTENCE_STRUCTURE:
            generator = GeneralGenerator(japanese=self.japanese)
            # generator = WordOrderGenerator(japanese=self.japanese)

        return generator

    def _generate_mistakes(
        self, original_essay: Essay, corrected_essay: Essay
    ) -> List[List[Type[Mistake]]]:
        all_mistakes = []
        for original_sentence, corrected_sentence in zip(
            original_essay.sentences, corrected_essay.sentences
        ):
            sentence_explanations = []
            sentence_mistakes = Classifier().classify(
                original_sentence, corrected_sentence, token_logger=self.token_logger
            )
            all_mistakes.append(sentence_mistakes)

        return all_mistakes

    def _generate_sentence_explanation_documents(
        self,
        original_essay: Essay,
        corrected_essay: Essay,
        all_mistakes: List[List[Type[Mistake]]],
    ) -> List[SentenceExplanationDocument]:
        all_explanations = []
        for original_sentence, corrected_sentence, sentence_mistakes in zip(
            original_essay.sentences, corrected_essay.sentences, all_mistakes
        ):
            sentence_explanations = []
            if sentence_mistakes == []:  # No mistake
                all_explanations.append(
                    SentenceExplanationDocument(
                        original_sentence,
                        corrected_sentence,
                        [],
                        self.japanese,
                        complement_comment="Perfect!",
                    )
                )

            else:  # there is (are) mistake(s)
                for mistake in sentence_mistakes:
                    explanation_generator = self._get_explanation_generator(
                        mistake.type
                    )

                    if explanation_generator != None:
                        explanation = explanation_generator.generate(
                            mistake.original_sentence,
                            mistake.corrected_sentence,
                            mistake.get_change_prompt(),
                            token_logger=self.token_logger,
                        )

                        sentence_explanations.append(explanation)
                all_explanations.append(
                    SentenceExplanationDocument(
                        original_sentence,
                        corrected_sentence,
                        sentence_explanations,
                        self.japanese,
                    )
                )
        return all_explanations


def main():
    tensaku = TensakuGenerator()
    document = tensaku.generate("I loves you. There is a door.")
    print(document.generate_md())


if __name__ == "__main__":
    main()

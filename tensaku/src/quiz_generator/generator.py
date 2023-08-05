from tensaku.utils.openai_utils import create_chat, GPTConfig
from tensaku.src.documents import FreeAnswerQuizDocument, MultipleChoiceQuizDocument
from tensaku.utils.utils import run_function_in_small_batches

MAX_MISTAKES_PER_PROMPT = 3

class QuizGenerator():
    
    check_initial_conversation = [
         {"role": "system", "content": """Compare the English sentences written by the student and the corrected English sentences. Determine whether the mistakes that can be generalized and a valid quiz can be created. Answer yes quiz should be created and no if it should not be.

For example, 

That's amazing!
That's incredible!
amazing -> incredible

A quiz can not be created from this mistake because two words are interchangeable. It is impossible to create a multiple choice question.

Mistakes related to articles are also difficult to be made into a quiz."""},
        {"role": "user", "content": """1.
That's amazing!
That's incredible!
amazing -> incredible
2.
I speaked on my mother.
I spoke with my mother.
speaked -> spoke.
3.
This is a man I were looking for.
This is the man I was looking for.
a -> the"""},
        {"role": "assistant", "content": """1. No
2. Yes
3. No"""}
    ]
    
    initial_conversation = [
    {"role": "system", "content": """Please create questions by generalizing the the mistakes indicated by arrow. The questions can be either multiple-choice questions or fill-in-the-blank questions. For each sentence there should only be one blank. For multiple-choice, the answer should be very clear, and the words should not be interchangeable. Each choice should be used 2 times.
Only use multiple choice question when you are comparing the usage of two words.

Additional information can be added with (). Generalize the mistakes and create variations in the answers using various words.

Generalize the mistake and you must use various words that was not present in the original sentence whenever possible. For example, if the student made a mistake conjugating the verb, the quiz include various verbs not present in the original sentence.

First explain the aim of the question in detail.
Separate questions with ---.
"""},
    {"role": "user", "content": """Follow the format below

The price is rising because import restrictions.
The price have been rising because of import restrictions.
1 because -> because of

Dancing fairys.
Dancing fairies.
2 fairys -> fairies

It seemed valid not just for me but could be adapted to everyone.
It seemed not only valid for me but could also be adapted for everyone.
3 valid not just for me -> not only valid for me

1
Aim: The student have trouble understanding that "because of" should be used  when it is followed by a noun or a gerund, and "because" when it is followed by a clause. This multiple-choice quiz tests the student's ability to choose "because" or "because of" in a sentence.
Type: multiple-choice
Title: because と because of の用法
Choices: 1 because, 2 because of
Questions:
1. He failed the test [1 because] he didn't study enough.
2. They won the game [2 because of] their excellent teamwork.
3. She couldn't attend the meeting [2 because of] her sickness.
4. She couldn't attend the meeting [1 because] she was sick.
---
2
Aim: The student have trouble creating plural form of a noun ending in "y". The  fill-in-the-blank quiz tests the student's ability to write plural form of various nouns ending in "y".
Type: fill-in-the-blank
Title: "y"で終わる名詞の複数形
Questions:
1. The [fairies] were dancing in the moonlight. (fairy)
2. The [butterfiles] were playing in the garden. (butterfly)
3. The [ladies] were singing in the choir. (lady)
4. The [berries] were growing in the field. (berry)
---
3
Aim: The student has trouble using "not only... but also" to express that something is true for more than one person or thing. This fill-in-the-blank quiz tests the student ability to correctly use "not only... but also" structure.Type: fill-in-the-blank
Title: "not only... but also" の使い方
Questions:
1. Staying in Kyoto is interesting [not only in summer but also] in winter. (京都に滞在することは夏だけでなく冬も面白い)
2. He [not only arrived late but also] forgot to do his homework. (彼は遅れてきただけでなく、宿題をするのを忘れた)
3. Nancy can speak [not only English but also] French. (ナンシーは英語だけでなくフランス語も話すことができます。)
4. He was kind [not only to man but also] to animals. (彼は人ばかりでなく動物に対しても親切であった。)"""}
    ]
    
    gpt_config = GPTConfig(model="gpt-4", max_tokens=1500)
        
    def __init__(self, japanese: bool = True) -> None:
        """
        non japanese not implemented yet
        """
        self.japanese = japanese
    
    def generate(self, mistakes: list[dict]) -> list[FreeAnswerQuizDocument | MultipleChoiceQuizDocument]:
        """
        mistakes: [{"original": "I got a lot of results.", "edited": "I achieved a lot of results.", "change": "got -> achieved"}]
        """
        check_if_quiz_should_be_created = run_function_in_small_batches(self.check_if_quiz_should_be_created_small_batch, mistakes, MAX_MISTAKES_PER_PROMPT)
        mistakes = [mistake for mistake, should_be_created in zip(mistakes, check_if_quiz_should_be_created) if should_be_created]
        quizzes = run_function_in_small_batches(self.quizzes_from_small_batch_of_mistakes, mistakes,  MAX_MISTAKES_PER_PROMPT)
            
        return quizzes
    
    def check_if_quiz_should_be_created_small_batch(self, mistakes: list[dict]) -> list[bool]:
        """
        mistakes: [{"original": "I got a lot of results.", "edited": "I achieved a lot of results.", "change": "got -> achieved"}]
        """
        mistakes_string = ""
        for index, mistake in enumerate(mistakes):
            mistakes_string += f'{index + 1}.\n{mistake["original"]}\n{mistake["edited"]}\n{mistake["change"]}\n'
        print(mistakes_string)
        
        messages = self.check_initial_conversation + [{
            "role": "user", "content": mistakes_string
        }]
        result = create_chat(messages=messages, gpt_config=self.gpt_config)
        
        try:
            quiz_should_be_created = self._parse_quiz_should_be_created_string(result)
        except Exception as e:
            print("error parsing quiz should be created string")
            print("Prompt: ")
            print(messages)
            print("Completion:")
            print(result)
            print(e)
            quiz_should_be_created = []
        
        if len(quiz_should_be_created) != len(mistakes):
            print("error parsing quiz should be created string")
            print("Prompt: ")
            print(messages)
            print("Completion:")
            print(result)
            print("quiz_should_be_created: ")
            print(quiz_should_be_created)
            print("mistakes: ")
            print(mistakes)
            quiz_should_be_created = [False for _ in mistakes]
            
        return quiz_should_be_created
    
    def _parse_quiz_should_be_created_string(self, result: str) -> list[bool]:
        result = result.strip()
        lines = result.splitlines()
        quiz_should_be_created = []
        for line in lines:
            if "Yes" in line:
                quiz_should_be_created.append(True)
            elif "No" in line:
                quiz_should_be_created.append(False)
        return quiz_should_be_created

    def quizzes_from_small_batch_of_mistakes(self, mistakes: list[dict]) -> list[FreeAnswerQuizDocument | MultipleChoiceQuizDocument]:
        """
        mistakes: [{"original": "I got a lot of results.", "edited": "I achieved a lot of results.", "change": "got -> achieved"}]
        """
        mistakes_string = ""
        for index, mistake in enumerate(mistakes):
            mistakes_string += f'{mistake["original"]}\n{mistake["edited"]}\n{index + 4} {mistake["change"]}\n\n'
        
        messages = self.initial_conversation + [{
            "role": "user", "content": mistakes_string
        }]
        result = create_chat(messages=messages, gpt_config=self.gpt_config)
        try:
            quizzes = self._parse_quiz_string(result)
        except Exception as e:
            print("error parsing quiz string")
            print("Prompt: ")
            print(messages)
            print("Completion:")
            print(result)
            print(e)
            quizzes = []
            
        return quizzes
    
    @staticmethod
    def _parse_quiz_string(quiz_string: str):
        quiz_list = []
        quiz_sections = quiz_string.strip().split('---')
        
            
        for quiz_section in quiz_sections:
            lines = quiz_section.strip().split('\n')
            if lines[0].isdigit():
                lines = lines[1:]
                quiz_section = '\n'.join(lines)
            if len(lines) < 2:
                pass
            
            quiz_type = lines[1].split(': ')[1].strip()     

            if quiz_type == 'multiple-choice':
                quiz_list.append(MultipleChoiceQuizDocument.from_quiz_section(quiz_section))
            elif quiz_type == 'fill-in-the-blank':
                quiz_list.append(FreeAnswerQuizDocument.from_quiz_section(quiz_section))

        return quiz_list
        
        
        
"""
Follow the format below

The price is rising because import restrictions.
The price have been rising because of import restrictions.
because -> because of

I speaked on my mother.
I spoke with my mother.
speaked -> spoke.

Dancing fairys.
Dancing fairies.
fairys -> fairies


Aim: The student have trouble understanding that "because of" should be used  when it is followed by a noun or a gerund, and "because" when it is followed by a clause. This multiple-choice quiz tests the student's ability to choose "because" or "because of" in a sentence.
Type: multiple-choice
Title: because と because of の用法
Choices: 1 because, 2 because of

Questions:
1. He failed the test (1 because) he didn't study enough.
2. They won the game (2 because of) their excellent teamwork.
3. She couldn't attend the meeting (2 because of) her sickness.
4. She couldn't attend the meeting (1 because) she was sick.
---
Aim: The student has trouble conjugating irregular past tense verbs. This  fill-in-the-blank quiz tests the student's ability to conjugate different irregular verbs indicated in () to past tense.
Type: fill-in-the-blank
Title: 過去形の不規則動詞

Questions:
1. I ___ with my mother yesterday. (speak) 
2. They ___ a great time at the party last night. (have)
3. She ___ to the store before coming home. (go)
4. He ___ a letter to his friend last week. (write)

Answers:
1. spoke
2. had
3. went
4. wrote
---
Aim: The student have trouble creating plural form of a noun ending in "y". The  fill-in-the-blank quiz tests the student's ability to write plural form of various nouns ending in "y".
Type: fill-in-the-blank
Title: "y"で終わる名詞の複数形
Questions:
1. The ___ were dancing in the moonlight. (fairy)
2. The ___ were playing in the garden. (butterfly)
3. The ___ were singing in the choir. (lady)
4. The ___ were growing in the field. (berry)

Answers:
1. fairies
2. butterflies
3. ladies
4. berries

"""

"""
Please create questions by generalizing the the mistakes indicated by arrow. The questions can be either multiple-choice questions or fill-in-the-blank questions. For multiple-choice, the answer should be very clear, and the words should not be interchangeable. Each choice should be used 2 times.

Additional information can be added with (). Generalize the mistakes and create variations in the answers using various words.

Generalize the mistake and use different words for each of the questions if possible.

First explain the aim of the question in detail. Be specific."""
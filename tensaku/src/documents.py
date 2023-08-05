from abc import ABC, abstractmethod
import re
from uuid import uuid1
from typing import List
from typing import Type, Optional
from dataclasses import dataclass, field



class TensakuDocument(ABC):
    
    @abstractmethod
    def generate_md(self) -> str:
        pass
    
    def generate_html(self) -> str:
        pass


@dataclass
class NativeExplanationDocument(TensakuDocument):
    explanation: str
    exists: bool = True

    def generate_md(self):
        return self.explanation

    def generate_html(self) -> str:
        # convert markdown list to html list, and linebreak to <br>.
        lines = self.explanation.split("\n")
        in_list = False
        html_list = []

        for line in lines:
            if line.startswith("- "):
                if not in_list:
                    html_list.append("<ul>")
                    in_list = True
                html_list.append(f"  <li>{line[2:]}</li>")
            elif line.startswith("#"):
                html_list.append(f"<h3>{line[2:]}</h3>")
            else:
                if in_list:
                    html_list.append("</ul>")
                    in_list = False
                html_list.append(f"{line}<br>")

        if in_list:
            html_list.append("</ul>")

        explanation =  "\n".join(html_list)
        
        return explanation
    


@dataclass
class MistakeExplanationDocument(TensakuDocument):
    mistake_type: str
    explanation: str
    japanese: bool

    def generate_md(self):
        return self.explanation

    def generate_html(self) -> str:
        # convert markdown list to html list, and linebreak to <br>.
        lines = self.explanation.split("\n")
        in_list = False
        html_list = []

        for line in lines:
            if line.startswith("- "):
                if not in_list:
                    html_list.append("<ul>")
                    in_list = True
                html_list.append(f"  <li>{line[2:]}</li>")
            else:
                if in_list:
                    html_list.append("</ul>")
                    in_list = False
                html_list.append(f"{line}<br>")

        if in_list:
            html_list.append("</ul>")

        explanation =  "\n".join(html_list)
        
        return explanation
    
@dataclass
class SentenceExplanationDocument(TensakuDocument):
    original_sentence: str
    edited_sentence: str
    mistake_explanations: List[MistakeExplanationDocument]
    japanese: bool
    complement_comment: Optional[str] = None

    
    def generate_html(self):
        mistake_explanations_html = "".join([mistake_explanation.generate_html() for mistake_explanation in self.mistake_explanations])
        complement_comment_html = f"<p class='body-text'>{self.complement_comment}</p>" if self.complement_comment else ""
        return f"""<div class='box'>
                        <p class='body-text'><span class='highlight'>{self.original_sentence}</span></p>
                        <p class='body-text'><span class='corrected'>{self.edited_sentence}</span></p>{mistake_explanations_html}
                        {complement_comment_html}
                    </div>"""
                    
    def generate_md(self):
        if self.complement_comment:
            return self.generate_md_with_complement()
        else:
            return self.generate_md_without_complement()
    
    def generate_md_without_complement(self, separator="\n\n"):
        mistake_explanations_md = ""
        for mistake_explanation in self.mistake_explanations:
            mistake_explanations_md += mistake_explanation.generate_md()
            mistake_explanations_md += separator
        
        return f"{self.original_sentence}\n\n{self.edited_sentence}\n\n{mistake_explanations_md}"

    def generate_md_with_complement(self, separator="\n\n"):
        mistake_explanations_md = ""
        for mistake_explanation in self.mistake_explanations:
            mistake_explanations_md += mistake_explanation.generate_md()
            mistake_explanations_md += separator
        self.complement_comment
        
        return f"{self.original_sentence}\n\n{self.edited_sentence}\n\n{mistake_explanations_md}\n\n{self.complement_comment}"





@dataclass
class MultipleChoiceQuizDocument(TensakuDocument):
    title: str
    choices: list[str]
    questions: list[str]
    answers: list[str]
    quiz_id: str = field(init=False)
    
    def __post_init__(self):
        self.quiz_id = str(uuid1())
        
    @classmethod
    def from_quiz_section(cls, quiz_section: str):
        lines = quiz_section.strip().split('\n')
        title = lines[2].split(': ')[1].strip()
        choices = lines[3].split(': ')[1].strip().split(', ')
        choices = [choice[2:] for choice in choices]
        
        questions = []
        answers = []
        for line in lines[5:]:
            #answer_number = re.findall(r'\((.*?)\)', line)[0][0]
            # find the words between []
            answer_number = re.findall(r'\[(.*?)\]', line)[0][0]
            answer = choices[int(answer_number) -1 ]
            answers.append(answer)
            question = re.sub(r'\[.*?\]', '____', line[3:])
            questions.append(question)
        
        return cls(title, choices, questions, answers)
    
    def generate_html(self):
        questions_html = ""
        for i, question in enumerate(self.questions):
            choices_html = ""
            for j, choice in enumerate(self.choices):
                choices_html += f'<input type="radio" name="q{self.quiz_id}_{i+1}" value="{choice}" id="q{self.quiz_id}_{i+1}{j+1}"> <label for="q{self.quiz_id}_{i+1}{j+1}">{choice}</label>'
            questions_html += f'<li id="answer{self.quiz_id}_{i+1}" class="multiple-choice">{question} {choices_html}</li>'
        
        return f"""
        <h3>{self.title}</h3>
        <ol>
            {questions_html}
        </ol>
        """

    def generate_js(self):
        check_answers_js = ""
        for i, answer in enumerate(self.answers):
            check_answers_js += f"""if (document.querySelector('input[name="q{self.quiz_id}_{i+1}"]:checked')?.value === '{answer}') {{
                correctCount++;
                document.getElementById('answer{self.quiz_id}_{i+1}').classList.add('correct');
            }} else {{
                document.getElementById('answer{self.quiz_id}_{i+1}').classList.add('incorrect');
            }}"""
        return check_answers_js

    
    def generate_md(self) -> str:
        choices_md = ""
        for choice in self.choices:
            choices_md += f"- {choice}"
        questions_md = ""
        for question in self.questions:
            questions_md += f"- {question}"
        answers_md = ""
        for answer in self.answers:
            answers_md += f"- {answer}"
        return f"""## {self.title}
{self.mistake_document.generate_md()}
### 選択肢
{choices_md}

### 問題
{questions_md}

## 回答
{answers_md}
"""


@dataclass
class FreeAnswerQuizDocument(TensakuDocument):
    title: str
    questions: list[str]
    answers: list[str]
    quiz_id: str = field(init=False)
    
    def __post_init__(self):
        self.quiz_id = str(uuid1())
        
    @classmethod
    def from_quiz_section(cls, quiz_section: str):
    
        lines = quiz_section.strip().split('\n')
        title = lines[2].split(': ')[1].strip()
        
        questions = []
        answers = []
        for line in lines[4:]:
            answer = re.findall(r'\[(.*?)\]', line)[0]
            answers.append(answer)
            question = re.sub(r'\[.*?\]', '____', line[3:])
            questions.append(question)
        
        return cls(title, questions, answers)
    
    def generate_md(self) -> str:
        return super().generate_md()
    
    def generate_html(self):
        questions_html = ""
        for i, question in enumerate(self.questions):
            questions_html += f'<li id="answer{self.quiz_id}_{i+1}">{question} <input type="text" id="q{self.quiz_id}_{i+1}"></li>'
        
        return f"""
        <h3>{self.title}</h3>
        <ol>
            {questions_html}
        </ol>
        """

    def generate_counter_js(self):
        check_answers_js = ""
        for i, answer in enumerate(self.answers):
            check_answers_js += f"""
            if (document.getElementById('q{self.quiz_id}_{i+1}').value === '{answer}') {{
                correctCount++;
                document.getElementById('answer{self.quiz_id}_{i+1}').classList.add('correct');
            }} else {{
                document.getElementById('answer{self.quiz_id}_{i+1}').classList.add('incorrect');
            }}
            """
        return check_answers_js

    
@dataclass
class QuizzesDocument(TensakuDocument):
    quizzes: list[FreeAnswerQuizDocument | MultipleChoiceQuizDocument]
    
    def generate_md(self) -> str:
        return super().generate_md()
    
    def generate_html(self) -> str:
        return

style_text = """.container {
	max-width: 800px;
	margin: 0 auto;
	padding: 20px;
	background-color: #fff;
	border-radius: 10px;
	box-shadow: 0px 0px 10px rgba(0,0,0,0.2);
}

.title {
	color: #333;
	font-size: 24px;
	margin-bottom: 10px;
	text-align: center;
}

.body-text {
	color: #444;
	font-size: 16px;
	line-height: 1.5;
	margin-bottom: 20px;
}

.box {
	border: 1px solid #ccc;
	border-radius: 5px;
	padding: 15px;
	margin-bottom: 20px;
}

.highlight {
	color: #007BFF;
	text-decoration: underline;
}

.corrected {
	color: #28A745;
	text-decoration: underline;
}

.explanation {
	color: #444;
	font-size: 16px;
	line-height: 1.5;
	margin-bottom: 10px;
}

.example {
	color: #444;
	font-size: 16px;
	line-height: 1.5;
	margin-bottom: 0;
}

.example li {
	margin-bottom: 5px;
	padding-left: 20px;
	position: relative;
}

.example li:before {
	content: "- ";
	position: absolute;
	left: 0;
} 

/* Decoration for perimeter */
body {
	background-color: #f2f2f2;
}

.container {
	border: 2px solid #ccc;
	padding: 30px;
	box-shadow: 0px 0px 20px rgba(0,0,0,0.2);
}

h2.title {
	border-bottom: 1px solid #ccc;
	padding-bottom: 10px;
	text-transform: uppercase;
}

.box {
	background-color: #fff;
}

.highlight {
    color: #007BFF;
    text-decoration: underline;
}

.corrected {
    color: #28A745;
    text-decoration: underline;
}

.explanation {
    color: #444;
    font-size: 16px;
    line-height: 1.5;
    margin-bottom: 10px;
}

.example {
    color: #444;
    font-size: 16px;
    line-height: 1.5;
    margin-bottom: 0;
}

.example li {
    margin-bottom: 5px;
    padding-left: 20px;
    position: relative;
}

.example li:before {
    content: "- ";
    position: absolute;
    left: 0;
}

/* Decoration for perimeter */
body {
    background-color: #f2f2f2;
}

.container {
    border: 2px solid #ccc;
    padding: 30px;
    box-shadow: 0px 0px 20px rgba(0,0,0,0.2);
}

h2.title {
    border-bottom: 1px solid #ccc;
    padding-bottom: 10px;
    text-transform: uppercase;
}

.box {
    background-color: #fff;
}

/* Button styling */
button {
    background-color: #007BFF;
    border: none;
    color: white;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 10px 2px;
    cursor: pointer;
    border-radius: 5px;
    margin-left: 50%;
    transform: translateX(-50%);
}

button:hover {
    background-color: #0056b3;
}

/* Correct and incorrect answer styling */
.correct {
    color: #28A745;
}

.incorrect {
    color: #DC3545;
}

/* Multiple choice question styling */
.multiple-choice {
    margin-bottom: 10px;
}


/* Stylized text box */
input[type="text"] {
    border: 1px solid #ccc;
    border-radius: 5px;
    padding: 5px;
    width: 100px;
}

/* Stylized radio button */
input[type="radio"] {
    display: none;
}

label {
    display: inline-block;
    padding: 5px 10px;
    background-color: #007BFF;
    color: white;
    border-radius: 5px;
    cursor: pointer;
    margin-left: 10px;
}

label:hover {
    background-color: #0056b3;
}

input[type="radio"]:checked + label {
    background-color: #0056b3;
}"""


@dataclass 
class AllTensakuDocument(TensakuDocument):
    original_paragraph: str
    edited_paragraph: str
    native_paragraph: str
    native_explanation: NativeExplanationDocument
    comment: str
    sentence_wise_explanations: List[SentenceExplanationDocument]
    quizzes: QuizzesDocument
    VERSION:str = "0.0.1"
    
    
    def _generate_sentence_wise_explanations_md(self, separator="\n\n---\n"):
        md = ""
        for sentence_explanation in self.sentence_wise_explanations:
            md += sentence_explanation.generate_md()
            md += separator
        return md
        
    def generate_md(self):
        if self.japanese:
            return f"""## あなたの英語
{self.original_paragraph}

## 添削
{self.edited_paragraph}

## ネイティブが使う表現
{self.native_paragraph}

## 文ごとの添削
{self._generate_sentence_wise_explanations_md()}

## Nicky からのコメント 
{self.comment}
"""
        else:
            return f"""## Your essay
{self.original_paragraph}

## Revised essay 
{self.edited_paragraph}

## Native essay
{self.native_paragraph}

## Sentence Wise Explanations
{self._generate_sentence_wise_explanations_md()}

## Comment from Nicky
{self.comment}
"""
    def generate_html(self):
        sentence_wise_explanations_html = "".join([sentence_explanation.generate_html() for sentence_explanation in self.sentence_wise_explanations])
        #add version on the buttom
        return f"""<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Tensaku Result</title>
        <style>{style_text}</style>
        <script>
            function checkAnswers() {{
                let correctCount = 0;

                {self.quizzes.generate_js()}

                document.getElementById('score').innerHTML = `You got ${{correctCount}} out of {len(self.quizzes.quizzes)} correct!`;
            }}

        // ... (rest of the JavaScript code)
    </script>
    </head>
    <body>
        <div class='container'>
            <h2 class='title'>あなたの英語</h2>
            <p class='body-text'>{self.original_paragraph}</p>
            <h2 class='title'>添削</h2>
            <p class='body-text'>{self.edited_paragraph}</p>
            <h2 class='title'>ネイティブが使う表現</h2>
            <p class='body-text'>{self.native_paragraph}</p>
            <h2 class='title'>文ごとの添削</h2>
            {sentence_wise_explanations_html}
            <h2 class='title'>Nicky からのコメント</h2>
            <p class='body-text'>{self.comment}</p>
        </div>
        <div class='container'>
            {self.quizzes.generate_html()}
        </div>
        Version: {self.VERSION}
    </body>
</html>"""



from tensaku.utils.openai_utils import create_chat, GPTConfig, create_chat_and_parse
from tensaku.src.explanation_generator.generatorbase import ExplanationGenerator
from tensaku.src.documents import NativeExplanationDocument, ExpressionDocument

from typing import List
import re

class NativeExplanationGenerator(ExplanationGenerator):
    
    initial_conversation = [
    {"role": "system", "content": "生徒が書いた英文と先生が書いた英文を比較して、先生が書いた英文の単語や短いフレーズから特に英語学習において重要なものだけを選んで、例文を用いて詳しく日本語で解説してください。生徒の英文に既に書かれている単語やフレーズは解説しないでください。周辺情報に関しても詳しく説明したり関連する表現やフレーズを教えてください。"},
    {"role": "user", "content": """Original: It's the 8th day of 12 days of continuous work. I don't feel tired at all; I guess I cheer up seeing my colleagues working harder. I had a party with the old PTA members last night. We had a really good time, so I was able to release my fatigue.
Edited: Today marks the eighth day of twelve days of consecutive work. I'm surprisingly not feeling tired, I think it's because I'm encouraged by my colleagues working hard. Last night, I had a great time catching up with some of the old PTA members. It was a great way to let off some steam and relax.

以下の例にできるだけ従ってください。

# Today Marks
- Today marks the anniversary of our first date.
- Today marks one year since my grandmother died.
日本語でアニバーサリーといえば良いことの”記念日”として使われますが、英語では歴史的惨事など”好ましくないこと” にも anniversary を使います。

# Consecutive
- The player hit home runs in three consecutive games. 
- Our company has posted record profits for three consecutive years. 
"Consecutive" と "continuous" はどちらも連続性を表す英単語ですが、それぞれ異なるニュアンスを持っています。
"Consecutive" は、一連の事象が順番に、間断なく続いていることを表します。これは、特定の順序やシーケンスに従って事象が連続していることを意味します。"Continuous" は、一定の期間にわたって何かが継続的に行われていることを表します。これは、一貫性や不変性を強調するために使用されます。例えば、
- The rain has been continuous for the past three days.
- The store offers continuous sales throughout the year.
両方の単語は連続性を表すものの、"consecutive" は順序やシーケンスに重点を置いているのに対し、"continuous" は一貫性や不変性に焦点を当てています。したがって、これらの単語は状況に応じて使い分けることが重要です。

# catching up with
  - It was great catching up with you after all these years.
  - I enjoyed catching up with my old friends at the reunion.
家族や友達との再会を表すフレーズは他にもあります。
reconnect with:
  - I recently reconnected with my childhood friend on social media.
  - It's important to reconnect with family members you haven't seen in a while.

# Let off some steam
- After a long day at work, I like to let off some steam by going for a run.
- The employees went out for drinks after work to let off some steam.
let off steam または let off some steam といいます。
本来は文字通り余分な蒸気を外に逃がすことですが、転じて「怒りや激情などを発散する」という意味となり、通常、言動や運動などで鬱憤を晴らすことをいいます。let の他、blow やwork といった動詞も用いられます。"""},
    ]
    
    gpt_config = GPTConfig(model="gpt-4", max_tokens=1000)
        
    
    def generate(self, original: str, edited: str) -> NativeExplanationDocument:
        
        if original == edited:
            return NativeExplanationDocument(explanations=[], exists=False)
        
        messages = self.initial_conversation + [{
            "role": "user", "content": f"Original: {original}\nEdited: {edited}"
        }]
        
        
        def parsing_function(text):
          expressions_list = []

          # Find all expressions and their explanations using Regex
          expression_pattern = re.compile(r'# (.+?)\n((?:- [^\n]+\n)+)((?:[^#]+)?)', re.S)
          matches = expression_pattern.findall(text)

          for match in matches:
              expression_dict = {}
              expression_dict['expression'] = match[0]
              expression_dict['explanation'] = match[1] + match[2]
              expressions_list.append(expression_dict)
          
          return expressions_list
        
        result = create_chat_and_parse(messages=messages, gpt_config=self.gpt_config, parsing_function=parsing_function)
        
        explanations = [ExpressionDocument(one_result['expression'], one_result['explanation']) for one_result in result]
        
        return NativeExplanationDocument(explanations=explanations)
    
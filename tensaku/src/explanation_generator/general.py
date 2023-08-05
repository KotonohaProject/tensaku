from tensaku.utils.openai_utils import create_chat, GPTConfig
from tensaku.src.explanation_generator.generatorbase import ExplanationGenerator
from tensaku.src.documents import MistakeExplanationDocument

from typing import List

class GeneralGenerator(ExplanationGenerator):
    
    initial_conversation = [
    {"role": "system", "content": "あなたは英語の先生です。生徒が書いた英文と修正後の英文を比較して、矢印で示された間違いを詳細に文法用語を用いて自然な日本語で解説してください。文章に複数の間違いがあっても、矢印で示された間違え１つだけを解説してください。必要に応じて比較したり例文も用いてください。"},
    {"role": "user", "content": """以下の例にできる限り従って解説してください。
Original: We cannot avoid feeling the Winter freezing.
Corrected: We cannot avoid feeling cold in the winter.
feeling the Winter freezing -> feeling cold in the winter

このままでも伝わりますが、feel Winter freezing は一般的な表現ではありません。「寒さを感じる」はfeel coldという表現がよく使われます。freezingを形容詞として使って、We can not avoid freezing winter. と表現することもできます。
他にも寒さを表現する英語は以下のようなものがあります。
- I am freezing.
- It's so cold outside.
- I feel cold to the bone.

Original: I was able to recognize what is not good in my habits daily.
Edited:  I was able to recognize a mistake in my daily habits.
what is not good -> a mistake

what is not good は冗長で少し不自然です。a mistake とすると、より自然で簡潔な表現となります。"""},
    {"role": "assistant", "content": "分かりました。"},
#     {"role": "user", "content": """Original: It's heavy snow in Niigata prefecture.
# Edited: There is heavy snow in Niigata prefecture.
# It’s heavy snow. -> There is heavy snow.""",},
#     {"role": "assistant", "content": """It’s snowは「これは雪である」という意味で、今回の文脈では不適切です。「雪がふっている」は、There is snowと表します。他の表現として、It is snowing heavily. とすることもできます。"""},
    {"role": "user", "content": """Original: I got a lot of results.
Edited: I achieved a lot of results.
got -> achieved"""},
    {"role": "assistant", "content": """getとachieveはどちらも何かを手に入れるという意味では似ていますが、それぞれのニュアンスや使い方に違いがあります。

getは、もっと一般的で広い意味を持ち、物や情報、状況など様々なものを手に入れることができます。また、getは、特定の努力や過程が必要でない場合も使われます。例:
- I got a new phone.（新しい携帯電話を手に入れた）
- She got the information she needed.（彼女は必要な情報を手に入れた）

一方、achieveは、目標や願望を達成することに特化した言葉で、通常努力や時間をかけて達成されるものに対して使われます。たいてい、達成されるものは抽象的で、具体的な物体ではないことが多いです。例:
- He achieved his goal of becoming a doctor.（彼は医者になるという目標を達成した）
- She achieved success in her career.（彼女はキャリアで成功を収めた）

今回のように、成果や目標を達成する文脈では、achieved を使うことでより自然な表現になります。"""},
#     {"role": "user", "content": """The price is rising because import restrictions.
# The price have been rising because of import restrictions.
# because -> because of"""},
#     {"role": "assistant", "content": """解説：
# because は「〜の理由で」という意味で、主に文の接続に使われます。一方、because of は「〜のために」という意味で、名詞や名詞句と一緒に使われます。 例えば、以下のような表現があります。

# Because of:
# - The game was canceled because of the rain.
# - She was late because of the traffic.

# Because:
# - I went to the store because I was out of milk.
# - He wasn’t able to get the job because he didn’t have enough experience.

# この場合、import restrictions は名詞句なので、because of が適切な接続詞となります。due to も because of と同じ意味なので使うことができます。"""}
     ]
    
    gpt_config = GPTConfig(model="gpt-4")
        
    def __init__(self, japanese: bool = True) -> None:
        """
        non japanese not implemented yet
        """
        self.japanese = japanese
    
    def generate(self, original: str, edited: str, change: str) -> MistakeExplanationDocument:
        
        messages = self.initial_conversation + [{
            "role": "user", "content": f"Original: {original}\nEdited: {edited}\n{change}"
        }]
        result = create_chat(messages=messages, gpt_config=self.gpt_config)
        if not self.japanese:
            return MistakeExplanationDocument('Grammar', f"[engish not implemented yet. showing jaoanese version]\n\n{result}", self.japanese)
        
        return MistakeExplanationDocument('Grammar', result, self.japanese)



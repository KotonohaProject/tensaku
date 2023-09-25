from tensaku.utils.openai_utils import create_chat_and_parse


def score_essay(essay: str):
    
    prompt = f"""生徒のエッセイを日本語で採点してください。
採点基準
- 内容●構成
- 語彙
- 文法
それぞれの観点に対してコメントして、最終的な点数を10点満点で教えてください。
pythonのスクリプトでparseするので、以下のフォーマットに厳格に従ってください。
基本的な語彙が適切に使えていて、文法的な問題がなければ満点です。
例：
I can't master English although I had stayed in England for a year: 10

内容●構成
{{一文でコメント}}
語彙
{{一文でコメント}}
文法
{{一文でコメント}}
Score: {{整数}}

{essay}
"""
    messages = [{
        "role": "user",
        "content": prompt
    }]
    def parse(output):
        # output score and comments
        return output.split("Score: ")[0].strip(), output.split("Score: ")[1].strip()
    
    return create_chat_and_parse(messages, parse)

if __name__ == "__main__":
    essay = "My sister has a talent for taking photographs. She often posts pictures on her SNS. I always think that her photographs are beautiful and well-balanced. If we take pictures of the same thing, my sister's pictures are always better than mine! I have no idea how to take nice pictures. I think she could become a very good photographer!"
    print(score_essay(essay))
from tensaku.utils.openai_utils import create_chat, GPTConfig, TokenLogger

def create_comment(essay_text, token_logger: TokenLogger = None) -> str:
    config = GPTConfig(model='gpt-4', temperature=0.7)
    initial_messages = [
        {"role": "system", "content": "You are an English teacher. Write a friendly comment to the following student essay. (It might be an Essay) Mention things that are done well in terms of English. Then translate it in Japanese."},
        {"role": "user", "content": "I got an invitation for English coaching online seminar! I could get TOEIC score, over 800 thanks to his YouTube, so I'm very exciting😆✨ Thank you so much, おさるさん！"},
        {"role": "assistant", "content": """Hi there! It's wonderful to see your enthusiasm for improving your English skills. You've done an excellent job of expressing your excitement and gratitude in your essay entry. Your use of the phrase "I'm very exciting" effectively conveys your feelings, although it's more appropriate to say "I'm very excited" in this context. Also, it's great to see that you're incorporating informal language and emojis to create a friendly tone. Keep up the fantastic work, and congratulations on achieving a TOEIC score of over 800! 😊👏
こんにちわ！あなたの英語力向上への熱意を拝見して、素晴らしいです。あなたは日記で、興奮と感謝の気持ちを見事に表現していますね。この文脈では「I'm very excited」と言った方が適切ですが、「I'm very exciting」というフレーズを使うことで、あなたの気持ちを効果的に伝えています。また、カジュアルな言葉や絵文字を使って親しみやすさを演出しているのも素晴らしいですね。引き続き素晴らしい成果をおさめてください！そして、TOEIC800点以上達成おめでとうございます！😊👏。"""},
        {"role": "user", "content": essay_text}
    ]
    return create_chat(initial_messages, config, token_logger=token_logger)

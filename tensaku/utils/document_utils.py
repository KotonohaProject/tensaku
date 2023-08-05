import imgkit
import markdown


def markdown2png(text: str, output_file: str = 'output.png'):
    html_text = markdown.markdown(text)
    print(html_text)
    styled_html_text = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{
          font-family: Arial, sans-serif;
        }}
      </style>
    </head>
    <body>
    {html_text}
    </body>
    </html>
    """
    imgkit.from_string(styled_html_text, output_file)

if __name__ == '__main__':
    # Markdown text
#     md_text = '''# Hello, World!
    html_text ="""<h2 style='color: #333; font-size: 24px; margin-bottom: 10px;'>あなたの英語</h2><p style='color: #444; font-size: 16px; line-height: 1.5; margin-bottom: 20px;'>I've been going through everything I can do this year, but it's not perfect, and there is more I can do. On the other hand, I got a lot of results I never had last year. But I wanna do something more, especially in English.</p><h2 style='color: #333; font-size: 24px; margin-bottom: 10px;'>添削</h2><p style='color: #444; font-size: 16px; line-height: 1.5; margin-bottom: 20px;'>I have been exploring all the possibilities I can do this year, but it's not perfect, and there is more I can do. On the other hand, I achieved a lot of results I never had last year. But I want to do something more, especially in English.</p><h2 style='color: #333; font-size: 24px; margin-bottom: 10px;'>ネイティブが使う表現</h2><p style='color: #444; font-size: 16px; line-height: 1.5; margin-bottom: 20px;'>I've been considering all the possibilities for this year, but I'm not completely satisfied with the outcome. I have achieved more than I did last year, but I'm still looking for ways to improve, particularly in English.</p><h2 style='color: #333; font-size: 24px; margin-bottom: 10px;'>文ごとの添削</h2><div style='border: 1px solid #ccc; border-radius: 5px; padding: 15px; margin-bottom: 20px;'><p style='color: #444; font-size: 16px; line-height: 1.5;'><span style='color: #007BFF; text-decoration: underline;'>I've been going through everything I can do this year, but it's not perfect, and there is more I can do.</span></p><p style='color: #444; font-size: 16px; line-height: 1.5;'><span style='color: #28A745; text-decoration: underline;'>I have been exploring all the possibilities I can do this year, but it's not perfect, and there is more I can do.</span></p><p style='color: #444; font-size: 16px; line-height: 1.5; margin-bottom: 10px;'>解説：
going through は、「通過する」「（試練などを）経験する」「（書類やリストなどを）見る」などの意味がありますが、この文脈では適切ではありません。「自分ができることを調べる」という意味で exploring（探索する） を用いると、より自然で正確な表現になります。

Going through の例文:
- She is going through a difficult time.
- I am going through my old photos.

Exploring の例文:
- We are exploring new marketing strategies.
- She is exploring her career options.

今回の文脈では、going through を exploring に変更することで、自分ができることを見つけられる可能性に焦点を当てた、より適切な表現になります。</p><p style='color: #444; font-size: 16px; line-height: 1.5; margin-bottom: 10px;'>解説：
everything I can do という表現は、直訳では「私ができるすべてのこと」となりますが、この文脈では少し不自然です。all the possibilities は「すべての可能性」という意味で、今回の文脈では、「今年私ができることを試みる」というニュアンスでより適切です。

Everything I can do:
- I will give everything I can do to help you.

All the possibilities:
- I have considered all the possibilities before making a decision.

今回の場合、all the possibilities を使うことで、「今年私ができることのすべての可能性を探求しているが、それでも完全ではなく、もっとできることがある」という意味がより明確に伝わり、自然な表現になります。</p></div><div style='border: 1px solid #ccc; border-radius: 5px; padding: 15px; margin-bottom: 20px;'><p style='color: #444; font-size: 16px; line-height: 1.5;'><span style='color: #007BFF; text-decoration: underline;'>On the other hand, I got a lot of results I never had last year.</span></p><p style='color: #444; font-size: 16px; line-height: 1.5;'><span style='color: #28A745; text-decoration: underline;'>On the other hand, I achieved a lot of results I never had last year.</span></p><p style='color: #444; font-size: 16px; line-height: 1.5; margin-bottom: 10px;'>解説：
この場合も、got ではなく achieved を使うことで、「成果を上げる」という意味になり、文脈に適した表現をしています。got は「得る」や「手に入れる」という意味ですが、ここでは「成果を上げる」という意味で使いたいため、achieved が適切です。

例文：
- She achieved remarkable results in her studies.
- Our team achieved great results last month.

達成感や努力を伴う成果について表現する際は、achieved を使うことで自然な英文になります。</p></div><div style='border: 1px solid #ccc; border-radius: 5px; padding: 15px; margin-bottom: 20px;'><p style='color: #444; font-size: 16px; line-height: 1.5;'><span style='color: #007BFF; text-decoration: underline;'>But I wanna do something more, especially in English.</span></p><p style='color: #444; font-size: 16px; line-height: 1.5;'><span style='color: #28A745; text-decoration: underline;'>But I want to do something more, especially in English.</span></p><p style='color: #444; font-size: 16px; line-height: 1.5; margin-bottom: 10px;'>解説：
wanna は口語やインフォーマルな表現で、want to の短縮形です。ただし、正式な文書やビジネス会話などフォーマルな場面では、want to を使う方が適切で、より自然です。wanna は友達や家族との会話などカジュアルな場面で使用することができますが、一般的には want to を使った方が安全です。そのため、この文では want to に修正しました。</p></div><h2 style='color: #333; font-size: 24px; margin-bottom: 10px;'>Nicky からのコメント</h2><p style='color: #444; font-size: 16px; line-height: 1.5; margin-bottom: 20px;'>Hi there! It sounds like you have been doing a lot of reflection and goal-setting this year. That's great! It's wonderful that you have achieved a lot of results already, and I'm sure you can do even more. English is a great subject to explore, and I'm sure you can find something that will challenge and excite you. Keep up the great work!</p>"""
    imgkit.from_string("""<!DOCTYPE html>
    <html>
    <head>
	<title>Professional HTML</title>
 <meta charset="utf-8">
 <style>
.container {
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
      </style>
     
</head>
<body>
	<div class="container">
		<h2 class="title">あなたの英語</h2>
		<p class="body-text">I've been going through everything I can do this year, but it's not perfect, and there is more I can do. On the other hand, I got a lot of results I never had last year. But I wanna do something more, especially in English.</p>
		<h2 class="title">添削</h2>
		<p class="body-text">I have been exploring all the possibilities I can do this year, but it's not perfect, and there is more I can do. On the other hand, I achieved a lot of results I never had last year. But I want to do something more, especially in English.</p>
		<h2 class="title">ネイティブが使う表現</h2>
		<p class="body-text">I've been considering all the possibilities for this year, but I'm not completely satisfied with the outcome. I have achieved more than I did last year, but I'm still looking for ways to improve, particularly in English.</p>
		<h2 class="title">文ごとの添削</h2>
		<div class="box">
			<p class="body-text"><span class="highlight">I've been going through everything I can do this year, but it's not perfect, and there is more I can do.</span></p>
			<p class="body-text"><span class="corrected">I have been exploring all the possibilities I can do this year, but it's not perfect, and there is more I can do.</span></p>
			<p class="explanation">解説：
				going through は、「通過する」「（試練などを）経験する」「（書類やリストなどを）見る」などの意味がありますが、この文脈では適切ではありません。「自分ができることを調べる」という意味で exploring（探索する） を用いると、より自然で正確な表現になります。
			</p>
			<p class="example">
				Going through の例文:
				- She is going through a difficult time.
				- I am going through my old photos.

				Exploring の例文:
				- We are exploring new marketing strategies.
				- She is exploring her career options.

				今回の文脈では、going through を exploring に変更することで、自分ができることを見つけられる可能性に焦点を当てた、より適切な表現になります。</p>
		</div>
		<div class="box">
			<p class="body-text"><span class="highlight">On the other hand, I got a lot of results I never had last year.</span></p>
			<p class="body-text"><span class="corrected">On the other hand, I achieved a lot of results I never had last year.</span></p>
			<p class="explanation">解説：
				この場合も、got ではなく achieved を使うことで、「成果を上げる」という意味になり、文脈に適した表現をしています。got は「得る」や「手に入れる」という意味ですが、ここでは「成果を上げる」という意味で使いたいため、achieved が適切です。</p>
			<p class="example">
				例文：
				- She achieved remarkable results in her studies.
				- Our team achieved great results last month.

				達成感や努力を伴う成果について表現する際は、achieved を使うことで自然な英文になります。</p>
		</div>
		<div class="box">
			<p class="body-text"><span class="highlight">But I wanna do something more, especially in English.</span></p>
			<p class="body-text"><span class="corrected">But I want to dosomething more, especially in English.</span></p>
			<p class="explanation">解説：
				wanna は口語やインフォーマルな表現で、want to の短縮形です。ただし、正式な文書やビジネス会話などフォーマルな場面では、want to を使う方が適切で、より自然です。wanna は友達や家族との会話などカジュアルな場面で使用することができますが、一般的には want to を使った方が安全です。そのため、この文では want to に修正しました。</p>
		</div>
		<h2 class="title">Nicky からのコメント</h2>
		<p class="body-text">Hi there! It sounds like you have been doing a lot of reflection and goal-setting this year. That's great! It's wonderful that you have achieved a lot of results already, and I'm sure you can do even more. English is a great subject to explore, and I'm sure you can find something that will challenge and excite you. Keep up the great work!</p>
	</div>
</body>
</html>""", 'test.png')
# This is a simple markdown document.

# - Item 1
# - Item 2
#     '''
#     markdown2png(md_text)

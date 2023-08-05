import openai

def create_completion(prompt, max_tokens=100, print_prompt=False):
    if print_prompt:
      print(prompt)
    result = openai.Completion.create(
  model="text-davinci-003",
  prompt=prompt,
  max_tokens=max_tokens,
  temperature=0
)
    return result['choices'][0]['text'].strip()
## tensaku
Tensaku package.

This package is used for tensaku and cyten(giving scores on essays) only.
Creating UI (HTML, PDF, ...) around the result should be handled somewhere else.

# Installation

1. Set openai api key according to the official documentation
2. Setup ssh authentication, so that your project will have access to this repo. (Using deploy key is recommended)
4. poetry add git+ssh://git@github.com-tensaku:KotonohaProject/tensaku.git#v0.2.0

# Usage

Set the following environmental variables
- OPENAI_API_KEY
- OPENAI_API_TYPE (Only when using azure)
- OPENAI_API_BASE (Only when using azure)
- OPENAI_API_VERSION="2023-07-01-preview"

```python
from tensaku import TensakuGenerator, score_essay

generator = TensakuGenerator()
essay = "I love learning English"
result = generator.generate(essay_text=essay, generate_quiz=True, generate_comment=True, generate_native_example=True, generate_native_explanation=True)
score, comment = score_essay(essay)
```

Result returned from TensakuGenerator is a python dataclass. Refer here https://github.com/KotonohaProject/tensaku/blob/main/tensaku/src/documents.py#L495.

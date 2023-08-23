## tensaku
Tensaku package.

This package is used for tensaku and cyten(giving scores on essays) only.
Creating UI (HTML, PDF, ...) around the result should be handled somewhere else.

# Installation

1. Set openai api key according to the official documentation
2. Setup ssh authenticatio, so that your project will have access to this repo. (Using deploy key is recommended)
4. poetry add git+ssh://git@github.com:KotonohaProject/tensaku.git#v0.2.0

# Usage

```python
from tensaku import TensakuGenerator

generator = TensakuGenerator()
result = generator.generate(essay_text="I love learning English", generate_quiz=True, generate_comment=True, generate_native_example=True, generate_native_explanation=True)
```

Result returned from TensakuGenerator is a python dataclass. Refer here https://github.com/KotonohaProject/tensaku/blob/main/tensaku/src/documents.py#L495.

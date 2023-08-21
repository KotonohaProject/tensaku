## tensaku
Tensaku package

# Usage

```python
from tensaku import TensakuGenerator

generator = TensakuGenerator()
result = generator.generate(essay_text="I love learning English", generate_quiz=True, generate_comment=True, generate_native_example=True, generate_native_explanation=True)
```

Result returned from TensakuGenerator is a python dataclass. Refer here https://github.com/KotonohaProject/tensaku/blob/main/tensaku/src/documents.py#L495.

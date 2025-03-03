import asyncio

from validation.models import ValidateRequest
from validation.validation_endpoint import Validation


async def test_my_score():
    prompt_text = "A stainless steel chef's knife with a comfortable ergonomic handle and a razor-sharp blade."

    validation = Validation()
    resp = ValidateRequest(prompt=prompt_text, uid=173)
    # 校验得分
    score = validation.validate(resp)
    print(f"test_my_score: {score}")


if __name__ == '__main__':
    asyncio.run(test_my_score())

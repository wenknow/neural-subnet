import asyncio
import os
import shutil
import sys
import time

import requests

from validation.models import ValidateRequest
from validation.validation_endpoint import Validation


async def test_my_score(url, prompt, ext, steps, seed):
    prompt_text = prompt
    destination_folder = './validation/results/186'
    gen_url = url + "/generate_from_text/"

    params = {'prompt': prompt + ext, 'steps':steps, 'seed':seed}
    response = requests.post(gen_url, json=params)
    if response.status_code != 200:
        print(f"err to request text_to_image. {response.text}")
        return
    time.sleep(15)
    print(f"response: {response.text}")

    # 复制文件到验证器文件夹
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    try:
        shutil.copy("../generate/outputs/text_to_3d/mesh.png", destination_folder + '/preview.png')
        shutil.copy("../generate/outputs/text_to_3d/mesh.glb", destination_folder + '/output.glb')
        print(f"文件已成功复制到 {destination_folder}")
    except Exception as e:
        print(f"复制文件时出错: {e}")

    validation = Validation()
    resp = ValidateRequest(prompt=prompt_text, uid=186)
    # 校验得分
    score = validation.validate(resp)
    print(f"test_my_score: {score}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        url = sys.argv[1]
        prompt = sys.argv[2]
        ext = sys.argv[3]
        steps = sys.argv[4]
        seed = sys.argv[5]
    else:
        url = "http://localhost:9071"
        prompt = "A stainless steel chef's knife with a comfortable ergonomic handle and a razor-sharp blade."
        ext = "A stainless steel chef's knife with a comfortable ergonomic handle and a razor-sharp blade.白色背景,3D风格,最佳质量"
        steps = 25
        seed = 0
    asyncio.run(test_my_score(url, prompt, ext, steps, seed))

import asyncio
import os
import shutil

from neuralai.protocol import NATextSynapse
from neurons.miner import Miner
from validation.models import ValidateRequest
from validation.validation_endpoint import Validation


async def test_my_score():
    prompt_text = "A stainless steel chef's knife with a comfortable ergonomic handle and a razor-sharp blade."
    destination_folder = './validation/results/186'

    miner = Miner()
    synapse2 = NATextSynapse()
    synapse2.prompt_text = prompt_text
    synapse2.timeout = 120
    # 生成模型
    synapse = await miner.forward_text(synapse2)
    print(f"success generate synapse:{synapse}")

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
    asyncio.run(test_my_score())

import os
import sys

from infer import Text2Image

text_to_image_model = Text2Image(pretrain="weights/hunyuanDiT", device="cuda:0", save_memory=False)
output_folder = os.path.join("../validation/validation/results", "173")

if len(sys.argv) > 1:
    prompt = sys.argv[1]
    ext = sys.argv[2]
    steps = sys.argv[3]
    seed = sys.argv[4]
else:
    exit("argv error")

res_rgb_pil = text_to_image_model(
    prompt + ext,
    seed=int(seed),
    steps=int(steps)
)
res_rgb_pil.save(os.path.join(output_folder, "preview.png"))

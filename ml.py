#%%
import torch
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
from diffusers.pipeline_utils import DIFFUSERS_CACHE
import os
# import matplotlib.pyplot as plt
from PIL import Image
# from xformers.ops import MemoryEfficientAttentionFlashAttentionOp

print('CUDA is available') if torch.cuda.is_available() else print('CUDA is not available')

huggingface_access_token = os.environ.get("HUGGINGFACE_ACCESS_TOKEN")


def load_pipeline(model: str = "stabilityai/stable-diffusion-2", revision: str = "fp16", cache_dir: str = DIFFUSERS_CACHE) -> StableDiffusionPipeline:
    """ Important: The diffusion models are large (~2.5GB) so loading the pipeline in memory from disk is time-consuming.
    It is recommended to load the pipeline on host start, and then reuse it for all images you want to generate.
    :param model: The name of the model to load.
    :param revision: The precision of the loaded weights. By default we load the float16 precision model branch
    :param cache_dir: The local directory where the models are stored. If None, the default cache directory is used.
    (instead of float32)
    """
    print('loading pipeline...')
    torch_dtype = torch.float16  # telling diffusers to expect the weights to be in float16 precision
    scheduler = EulerDiscreteScheduler.from_pretrained(model, subfolder="scheduler")
    pipe = StableDiffusionPipeline.from_pretrained(
        model, revision=revision, scheduler=scheduler, local_files_only=False, cache_dir=cache_dir,
        return_cached_folder=False, torch_dtype=torch_dtype, use_auth_token=huggingface_access_token)
    return pipe


def img_from_prompt(
        prompt: str, pipe, seed: int = 1024, height: int = 256, width: int = 256, guidance_scale: float = 7.5,
        num_inference_steps: int = 10) -> Image:

    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe.to(device)
    if device == "cuda":
        # pipe.enable_xformers_memory_efficient_attention(attention_op=MemoryEfficientAttentionFlashAttentionOp)
        torch.cuda.empty_cache()
        pipe.enable_attention_slicing()

    # Generate the image
    generator = torch.Generator(device).manual_seed(seed)
    img: Image = pipe(prompt=prompt, height=height, width=width, guidance_scale=guidance_scale,
                      num_inference_steps=num_inference_steps, generator=generator).images[0]

    return img


#%%
# pipe = load_pipeline()

#%%
# prompt = "A Japanese old man, wide shot, ultrarealistic uhd faces, Kodak Ultramax 800, pexels, 85mm, casual pose, " \
#          "35mm film roll photo, hard light, detailed skin texture, masterpiece, sharp focus, pretty, perfect, " \
#          "wise, handsome, adorable, Hasselblad, candid street portrait : 6"
# image = img_from_prompt(prompt, pipe)
# image = Image.open("D:/Projects_D/ΑΣΕΠ τεστ/images/ad1.PNG")

# print(type(image))
# # display(image)
# plt.imshow(image)
# plt.axis('off')
# plt.show()
#%%


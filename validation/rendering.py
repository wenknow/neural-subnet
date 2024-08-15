import os
import io
import torch
from pydantic import BaseModel
from PIL import Image 
import cv2
from pytorch3d.io import load_objs_as_meshes
from pytorch3d.renderer import (
    MeshRenderer, MeshRasterizer, RasterizationSettings,
    HardPhongShader, PointLights, PerspectiveCameras
)
from pytorch3d.renderer import look_at_view_transform
from torchvision.utils import save_image
from skimage.metrics import structural_similarity as ssim
import numpy as np
from fastapi import  HTTPException
from torchvision import transforms
from fastapi.responses import FileResponse
DATA_DIR = './results'


device = "cuda" if torch.cuda.is_available() else "cpu"
# Function to load an image and prepare for CLIP
def load_image(image_buffer):
    image = Image.open(image_buffer).convert("RGB")
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),  # Resize the image to match the input size expected by the model
        transforms.ToTensor(),          # Convert the image to a tensor
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # Normalize the image
    ])
    return preprocess(image).unsqueeze(0).to(device)


def render_mesh(obj_file: str, distance: float = 3.0, elevation: float = 20.0, azimuth: float = 0.0, 
                image_size: int = 512, angle_step: int = 30):
    render_images = []
    before_render = []
    try:
        # Load the mesh
        mesh = load_objs_as_meshes([obj_file], device=device)
        
        # Renderer setup
        R, T = look_at_view_transform(distance, elevation, azimuth)
        cameras = PerspectiveCameras(device=device, R=R, T=T)
        raster_settings = RasterizationSettings(
            image_size=image_size,
            blur_radius=0.0,
            faces_per_pixel=1,
        )
        lights = PointLights(device=device, location=[[2.0, 2.0, 2.0]])
        renderer = MeshRenderer(
            rasterizer=MeshRasterizer(
                cameras=cameras,
                raster_settings=raster_settings
            ),
            shader=HardPhongShader(
                device=device,
                cameras=cameras,
                lights=lights
            )
        )

        # Generate and save images
        angles = range(0, 360, angle_step)  # Angles from 0 to 330 degrees with step size
        for angle in angles:
            R, T = look_at_view_transform(distance, elevation, angle)
            cameras = PerspectiveCameras(device=device, R=R, T=T)
            renderer = MeshRenderer(
                rasterizer=MeshRasterizer(
                    cameras=cameras,
                    raster_settings=raster_settings
                ),
                shader=HardPhongShader(
                    device=device,
                    cameras=cameras,
                    lights=lights
                )
            )
            
            # Render the image
            images = renderer(mesh)
            
            # Ensure the image tensor is in the correct format
            image = images[0, ..., :3].cpu().detach()
            if image.shape[0] != 3:
                image = image.permute(2, 0, 1)  # Change shape to [C, H, W]
            
            # Ensure the image tensor is in the [0, 1] range
            image = (image - image.min()) / (image.max() - image.min())
            
            # Create a black background
            black_background = torch.zeros_like(image)
            
            # Composite the image with the black background
            alpha = images[0, ..., 3].cpu().detach()  # Extract the alpha channel
            alpha = alpha.unsqueeze(0).expand_as(image)  # Match the shape of the image
            image = image * alpha + black_background * (1 - alpha)
            
            ndarr = image.mul(255).clamp(0, 255).byte().numpy().transpose(1, 2, 0)  # Convert to [H, W, C]
            pil_image = Image.fromarray(ndarr)
            
            buffer = io.BytesIO()
            pil_image.save(buffer, format='PNG')  # Save the PIL image to the buffer
            buffer.seek(0)
            before_render.append(buffer)
            
            loaded_image = load_image(buffer)
            render_images.append(loaded_image)
            
        return render_images, before_render
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def render(
    prompt_image: str,
    id: int = 1
):
    print(f"promt_image: {prompt_image} : id={id}")
    
    # Use the uploaded objective file for rendering
    obj_file = os.path.join(DATA_DIR, f"{id}/output.obj")

    # Print the file size
    image_files = render_mesh(obj_file)
    
    print(f"output mesh:{len(image_files)}")
    if not image_files:
        raise HTTPException(status_code=500, detail="Rendering failed")
    
    return image_files
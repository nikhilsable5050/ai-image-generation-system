from PIL import Image
import torch
from diffusers import StableDiffusionPipeline

# Settings
MODEL_ID = "CompVis/stable-diffusion-v1-4"
AUTHORIZATION_TOKEN = "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"
DEVICE = torch.device("cpu")  # Use CPU instead of GPU
PROMPT = "Sunset"

def generate_image(prompt):
    try:
        # Load the model
        print("Loading the model...")
        pipe = StableDiffusionPipeline.from_pretrained(
            MODEL_ID,
            use_auth_token=AUTHORIZATION_TOKEN,
            local_files_only=False
        )

        # Disable the safety checker for faster generation
        pipe.safety_checker = None
        
        # Move the model to CPU and set data type to float32
        pipe.to(DEVICE, torch.float32)
        
        # Adjust settings for faster image generation
        pipe.scheduler.num_inference_steps = 20  # Lower number of steps for faster generation
        height, width = 256, 256  # Lower resolution for faster processing

        # Generate the image
        print("Generating the image...")
        with torch.no_grad():
            image = pipe(prompt, height=height, width=width, guidance_scale=7.5).images[0]
        
        # Save the generated image
        image_path = "sunset.png"
        image.save(image_path)
        print(f"Image generated and saved as {image_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Generate an image for the prompt
    generate_image(PROMPT)

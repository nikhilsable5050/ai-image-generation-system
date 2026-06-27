import pandas as pd
from PIL import Image
from datasets import Dataset  # type: ignore
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from torch.optim import AdamW
from torch.utils.data import DataLoader
import torch
from torchvision import transforms
from transformers import CLIPTokenizer

# Step 1: Load the CSV file and prepare dataset
df = pd.read_csv("result3.csv", sep="|", names=["image_name", "comment_number", "description"])

# Prepare the lists to hold images and descriptions
images = []
descriptions = []

# Load each image and description
for _, row in df.iterrows():
    # Construct the path to each image in the 'images' folder
    image_path = f"images/{row['image_name']}"
    description = row['description']

    print(f"Processing: {image_path}")  # Debugging line to verify paths

    try:
        # Open and convert image to RGB
        image = Image.open(image_path).convert("RGB")
        images.append(image)
        descriptions.append(description)
    except FileNotFoundError:
        print(f"Error: {image_path} not found. Skipping this file.")
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")

# Check if any images were successfully loaded
if not images:
    print("No images were loaded. Please check your file paths.")
else:
    # Create the dataset from separate lists of images and descriptions
    data = {"image": images, "text": descriptions}
    dataset = Dataset.from_dict(data)

# Step 2: Load the Stable Diffusion model
model_id = "CompVis/stable-diffusion-v1-4"
pipeline = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config)

# Move the pipeline to the appropriate device (GPU or CPU)
pipeline = pipeline.to("cuda" if torch.cuda.is_available() else "cpu")

# Step 3: Set up custom training loop and optimizer for the UNet (fine-tuning part of the model)
learning_rate = 5e-6
num_epochs = 2
batch_size = 1

# Define a DataLoader
def data_collator(batch):
    images = [item["image"] for item in batch]
    texts = [item["text"] for item in batch]
    
    # Preprocess images: Resize and normalize
    transform = transforms.Compose([
        transforms.Resize((512, 512)),  # Stable Diffusion typically expects 512x512 images
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])  # Normalize the images to [-1, 1]
    ])
    pixel_values = torch.stack([transform(image) for image in images])
    
    # Use the correct CLIP tokenizer
    tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32", use_auth_token="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")
    input_ids = tokenizer(texts, padding=True, return_tensors="pt").input_ids
    
    return {"pixel_values": pixel_values, "input_ids": input_ids}

train_dataloader = DataLoader(dataset, batch_size=batch_size, collate_fn=data_collator)

# Initialize the optimizer (train only the UNet part)
optimizer = AdamW(pipeline.unet.parameters(), lr=learning_rate)

# Step 4: Fine-tuning the UNet model (training loop)
for epoch in range(num_epochs):
    pipeline.unet.train()  # Set the UNet model in training mode
    for batch in train_dataloader:
        pixel_values = batch["pixel_values"].to("cuda" if torch.cuda.is_available() else "cpu")
        input_ids = batch["input_ids"].to("cuda" if torch.cuda.is_available() else "cpu")

        # Adjust the forward pass:
        # Use input_ids (text tokens) and pixel_values (image tensors) for training
        outputs = pipeline.vae.encode(pixel_values)  # For fine-tuning on images, use the VAE encoder
        
        # The loss will be from the output of the model (for training)
        loss = outputs.loss

        # Backward pass and optimization
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        print(f"Epoch {epoch+1}/{num_epochs}")

# Save the fine-tuned model
pipeline.save_pretrained("./stable-diffusion-model")

# Step 5: Load the fine-tuned model and test image generation
fine_tuned_pipeline = StableDiffusionPipeline.from_pretrained("./stable-diffusion-model")
fine_tuned_pipeline = fine_tuned_pipeline.to("cuda" if torch.cuda.is_available() else "cpu")

# Test generating an image from a text prompt
prompt = "A woman ventriloquist is playing with her colorful green and red dragon in a beautiful garden backdrop."
image = fine_tuned_pipeline(prompt).images[0]  # Only pass the text prompt here
image.show()  # Display the image

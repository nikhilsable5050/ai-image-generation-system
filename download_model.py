from huggingface_hub import snapshot_download

# Set your model ID and cache directory
model_id = "CompVis/stable-diffusion-v1-4"
cache_dir = "./stable-diffusion-model"  # Change this to your preferred local path

# Download the model
snapshot_download(repo_id=model_id, cache_dir=cache_dir, use_auth_token="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")

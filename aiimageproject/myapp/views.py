import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
import requests

from .models import GeneratedImage
from .forms import UserRegisterForm, LoginForm
from django.contrib.auth.decorators import login_required

from django.core.files.base import ContentFile
from urllib.parse import urlparse
import os


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('image_generator')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


# from PIL import Image
# import torch
# from diffusers import StableDiffusionPipeline

# FLASK_API_URL = "https://suppliers-elsewhere-distinguished-billy.trycloudflare.com/generate-image"

# from django.core.files.base import ContentFile
# from urllib.parse import urlparse
# import os
# import requests
# from .models import GeneratedImage  # Assuming GeneratedImage model is in the same app

# @login_required
# def image_generator_view(request):
#     if request.method == 'POST':
#         object_name = request.POST.get('object_name')
#         object_description = request.POST.get('object_description')

#         # Prepare data to send to Flask API
#         data = {
#             "prompt": object_description  # Send the description as the prompt for the image
#         }

#         try:
#             # Make a POST request to the Flask API
#             response = requests.post(FLASK_API_URL, json=data)

#             # Check if the response is successful
#             if response.status_code == 200:
#                 # Assuming the response contains the image URL or path
#                 image_relative_url = response.json().get("image_url")  # Assuming the API returns a relative path

#                 # Prepend the base URL to the relative image URL
#                 base_url = "https://suppliers-elsewhere-distinguished-billy.trycloudflare.com"  # Replace with your actual base URL
#                 generated_image_url = base_url + image_relative_url
#                 print("Generated Image URL:", generated_image_url)

#                 # Download the image from the URL
#                 image_response = requests.get(generated_image_url)
#                 if image_response.status_code == 200:
#                     # Extract image name from URL
#                     parsed_url = urlparse(generated_image_url)
#                     image_name = os.path.basename(parsed_url.path)

#                     # Save the image to the database
#                     generated_image = GeneratedImage(
#                         object_name=object_name,
#                         object_description=object_description,
#                         generated_image_url=generated_image_url
#                     )
#                     generated_image.image.save(image_name, ContentFile(image_response.content))
#                     generated_image.save()
                    
#                     return render(request, 'image_generator.html', {
#                         'object_name': object_name,
#                         'object_description': object_description,
#                         'generated_images': [
#                             {
#                                 'object_name': object_name,
#                                 'object_description': object_description,
#                                 'generated_image_url': generated_image_url,
#                                 'image': generated_image.image.url  # Use this for displaying the saved image
#                             }
#                         ]
#                     })
#                 else:
#                     # Handle image download failure
#                     return render(request, 'image_generator.html', {
#                         'error': "Failed to download the image. Please try again."
#                     })
#             else:
#                 # Handle errors (e.g., log the error or return a failure message)
#                 return render(request, 'image_generator.html', {
#                     'error': "Failed to generate image. Please try again."
#                 })

#         except requests.exceptions.RequestException as e:
#             # Handle exception if the request fails
#             return render(request, 'image_generator.html', {
#                 'error': f"An error occurred: {e}"
#             })

#     return render(request, 'image_generator.html')

import os
import requests
from urllib.parse import urlparse
from django.shortcuts import render
from django.core.files.base import ContentFile
from django.conf import settings
from .models import GeneratedImage
from django.contrib.auth.decorators import login_required

# Define the URL for the Flask APIoudflare.com
FLASK_API_URL = " https://alleged-electronic-casa-muze.trycloudflare.com/generate-image"

@login_required
def image_generator_view(request):
    if request.method == 'POST':
        object_name = request.POST.get('object_name')
        object_description = request.POST.get('object_description')

        # Prepare data to send to Flask API
        data = {
            "prompt": object_description  # Send the description as the prompt for the image
        }

        generated_images = []  # List to store details of all generated images

        try:
            for i in range(4):  # Generate 4 images
                # Make a POST request to the Flask API
                response = requests.post(FLASK_API_URL, json=data)

                # Check if the response is successful
                if response.status_code == 200:
                    # Assuming the response contains the image URL or path
                    image_relative_url = response.json().get("image_url")  # Assuming the API returns a relative path

                    # Prepend the base URL to the relative image URL
                    base_url = " https://alleged-electronic-casa-muze.trycloudflare.com"  # Replace with your actual base URL
                    generated_image_url = base_url + image_relative_url
                    print(f"Generated Image URL ({i+1}):", generated_image_url)

                    # Download the image from the URL
                    image_response = requests.get(generated_image_url)
                    if image_response.status_code == 200:
                        # Extract image name from URL
                        parsed_url = urlparse(generated_image_url)
                        image_name = os.path.basename(parsed_url.path)

                        # Specify the folder where images will be saved
                        download_folder = 'download_images'

                        # Ensure the folder exists
                        download_path = os.path.join(settings.MEDIA_ROOT, download_folder)
                        os.makedirs(download_path, exist_ok=True)

                        # Full path to save the image (in download_images folder)
                        image_path = os.path.join(download_path, image_name)

                        # Save the image to the filesystem
                        with open(image_path, 'wb') as image_file:
                            image_file.write(image_response.content)

                        # Save the image details to the database
                        generated_image = GeneratedImage(
                            object_name=f"{object_name}_{i+1}",  # Unique name for each image
                            object_description=object_description,
                            generated_image_url=generated_image_url
                        )

                        # Update the image field with the relative path of the saved image
                        generated_image.image.name = os.path.join(download_folder, image_name)
                        generated_image.save()

                        # Add image details to the list to render on the frontend
                        generated_images.append({
                            'object_name': f"{object_name}_{i+1}",
                            'object_description': object_description,
                            'generated_image_url': generated_image_url,
                            'image_name': image_name,  # Add image_name here
                            'image': generated_image.image.url  # Use this for displaying the saved image
                        })
                    else:
                        print(f"Failed to download image ({i+1}).")
                        return render(request, 'image_generator.html', {
                            'error': f"Failed to download image {i+1}. Please try again."
                        })
                else:
                    print(f"Failed to generate image ({i+1}).")
                    return render(request, 'image_generator.html', {
                        'error': f"Failed to generate image {i+1}. Please try again."
                    })

            # Render the template with all generated images
            return render(request, 'image_generator.html', {
                'object_name': object_name,
                'object_description': object_description,
                'generated_images': generated_images  # Contains image_name for each image
            })

        except requests.exceptions.RequestException as e:
            # Handle exception if the request fails
            return render(request, 'image_generator.html', {
                'error': f"An error occurred: {e}"
            })

    return render(request, 'image_generator.html')


import os
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import GeneratedImage

def download_image(request, image_name):
    # Fetch the image from the GeneratedImage model using the object_name
    # generated_image = get_object_or_404(GeneratedImage, object_name=image_name)

    # Construct the full path to the image file relative to MEDIA_ROOT
    image_path = os.path.join(settings.MEDIA_ROOT, 'download_images', image_name)  # Adjusted path

    print(image_path);
    if os.path.exists(image_path):
        # Open the image and return it as a response
        with open(image_path, 'rb') as img:
            response = HttpResponse(img.read(), content_type='image/png')  # Use the correct content type for PNG images
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(image_name)}"'  # Forces download
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # Prevent caching
            response['Pragma'] = 'no-cache'  # Prevent caching in older HTTP/1.0 proxies
            response['Expires'] = '0'  # Forces the browser to fetch a fresh copy
            
            return response
    else:
        return HttpResponse('Image not found', status=404)

def logout_view(request):
    logout(request)
    return redirect('login')

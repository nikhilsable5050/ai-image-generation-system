from django.shortcuts import render


def home(request):
    image_url = 'https://in.images.search.yahoo.com/search/images;_ylt=AwrKEbUZmjlngQIAKU67HAx.;_ylu=Y29sbwNzZzMEcG9zAzEEdnRpZAMEc2VjA3BpdnM-?p=home+page+for+ai+image+generator&fr2=piv-web&type=E211IN714G0&fr=mcafee#id=15&iurl=https%3A%2F%2Fwww.weetechsolution.com%2Fwp-content%2Fuploads%2F2023%2F01%2Fimgpsh_fullsize_anim-4.jpg&action=click'  # Update this to your actual image URL or dynamically generated path

    return render(request, 'home.html', {'background_image_url': image_url})
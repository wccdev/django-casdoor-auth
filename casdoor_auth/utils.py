import requests
from django.core.files.base import ContentFile


def save_avatar_from_url(user, url):
    response = requests.get(url)
    if response.status_code != 200:
        print("downloading avatars failed")
        return

    # Assume the avatar is a .jpg
    user.avatar.save(f'{user.pk}.jpg', ContentFile(response.content), save=True)

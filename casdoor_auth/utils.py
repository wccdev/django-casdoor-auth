import os
import requests
import urllib.parse
from django.core.files.base import ContentFile


def save_avatar_from_url(user, url):
    parsed_url = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed_url.path)
    file_ext = os.path.splitext(filename)[1]

    if filename == "casbin.svg":
        return

    response = requests.get(url)
    if response.status_code != 200:
        print("downloading avatars failed")
        return

    user.avatar.save(f"{user.pk}{file_ext}", ContentFile(response.content), save=True)

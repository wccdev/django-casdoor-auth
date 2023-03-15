# Copyright 2022 The Casdoor Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from casdoor import CasdoorSDK
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.shortcuts import redirect


User = get_user_model()

conf = settings.CASDOOR_CONFIG

sdk = CasdoorSDK(conf.get('endpoint'),
                 conf.get('client_id'),
                 conf.get('client_secret'),
                 conf.get('certificate'),
                 conf.get('org_name'),
                 conf.get('application_name'),
                 conf.get('endpoint'))


def toLogin(request):
    redirect_url = sdk.get_auth_link(redirect_uri=settings.REDIRECT_URI)
    return redirect(redirect_url)


def callback(request):
    code = request.GET.get('code')
    token = sdk.get_oauth_token(code)
    user = sdk.parse_jwt_token(token)
    request.session['user'] = user
    email = user.get('email')
    username = user.get('name')
    in_user = None
    if email:
        try:
            in_user = User.objects.get(email=user.get('email'))
        except User.MultipleObjectsReturned:
            raise ValueError(f"Multiple emails found: {email}")

    if not in_user and username:
        try:
            in_user = User.objects.get(username=username)
        except User.MultipleObjectsReturned:
            raise ValueError(f"Multiple username found: {username}")

    if not in_user:
        in_user = User.objects.create_user(username, email=email)

    login(request, in_user)
    return redirect(settings.LOGIN_REDIRECT_URL)

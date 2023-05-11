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
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt


User = get_user_model()

conf = settings.CASDOOR_CONFIG

sdk = CasdoorSDK(conf.get('endpoint'),
                 conf.get('client_id'),
                 conf.get('client_secret'),
                 conf.get('certificate'),
                 conf.get('org_name'),
                 conf.get('application_name'),
                 conf.get('endpoint'))


@csrf_exempt
def to_login(request):
    redirect_url = sdk.get_auth_link(redirect_uri=settings.REDIRECT_URI)
    return redirect(redirect_url)


@csrf_exempt
def to_logout(request):
    id_token = request.session.get('casdoor_token')
    logout(request)
    redirect_url = sdk.get_auth_link(redirect_uri=settings.REDIRECT_URI)
    logout_url = f"{sdk.front_endpoint}/api/logout?id_token_hint={id_token}&post_logout_redirect_uri={redirect_url}"
    return redirect(logout_url)


@csrf_exempt
def callback(request):
    code = request.GET.get('code')
    token = sdk.get_oauth_token(code)
    if isinstance(token, dict):
        access_token = token.get("access_token")

    user = sdk.parse_jwt_token(access_token)
    request.session['user'] = user
    email = user.get('email')
    username = user.get('name')
    display_name = user.get('displayName', username)
    is_admin = user.get('isAdmin', False)
    in_user = None
    if email:
        try:
            in_user = User.objects.get(email=user.get('email'))
        except User.MultipleObjectsReturned:
            raise ValueError(f"Multiple emails found: {email}")
        except User.DoesNotExist:
            pass

    if not in_user and username:
        try:
            in_user = User.objects.get(username=username)
        except User.MultipleObjectsReturned:
            raise ValueError(f"Multiple username found: {username}")
        except User.DoesNotExist:
            pass

    if not in_user:
        extra_fields = dict(is_superuser=is_admin, is_staff=is_admin)
        in_user = User.objects.create_user(username, email=email, name=display_name, **extra_fields)

    login(request, in_user)
    request.session['casdoor_token'] = token

    redirect_url = settings.LOGIN_REDIRECT_URL + f"?username={in_user.username}"
    return redirect(redirect_url)


@csrf_exempt
def callback_no_redirect(request):
    code = request.GET.get('code')
    token = sdk.get_oauth_token(code)
    if isinstance(token, dict):
        access_token = token.get("access_token")

    user = sdk.parse_jwt_token(access_token)
    request.session['user'] = user
    email = user.get('email')
    username = user.get('name')
    display_name = user.get('displayName', username)
    is_admin = user.get('isAdmin', False)
    in_user = None
    if email:
        try:
            in_user = User.objects.get(email=user.get('email'))
        except User.MultipleObjectsReturned:
            raise ValueError(f"Multiple emails found: {email}")
        except User.DoesNotExist:
            pass

    if not in_user and username:
        try:
            in_user = User.objects.get(username=username)
        except User.MultipleObjectsReturned:
            raise ValueError(f"Multiple username found: {username}")
        except User.DoesNotExist:
            pass

    if not in_user:
        extra_fields = dict(is_superuser=is_admin, is_staff=is_admin)
        in_user = User.objects.create_user(username, email=email, name=display_name, **extra_fields)

    login(request, in_user)
    request.session['casdoor_token'] = token
    return HttpResponse("ok")


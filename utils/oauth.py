import constants
import requests


def get_facebook_avatar(fb_id):
    try:
        fb_avatar_url = constants.FACEBOOK_AVATAR_URL.format(fb_id)
        response = requests.get(fb_avatar_url)
        if response.status_code == 200:
            fb_avatar_name = response.url.split('/')[-1]
            # fp = BytesIO()
            # fp.write(response.content)
            return fb_avatar_name, response.content
    except:
        pass
    return None, None


def get_vk_web_info(access_token):
    try:
        response = requests.get(constants.VK_WEB_INFO_URL.format(access_token))
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(e)
        return None


def get_facebook_info(access_token):
    try:
        request_url = constants.FACEBOOK_INFO_URL.format(access_token)
        response = requests.get(request_url)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None


def get_google_info(access_token):
    try:
        request_url = constants.GOOGLE_INFO_URL_V3.format(access_token)
        response = requests.get(request_url)
        if response.status_code == 200:
            return response.json()
    except:
        return None


def get_social_info(body, social_type):
    access_token = body['access_token']
    result = {
        'social_type': social_type,
        'social_id': None,
        'full_name': '',
        'email': None,
        'phone': None,
        'avatar_url': None,
    }
    if social_type == constants.FACEBOOK:
        info = get_facebook_info(access_token)
        if info:
            result['social_id'] = info['id']
            result['full_name'] = info.get('name', '')
            result['first_name'] = info.get('first_name', '')
            result['last_name'] = info.get('last_name', '')
            result['email'] = info.get('email')
            result['phone'] = info.get('phone') # not given
            result['avatar_url'] = constants.FACEBOOK_AVATAR_URL.format(info['id'])
            return result, None
    elif social_type == constants.VK_WEB:
        result['social_id'] = body['user_id']
        result['first_name'] = body['first_name']
        result['last_name'] = body['last_name']
        result['full_name'] = '{} {}'.format(body['first_name'],
                                             body['last_name'])
        result['gender'] = body.get('gender')
        result['email'] = body.get('email') # not given
        result['phone'] = body.get('phone') # not given
        result['avatar_url'] = body.get('avatar_url')
        return result, None
    elif social_type == constants.GOOGLE:
        info = get_google_info(access_token)
        if info:
            result['social_id'] = info['email']
            result['full_name'] = info.get('name') # not given
            result['first_name'] = info.get('given_name')
            result['last_name'] = info.get('family_name')
            result['email'] = info['email']
            result['phone'] = info.get('phone') # not given
            result['avatar_url'] = info.get('picture')
            return result, None
    return None, constants.RESPONSE_SOCIAL_TOKEN_INVALID

from login.models import User


def header_avatar(request):
    username = request.session.get('username')
    if not username:
        return {}
    user = User.objects.filter(username=username).first()
    if not user:
        return {}
    data = {'header_is_admin': user.user_level == 1}
    if user.avatar:
        data['header_avatar_url'] = user.avatar.url
    return data
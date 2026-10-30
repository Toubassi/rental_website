from login.models import User


def header_avatar(request):
    username = request.session.get('username')
    if not username:
        return {}
    user = User.objects.filter(username=username).first()
    if user and user.avatar:
        return {'header_avatar_url': user.avatar.url}
    return {}
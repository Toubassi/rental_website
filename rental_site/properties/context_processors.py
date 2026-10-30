from .models import UserProfile


def header_avatar(request):
    username = request.session.get('username')
    if not username:
        return {}
    profile = UserProfile.objects.filter(user__username=username).first()
    if profile and profile.avatar:
        return {'header_avatar_url': profile.avatar.url}
    return {}
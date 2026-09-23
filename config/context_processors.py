from django.conf import settings


def site_links(request):
    return {
        'INSTAGRAM_URL': settings.INSTAGRAM_URL,
    }

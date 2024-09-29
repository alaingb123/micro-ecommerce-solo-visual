from . import settings

def global_settings(request):

    return {

        'PRIMARY_COLOR': '#003366',
        'site_key': settings.RECAPTCHA_SITE_KEY,
        'SECONDARY_COLOR': '#FF6600'
    }
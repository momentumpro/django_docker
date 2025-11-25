def google_provider_enabled(request):
    """Context processor para verificar si Google OAuth está configurado"""
    try:
        from allauth.socialaccount.models import SocialApp
        return {
            'google_provider_enabled': SocialApp.objects.filter(provider='google').exists()
        }
    except Exception:
        # Si hay algún error (DB no disponible, etc.), retornar False
        return {'google_provider_enabled': False}


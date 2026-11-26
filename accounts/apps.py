from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Disconnect default update_last_login to protect against read-only database errors
        # on serverless environments; wrap with fail-safe error handling.
        from django.contrib.auth.signals import user_logged_in
        from django.contrib.auth.models import update_last_login
        try:
            user_logged_in.disconnect(update_last_login, dispatch_uid='update_last_login')
        except Exception:
            pass

        def safe_update_last_login(sender, user, **kwargs):
            try:
                update_last_login(sender, user, **kwargs)
            except Exception:
                pass

        user_logged_in.connect(safe_update_last_login, dispatch_uid='safe_update_last_login')

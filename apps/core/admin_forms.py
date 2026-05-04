from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


ADMIN_USERNAME = "admin"


class AdminOnlyAuthenticationForm(AdminAuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields["username"].label = "Логин администратора"
        self.fields["username"].widget.attrs["placeholder"] = ADMIN_USERNAME

    def clean(self):
        username = (self.cleaned_data.get("username") or "").strip()
        password = self.cleaned_data.get("password")

        if username and password:
            if username != ADMIN_USERNAME:
                raise ValidationError(
                    _("В админ-панель может войти только пользователь admin."),
                    code="invalid_login",
                )

            User = get_user_model()
            admin_user = User.objects.filter(username=ADMIN_USERNAME).first()
            if not admin_user:
                raise ValidationError(
                    _("Пользователь admin не найден."),
                    code="invalid_login",
                )

            self.user_cache = authenticate(
                self.request,
                username=admin_user.email,
                password=password,
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.username != ADMIN_USERNAME or not user.is_staff or not user.is_superuser:
            raise ValidationError(
                _("В админ-панель может войти только пользователь admin."),
                code="invalid_login",
            )

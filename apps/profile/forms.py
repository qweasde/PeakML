from django import forms

from .models import SiteUser


class SiteUserSignupForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(), label="Пароль")
    password2 = forms.CharField(widget=forms.PasswordInput(), label="Повтори пароль")

    class Meta:
        model = SiteUser
        fields = ("full_name", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if SiteUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            self.add_error("password2", "Пароли не совпадают.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class SiteUserLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput(), label="Пароль")

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = (cleaned_data.get("email") or "").strip().lower()
        password = cleaned_data.get("password")
        if email and password:
            try:
                user = SiteUser.objects.get(email=email, is_active=True)
            except SiteUser.DoesNotExist:
                raise forms.ValidationError("Неверный email или пароль.")
            if not user.check_password(password):
                raise forms.ValidationError("Неверный email или пароль.")
            self.user = user
        return cleaned_data


class SiteUserProfileForm(forms.ModelForm):
    class Meta:
        model = SiteUser
        fields = ("full_name", "email", "age", "gender", "player_role", "phone", "avatar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "full_name": "Иванов Иван Иванович",
            "email": "you@example.com",
            "age": "18",
            "phone": "+7 900 123-45-67",
        }
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-input"
            if name in placeholders:
                field.widget.attrs["placeholder"] = placeholders[name]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = SiteUser.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

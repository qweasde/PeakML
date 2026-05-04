from allauth.account.forms import SignupForm
from django import forms


class CustomSignupForm(SignupForm):
    full_name = forms.CharField(
        max_length=255,
        label="ФИО",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Иванов Иван Иванович",
                "autocomplete": "name",
            }
        ),
    )

    def save(self, request):
        user = super().save(request)
        user.full_name = self.cleaned_data["full_name"].strip()
        user.save(update_fields=["full_name"])
        return user

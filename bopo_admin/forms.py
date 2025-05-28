# forms.py

from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError

class CustomSetPasswordForm(SetPasswordForm):
    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        user = self.user

        # Skip password validators for corporate users, only allow 4-digit PIN
        if hasattr(user, 'corporate') and user.corporate:
            if not password1.isdigit() or len(password1) != 4:
                raise ValidationError("PIN must be exactly 4 digits.")
            return password1  # no further validation

        # For others, use default validation
        return super().clean_new_password1()

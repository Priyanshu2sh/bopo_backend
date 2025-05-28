# forms.py

# from django.contrib.auth.forms import SetPasswordForm
# from django.core.exceptions import ValidationError

# class CustomSetPasswordForm(SetPasswordForm):
#     def clean_new_password1(self):
#         password1 = self.cleaned_data.get('new_password1')
#         user = self.user

#         # Skip password validators for corporate users, only allow 4-digit PIN
#         if hasattr(user, 'corporate') and user.corporate:
#             if not password1.isdigit() or len(password1) != 4:
#                 raise ValidationError("PIN must be exactly 4 digits.")
#             return password1  # no further validation

#         # For others, use default validation
#         return super().clean_new_password1()

#for custom password reset form with user type context
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class CustomSetPasswordForm(SetPasswordForm):
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')

        user = self.user

        # Custom validation for corporate users
        if hasattr(user, 'corporate') and user.corporate:
            if not password1 or not password1.isdigit() or len(password1) != 4:
                raise ValidationError("PIN must be exactly 4 digits.")
        else:
            # Run Django's default password validators
            validate_password(password1, user)

        return cleaned_data

# for sending password reset emails with user type context
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.core.mail import send_mail

class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        user = context.get('user')
        user_type = 'other'
        if hasattr(user, 'corporate') and user.corporate:
            user_type = 'corporate'
        elif hasattr(user, 'employee') and user.employee:
            user_type = 'employee'
        elif user.is_superuser:
            user_type = 'superadmin'

        context['user_type'] = user_type

        subject = render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())  # Remove newlines from subject
        body = render_to_string(email_template_name, context)

        send_mail(subject, body, from_email, [to_email], html_message=None)

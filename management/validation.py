from django.contrib.auth.password_validation import MinimumLengthValidator
from django.core.exceptions import ValidationError
#from django.utils.translation import ugettext as _
from django.utils.translation import gettext as _, ngettext


class CustomPasswordValidator():

    def __init__(self, min_length=8):
        self.min_length = min_length
        self.min_number = 1

    def validate(self, password, user=None):
        special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
        if len(password) < 8:
            raise ValidationError(_("Password must contain at least %(min_length)d characters.") % {'min_length': self.min_length})
        if (not any(char.isdigit() for char in password)):
            raise ValidationError(_('Password must contain at least %(min_number)d digit.') % {'min_number': self.min_number})
        if (not any(char.isalpha() for char in password)):
            raise ValidationError(_('Password must contain at least %(min_number)d letter.') % {'min_number': self.min_number})
        if (not any(char in special_characters for char in password)):
            raise ValidationError(_('Password must contain at least %(min_number)d special character.') % {'min_number': self.min_number})

    def get_help_text(self):
        return ""
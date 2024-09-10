from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Report
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from .models import studRec

from .models import UserProfile 



# Register admin

class CreateAdminForm(UserCreationForm):
    picture = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'placeholder': 'Upload profile picture'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}), label='Email')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define icon HTML here
        icons = {
            'first_name': '<i class="fa fa-user"></i> ',
            'last_name': '<i class="fa fa-user"></i> ',
            'username': '<i class="fa fa-user"></i> ',
            'email': '<i class="fa fa-envelope"></i> ',
            'password1': '<i class="fa fa-lock"></i> ',
            'password2': '<i class="fa fa-lock"></i> ',
        }
        for field_name, field in self.fields.items():
            if field_name in icons:
                # Update the label with icon
                field.label = f'{icons[field_name]} {field.label}'
# Login Admin


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_username',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_password',
            'placeholder': 'Password'
        })
    )

# Form for creating a new record
class CreateRecordForm(forms.ModelForm):
  

    class Meta:
        model = studRec
        fields = [
            'student_id',
            'first_name',
            'middle_name',
            'last_name',
            'suffix',
            'course',
            'major',
            'rfid_number',
            'picture',  # Include the picture field for image uploads
            
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student_id'].required = True
        self.fields['student_id'].label = ""
        self.fields['student_id'].widget.attrs.update({'placeholder': 'Enter Student ID'})
        self.fields['first_name'].required = True
        self.fields['first_name'].label = ""
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Enter First Name'})
        self.fields['middle_name'].required = False  # Middle name is optional
        self.fields['middle_name'].label = ""
        self.fields['middle_name'].widget.attrs.update({'placeholder': 'Enter Middle Name'})
        self.fields['last_name'].required = True
        self.fields['last_name'].label = ""
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Enter Last Name'})
        self.fields['suffix'].required = False
        self.fields['suffix'].label = ""
        self.fields['suffix'].widget.attrs.update({'placeholder': 'Enter Suffix'})
        self.fields['course'].required = True
        self.fields['course'].label = ""
        self.fields['course'].widget.attrs.update({'placeholder': 'Select Course'})
        self.fields['major'].required = True
        self.fields['major'].label = ""
        self.fields['major'].widget.attrs.update({'placeholder': 'Select Major'})
        self.fields['rfid_number'].required = True
        self.fields['rfid_number'].label = ""
        self.fields['rfid_number'].widget.attrs.update({'placeholder': 'Enter RFID Number'})
        self.fields['picture'].required = True
        self.fields['picture'].label = ""




class StudRecForm(forms.ModelForm):
    class Meta:
        model = studRec  # Assuming 'PendingRequests' is the model for the form
        fields = [
            'student_id',
            'first_name',
            'middle_name',
            'last_name',
            'suffix',
            'course',
            'major',
            'picture',
            'email',      # Include the email field
            'password',   # Include the password field
        ]
        widgets = {
            'password': forms.PasswordInput(),  # Use a PasswordInput widget for password
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student_id'].required = True
        self.fields['student_id'].label = ""
        self.fields['student_id'].widget.attrs.update({'placeholder': 'Enter Student ID'})

        self.fields['first_name'].required = True
        self.fields['first_name'].label = ""
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Enter First Name'})

        self.fields['middle_name'].required = False
        self.fields['middle_name'].label = ""
        self.fields['middle_name'].widget.attrs.update({'placeholder': 'Enter Middle Name'})

        self.fields['last_name'].required = True
        self.fields['last_name'].label = ""
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Enter Last Name'})

        self.fields['suffix'].required = False
        self.fields['suffix'].label = ""
        self.fields['suffix'].widget.attrs.update({'placeholder': 'Enter Suffix'})

        self.fields['course'].required = True
        self.fields['course'].label = ""
        self.fields['course'].widget.attrs.update({'placeholder': 'Select Course'})

        self.fields['major'].required = True
        self.fields['major'].label = ""
        self.fields['major'].widget.attrs.update({'placeholder': 'Select Major'})

        self.fields['picture'].required = True
        self.fields['picture'].label = ""

        # Email field
        self.fields['email'].required = True
        self.fields['email'].label = ""
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter Email'})

        # Password field
        self.fields['password'].required = True
        self.fields['password'].label = ""
        self.fields['password'].widget.attrs.update({'placeholder': 'Enter Password'})


# Form for updating an existing record
class UpdateRecordForm(forms.ModelForm):
    class Meta:
        model = studRec
        fields = [
            'student_id',
            'first_name',
            'middle_name',  # Add middle name
            'last_name',
            'suffix',
            'course',
            'major',
            'rfid_number',
            'picture',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student_id'].required = True
        self.fields['student_id'].label = ""
        self.fields['student_id'].widget.attrs.update({'placeholder': 'Enter Student ID'})
        self.fields['first_name'].required = True
        self.fields['first_name'].label = ""
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Enter First Name'})
        self.fields['middle_name'].required = False  # Middle name is optional
        self.fields['middle_name'].label = ""
        self.fields['middle_name'].widget.attrs.update({'placeholder': 'Enter Middle Name'})
        self.fields['last_name'].required = True
        self.fields['last_name'].label = ""
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Enter Last Name'})
        self.fields['suffix'].required = False
        self.fields['suffix'].label = ""
        self.fields['suffix'].widget.attrs.update({'placeholder': 'Enter Suffix'})
        self.fields['course'].required = True
        self.fields['course'].label = ""
        self.fields['course'].widget.attrs.update({'placeholder': 'Select Course'})
        self.fields['major'].required = True
        self.fields['major'].label = ""
        self.fields['major'].widget.attrs.update({'placeholder': 'Select Major'})
        self.fields['rfid_number'].required = True
        self.fields['rfid_number'].label = ""
        self.fields['rfid_number'].widget.attrs.update({'placeholder': 'Enter RFID Number'})
        self.fields['picture'].required = True
        self.fields['picture'].label = ""
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['rfid_loss_date', 'report_content']
        widgets = {
            'rfid_loss_date': forms.DateInput(attrs={'type': 'date'}),
        }
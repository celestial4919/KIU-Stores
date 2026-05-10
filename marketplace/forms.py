from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Product
from .models import BusinessApplication

# ADD THIS PART HERE:
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class StudentSignUpForm(UserCreationForm):
    # We make email required and give it a clean look
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'placeholder': 'University Email', 'style': 'width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ddd;'})
    )
    
    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Phone (e.g. +256...)', 'style': 'width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ddd;'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # These are the fields that will appear on the signup card
        fields = ("username", "email", "phone_number", "is_student_seller")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply styling to all fields automatically
        for field in self.fields:
            if field != 'is_student_seller':
                self.fields[field].widget.attrs.update({
                    'style': 'width: 100%; padding: 12px; border: 1px solid #dfe6e9; border-radius: 8px; box-sizing: border-box; outline: none; background: #fafafa;'
                })
            else:
                # Add a class just for the checkbox so it doesn't look weird
                self.fields[field].widget.attrs.update({'class': 'form-check-input'})



class ProductForm(forms.ModelForm):
    # This extra field allows selecting multiple files at once
    extra_images = MultipleFileField(
        required=False,
        help_text="You can select multiple images at once",
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'style': 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px;'
        })
    )
    class Meta:
        model = Product
        fields = ['title', 'category', 'description', 'price', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your item in detail...'}),
            'price': forms.NumberInput(attrs={'placeholder': 'UGX'}),
        }



class BusinessOnboardingForm(forms.ModelForm):
    class Meta:
        model = BusinessApplication
        fields = ['business_name', 'business_specialty', 'physical_location', 'merchant_code']
        widgets = {
            'business_name': forms.TextInput(attrs={'style': 'width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 15px;'}),
            'business_specialty': forms.TextInput(attrs={'placeholder': 'e.g. Campus Bites', 'style': 'width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 15px;'}),
            'physical_location': forms.TextInput(attrs={'style': 'width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 15px;'}),
            'merchant_code': forms.TextInput(attrs={'placeholder': 'Enter your 6-digit Merchant Code', 'style': 'width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ddd;'}),
        }

# Create a small custom field that handles multiple files
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
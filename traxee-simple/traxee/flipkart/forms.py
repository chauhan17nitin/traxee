from django import forms

class UserForm(forms.Form):

    name = forms.CharField(max_length=30)
    email = forms.CharField(max_length=30, widget = forms.EmailInput)  
    password = forms.CharField(widget = forms.PasswordInput)
    class Meta:
        fields = ['name', 'email', 'password']

# class HandlerForm(forms.ModelForm):

#     class Meta:
#         model = Handlers
#         fields = ['handle', 'handler_name']

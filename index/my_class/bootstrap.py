"""
自定义form类
"""
from django import forms

class BootstrapModelForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        for name,field in self.fields.items():
            if (name == 'password') and hasattr(field.widget, 'input_type'):
                field.widget.input_type = 'password'
            if field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.label
            else:
                field.widget.attrs = {
                    'class':'form-control',
                    'placeholder':field.label,
                }

class BootstrapForm(forms.Form):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        for name,field in self.fields.items():
            if (name == 'password') and hasattr(field.widget, 'input_type'):
                field.widget.input_type = 'password'
            if field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.label
            else:
                field.widget.attrs = {
                    'class':'form-control',
                    'placeholder':field.label,
                }



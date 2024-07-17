from django import forms

class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        coerce=int,
        widget=forms.Select,
    )
    update = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        available_quantity = kwargs.pop('available_quantity', 1)  # Извлекаем available_quantity из kwargs
        super().__init__(*args, **kwargs)
        self.fields['quantity'].choices = [(i, str(i)) for i in range(1, available_quantity + 1)]
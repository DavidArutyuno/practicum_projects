from django import forms


from .models import Post, User, Comment


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        """Обновление стилей формы под bootstrap."""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    def clean(self):
        """Проверка email на уникальность."""
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if (email
                and User.objects.filter(email=email).exclude(
                    username=username).exists()):
            raise forms.ValidationError('Email адрес должен быть уникальным')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%d %H:%M',
                attrs={
                    'type': 'datetime-local'
                }
            )
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Текст:'}
            )
        }

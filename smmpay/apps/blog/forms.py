from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'content': CKEditorUploadingWidget()
        }
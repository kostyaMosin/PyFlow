from django import forms


class PostForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)
    content_code = forms.CharField(widget=forms.Textarea)
    tags = forms.CharField()


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)

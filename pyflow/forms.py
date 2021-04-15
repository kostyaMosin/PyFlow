from django import forms


class PostForm(forms.Form):
    title = forms.CharField(required=False)
    content = forms.CharField(widget=forms.Textarea, required=False)
    content_code = forms.CharField(widget=forms.Textarea, required=False)
    tags = forms.CharField(required=False)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError('This field is empty')
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content:
            raise forms.ValidationError('This field is empty')
        return content

    def clean_content_code(self):
        content_code = self.cleaned_data.get('content_code')
        if not content_code:
            raise forms.ValidationError('This field is empty')
        return content_code

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if not tags:
            raise forms.ValidationError('This field is empty')
        return tags


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea, required=False)

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if not comment:
            raise forms.ValidationError('This field is empty')
        return comment


class SendEmailForm(forms.Form):
    receiver = forms.EmailField(required=False)
    topic = forms.CharField(required=False)

    def clean_receiver(self):
        receiver = self.cleaned_data.get('receiver')
        if not receiver:
            raise forms.ValidationError('This field is empty')
        return receiver

    def clean_topic(self):
        topic = self.cleaned_data.get('topic')
        if not topic:
            raise forms.ValidationError('This field is empty')
        return topic


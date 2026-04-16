from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Message

# メッセージ投稿フォームとユーザー登録フォームを定義
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']

# ユーザー登録フォーム
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    # ユーザー名の重複をチェック
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("このユーザー名は既に使用されています。")
        return username    
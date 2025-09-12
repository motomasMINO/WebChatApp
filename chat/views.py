from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import Message
from .forms import MessageForm

@login_required
def chat_room(request):
    # ユーザーの最終アクティブ時間を更新
    request.user.last_login = timezone.now()
    request.user.save(update_fields=["last_login"])

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.save()
            return redirect('chat:room')
    else:
        form = MessageForm()
    
    messages = Message.objects.order_by('-timestamp')[:20] # 最新20件

    # "5分以内にアクセスのあったユーザー" をオンラインとみなす
    online_threshold = timezone.now() - timedelta(minutes=5)
    online_count = User.objects.filter(last_login__gte=online_threshold).count()

    return render(request, 'chat/chat_room.html', {'form': form, 'messages': reversed(messages), 'online_count': online_count,})

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.user == request.user: # メッセージの所有者のみ削除可能
        message.delete()
    else:
        messages.error(request, 'このメッセージを削除する権限がありません')
    return redirect('chat:room')

@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'アカウントを削除しました')
        return redirect('chat:login')
    return render(request, 'chat/delete_account.html')

@login_required
def fetch_messages(request):
    messages = Message.objects.all().order_by("timestamp")
    data = [
        {
            "id": msg.id,
            "user": msg.user.username,
            "content": msg.content,
            "timestamp": msg.timestamp.strftime("%Y/%m/%d %H:%M"),
        }
        for msg in messages
    ]
    return JsonResponse(data, safe=False)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('chat:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'chat/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # ユーザー名が存在するかをチェック
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'ユーザー名が存在しません')
            return render(request, 'chat/login.html')

        # 認証
        user = authenticate(request, username=username, password=password)
        if user:
            # 既にログイン中か確認
            active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
            for session in active_sessions:
                data = session.get_decoded()
                if data.get('_auth_user_id') == str(user.id):
                    messages.error(request, 'このアカウントはログイン中です')
                    return render(request, 'chat/login.html')

            # ログイン実行
            login(request, user)
            return redirect('chat:room')
        else:
            messages.error(request, 'ユーザー名またはパスワードが違います')
    return render(request, 'chat/login.html')

def logout_view(request):
    logout(request)
    return redirect('chat:login')
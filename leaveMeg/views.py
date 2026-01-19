from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
import json
from django import forms
from index.my_class.bootstrap import BootstrapModelForm
from leaveMeg import models
from index.my_class.pagination import MyPage
from index.models import User
from leaveMeg.models import Comment 
import os
from django.conf import settings

class DmForm(BootstrapModelForm):
    class Meta:
        model = models.LeaveMeg
        fields = '__all__'
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'danmu-input',
                'placeholder': '输入你的弹幕内容...',
                'maxlength': '200'
            })
        }


def meg(request):
    form = DmForm()
    # 获取留言数据
    comments = models.Comment.objects.all().order_by('-id')
    count = len(models.LeaveMeg.objects.all())
    com_count = len(comments)
    # 分页处理留言
    obj = MyPage(request, comments, page_size=10)
   
    # 获取已有的弹幕数据
    messages = models.LeaveMeg.objects.all().order_by('-id')[:100]
    return render(request, 'leave.html', {
        'form': form,
        'messages': messages,
        'data': obj.page_queryset,  # 留言数据
        "page_string": obj.html(),
        "count":count,
        'com_count':com_count
    })


@csrf_exempt
def send_comment(request):
    """处理留言发送的AJAX请求"""
    if request.method == 'POST':
        try:
            # 获取用户ID
            user_id = request.session.get('user_id')
            if not user_id:
                return JsonResponse({'status': False, 'error': '请先登录'})

            # 获取留言内容
            data = json.loads(request.body)
            content = data.get('content', '').strip()

            if not content:
                return JsonResponse({'status': False, 'error': '留言内容不能为空'})

            if len(content) > 800:
                return JsonResponse({'status': False, 'error': '留言内容过长'})

            # 获取用户对象
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'status': False, 'error': '用户不存在'})

            # 创建留言 - 使用正确的模型
            comment = models.Comment.objects.create(
                user_id=user,
                content=content
            )

            return JsonResponse({
                'status': True,
                'message': '留言发表成功',
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'username': user.username,
                    'date': comment.date.strftime('%Y-%m-%d %H:%M'),
                    'role': user.role
                }
            })

        except Exception as e:
            return JsonResponse({'status': False, 'error': str(e)})

    return JsonResponse({'status': False, 'error': '无效的请求'})


@csrf_exempt
def send_danmu(request):
    """处理弹幕发送的AJAX请求"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()

            if not content:
                return JsonResponse({'status': False, 'error': '弹幕内容不能为空'})

            if len(content) > 200:
                return JsonResponse({'status': False, 'error': '弹幕内容过长'})

            user_id = request.session.get('user_id')
            user = None
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    pass

            # 保存到数据库，关联用户
            danmu = models.LeaveMeg.objects.create(
                content=content,
                user=user  
            )

            return JsonResponse({
                'status': True,
                'message': '弹幕发送成功',
                'content': content,
                'id': danmu.id
            })

        except Exception as e:
            return JsonResponse({'status': False, 'error': '发送失败: ' + str(e)})

    return JsonResponse({'status': False, 'error': '无效的请求方法'})


def get_danmus(request):
    """获取弹幕数据的API"""
    messages = models.LeaveMeg.objects.all().order_by('-id')[:100]  # 获取最新的100条
    
    danmus = []
    for msg in messages:
        # 检查用户是否有头像
        has_avatar = False
        user_id = None
        username = "游客"
        
        if msg.user:  # 如果弹幕有关联用户 - 这里改为 msg.user
            user_id = msg.user.id
            username = msg.user.username
            # 检查头像文件是否存在
            avatar_path = os.path.join(settings.MEDIA_ROOT, 'avatars', f'avatar_{user_id}.jpg')
            has_avatar = os.path.exists(avatar_path)
        
        danmus.append({
            'content': msg.content, 
            'id': msg.id,
            'user_id': user_id,
            'username': username,
            'has_avatar': has_avatar
        })
    
    return JsonResponse({'status': True, 'danmus': danmus})
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
import json
import os
import time
from django import forms
from index import models
from index.my_class.codeimg import check_code
from index.my_class.bootstrap import BootstrapModelForm, BootstrapForm
from index.models import User
from index.my_class.encrypt import md5
from django.contrib.auth import logout as auth_logout
from django.conf import settings


# 修改密码表单
class ChangePasswordForm(BootstrapForm):
    current_password = forms.CharField(
        label='当前密码',
        widget=forms.PasswordInput(render_value=True),
        required=True
    )

    new_password = forms.CharField(
        label='新密码',
        widget=forms.PasswordInput(render_value=True),
        required=True,
        min_length=8
    )

    confirm_password = forms.CharField(
        label='确认新密码',
        widget=forms.PasswordInput(render_value=True),
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.label
            else:
                field.widget.attrs = {
                    'class': 'form-control',
                    'placeholder': field.label,
                }

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        # 对输入的当前密码进行md5加密后比较
        encrypted_password = md5(current_password)
        if self.user and self.user.password != encrypted_password:
            raise ValidationError("当前密码错误")
        return current_password

    def clean_confirm_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("两次输入的密码不一致")
        return confirm_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        # 检查密码强度（至少包含字母和数字）
        if new_password and (new_password.isdigit() or new_password.isalpha()):
            raise ValidationError("密码必须包含字母和数字")
        return new_password


def set(request):
    # 检查用户是否登录
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('/')

    context = {
        'user': user
    }
    return render(request, 'proSet.html', context)


# 修改密码
@csrf_exempt
def change_password(request):
    if request.method != 'POST':
        return JsonResponse({'status': False, 'error': '无效的请求方法'})

    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'status': False, 'error': '用户未登录'})

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'status': False, 'error': '用户不存在'})

    form = ChangePasswordForm(request.POST, user=user)
    if form.is_valid():
        try:
            new_password = form.cleaned_data.get('new_password')
            # 对新密码进行md5加密
            encrypted_password = md5(new_password)
            user.password = encrypted_password
            user.save()

            return JsonResponse({
                'status': True,
                'message': '密码修改成功'
            })
        except Exception as e:
            return JsonResponse({
                'status': False,
                'error': f'密码修改失败: {str(e)}'
            })
    else:
        errors = {}
        for field, error_list in form.errors.items():
            errors[field] = [error for error in error_list]
        return JsonResponse({
            'status': False,
            'error': errors
        })


# 上传头像视图
@csrf_exempt
def upload_avatar(request):
    if request.method != 'POST':
        return JsonResponse({'status': False, 'error': '无效的请求方法'})

    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'status': False, 'error': '用户未登录'})

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'status': False, 'error': '用户不存在'})

    if 'avatar' not in request.FILES:
        return JsonResponse({'status': False, 'error': '请选择头像文件'})

    avatar_file = request.FILES['avatar']

    # 检查文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg']
    if avatar_file.content_type not in allowed_types:
        return JsonResponse({'status': False, 'error': '只支持 JPEG、PNG、GIF 格式的图片'})

    # 检查文件大小（限制为 5MB）
    if avatar_file.size > 5 * 1024 * 1024:
        return JsonResponse({'status': False, 'error': '图片大小不能超过 5MB'})

    try:
        # 创建 avatars 目录
        avatars_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
        if not os.path.exists(avatars_dir):
            os.makedirs(avatars_dir)

        # 生成文件名
        file_extension = os.path.splitext(avatar_file.name)[1]
        filename = f'avatar_{user_id}.jpg'
        filepath = os.path.join('avatars', filename)
        full_path = os.path.join(settings.MEDIA_ROOT, filepath)

        # 保存文件
        with open(full_path, 'wb+') as destination:
            for chunk in avatar_file.chunks():
                destination.write(chunk)

        # 更新用户头像路径
        # 假设 User 模型有 avatar 字段
        user.avatar = filepath
        user.save()

        return JsonResponse({
            'status': True,
            'message': '头像上传成功',
            'avatar_url': f'/media/{filepath}'
        })

    except Exception as e:
        return JsonResponse({
            'status': False,
            'error': f'头像上传失败: {str(e)}'
        })


def err(request):
    return render(request, 'err.html')
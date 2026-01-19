from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
import json
from django import forms
from index import models
from index.my_class.codeimg import check_code
from index.my_class.bootstrap import BootstrapModelForm, BootstrapForm
from index.models import User, Content,Tag
from index.my_class.encrypt import md5
from django.contrib.auth import logout as auth_logout
from django.utils import timezone
import datetime
from leaveMeg.models import LeaveMeg
from django.db.models import Sum
import logging
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from django.core.cache import cache
from django.conf import settings
import re
from userAdmin.models import Announcement,SiteInformation

from userAdmin.models import SiteInformation

# 设置日志
logger = logging.getLogger(__name__)

EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.qq.com',
    'SMTP_PORT': 587,
    'SENDER_EMAIL': '2497963177@qq.com',  # 你的QQ邮箱
    'SENDER_PASSWORD': 'gdzmbyzagbokeaig',  # QQ邮箱授权码，不是密码
}

# 登录表单
class logins(BootstrapForm):
    username = forms.CharField(
        label='用户名',
        widget=forms.TextInput,
        required=True
    )

    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(render_value=True),
        required=True
    )

    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput(),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if (name == 'password') and hasattr(field.widget, 'input_type'):
                field.widget.input_type = 'password'
            if field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.label
            else:
                field.widget.attrs = {
                    'class': 'form-control',
                    'placeholder': field.label,
                }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return md5(password)

# 发送邮箱验证码
@csrf_exempt
def send_email_code(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email', '').strip()

            # 邮箱格式验证
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                return JsonResponse({
                    'status': False,
                    'message': '请输入有效的邮箱'
                })

            # 检查邮箱是否已被注册 - 修复这里！
            if User.objects.filter(email=email).exists():  # 改为检查 email 字段
                return JsonResponse({
                    'status': False,
                    'message': '该邮箱已被注册'
                })

            # 生成6位随机验证码
            code = ''.join(random.choices('0123456789', k=6))
            print(f"生成的验证码: {code}")

            # 将验证码存入缓存，有效期10分钟
            cache_key = f'email_code_{email}'
            cache.set(cache_key, code, 600)

            # 启用真实邮件发送
            if send_verification_email(email, code):
                return JsonResponse({
                    'status': True,
                    'message': '验证码已发送到您的邮箱，请查收'
                })
            else:
                return JsonResponse({
                    'status': False,
                    'message': '邮件发送失败，请重试'
                })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'status': False,
                'message': f'系统错误: {str(e)}'
            })

    return JsonResponse({'status': False, 'message': '无效的请求方法'})

def send_verification_email(email, code):
    """发送验证码邮件"""
    try:
        # 邮件内容
        subject = "Fool Blog - 邮箱验证码"
        body = f"""
        <div style="font-family: 'Microsoft YaHei', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #333; margin-bottom: 10px;">Fool Blog 邮箱验证</h2>
                <p style="color: #666; font-size: 14px;">感谢您注册我们的博客平台</p>
            </div>

            <div style="background: #f8f9fa; padding: 20px; border-radius: 6px; margin-bottom: 20px;">
                <p style="margin: 0 0 15px 0; color: #333;">您的验证码是：</p>
                <div style="text-align: center; margin: 20px 0;">
                    <span style="font-size: 32px; font-weight: bold; color: #e74c3c; letter-spacing: 5px;">{code}</span>
                </div>
                <p style="margin: 15px 0 0 0; color: #666; font-size: 12px;">验证码有效期10分钟，请及时使用。</p>
            </div>

            <div style="border-top: 1px solid #e0e0e0; padding-top: 20px; text-align: center;">
                <p style="color: #999; font-size: 12px; margin: 0;">
                    此为系统邮件，请勿回复<br>
                    © 2025 Fool Blog. All rights reserved.
                </p>
            </div>
        </div>
        """

        # 创建邮件 - 使用正确的 MIMEText
        msg = MIMEText(body, 'html', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')  # 使用 Header 处理中文主题
        msg['From'] = EMAIL_CONFIG['SENDER_EMAIL']
        msg['To'] = email

        # 发送邮件
        server = smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT'])
        server.starttls()  # 启用TLS加密
        server.login(EMAIL_CONFIG['SENDER_EMAIL'], EMAIL_CONFIG['SENDER_PASSWORD'])
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        logger.error(f"发送邮件失败: {e}")
        return False

# 注册表单
class user_form(BootstrapModelForm):
    email = forms.EmailField(
        label="邮箱",
        widget=forms.EmailInput,
        required=True
    )
    con_password = forms.CharField(
        max_length=64,
        label="确认密码",
        widget=forms.PasswordInput,
        required=True
    )
    code = forms.CharField(
        label="图形验证码",
        widget=forms.TextInput(),
        required=True
    )
    email_code = forms.CharField(
        label="邮箱验证码",
        widget=forms.TextInput(),
        required=True
    )

    class Meta:
        model = models.User
        fields = ['username', 'email', 'password', 'con_password', 'code', 'email_code']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in ['password', 'con_password'] and hasattr(field.widget, 'input_type'):
                field.widget.input_type = 'password'
            if field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.label
            else:
                field.widget.attrs = {
                    'class': 'form-control',
                    'placeholder': field.label,
                }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return md5(password)

    def clean_con_password(self):
        pwd = self.cleaned_data.get('password')
        con_password = md5(self.cleaned_data.get('con_password'))
        if pwd != con_password:
            raise ValidationError("密码不一致")
        return con_password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("用户名已存在")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # 验证QQ邮箱格式
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("请输入有效的邮箱")

        # 检查邮箱是否已被注册
        if User.objects.filter(email=email).exists():
            raise ValidationError("该邮箱已被注册")

        return email

    def clean_email_code(self):
        email = self.cleaned_data.get('email')
        input_code = self.cleaned_data.get('email_code')

        if email and input_code:
            cache_key = f'email_code_{email}'
            cached_code = cache.get(cache_key)

            if not cached_code:
                raise ValidationError("邮箱验证码已过期")

            if cached_code != input_code:
                raise ValidationError("邮箱验证码错误")

            self.email_code_validated = True
            self.valid_email = email
            self.valid_email_code = cached_code

        return input_code

def website_runtime():
    """计算网站运行时间"""
    start_time = datetime.datetime(2025, 11, 8, 0, 0, 0) 
    start_time = timezone.make_aware(start_time)
    
    now = timezone.now()
    delta = now - start_time
    
    years = delta.days // 365
    months = (delta.days % 365) // 30
    days = (delta.days % 365) % 30
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds % 60
    
    return {
        'display': f"{years}年{months}月{days}天{hours}时{minutes}分{seconds}秒",
        'timestamp': start_time.timestamp()
    }

def index(request):
    site_info = SiteInformation.objects.first()
    if site_info:
        site_info.site_count += 1
        site_info.save()
   
    data = Content.objects.all().order_by('is_top','-id')[:8]
    login_form = logins()
    reg_form = user_form()
    runtime_data = website_runtime()
    content_count = len(Content.objects.all())
    dm = LeaveMeg.objects.all().order_by('-id')[:50]
    dm_count = len(LeaveMeg.objects.all())
    tag = models.Tag.objects.all()
    announcement = Announcement.objects.all().order_by('-id').first()
    site = SiteInformation.objects.all().first()


    total_views = Content.objects.aggregate(total_views=Sum('look_count'))['total_views'] or 0
    return render(request, 'index.html', {
        'form': login_form, 
        'user_form': reg_form, 
        'data': data,
        'runtime_display': runtime_data['display'],
        'start_timestamp': runtime_data['timestamp'],
        'count': content_count,
        'dm': dm,
        'dm_count': dm_count,
        'cont_count':total_views,
        'tag':tag,
        'announcement':announcement,
        'site':site,
    })

# 图片验证码
def code(request):
    try:
        img, code_string = check_code()
        request.session['code'] = code_string
        request.session.set_expiry(300)
        stream = BytesIO()
        img.save(stream, format='png')
        return HttpResponse(stream.getvalue(), content_type='image/png')
    except Exception as e:
        logger.error(f"验证码生成错误: {e}")
        return HttpResponse(status=500)

# 检查登录状态
def check_login(request):
    user_id = request.session.get('user_id')
    username = request.session.get('username')
    if user_id and username:
        return JsonResponse({
            'status': True,
            'username': username
        })
    else:
        return JsonResponse({
            'status': False
        })

# 退出登录
@csrf_exempt
def logout(request):
    if request.method == 'POST':
        # 清除session
        request.session.flush()
        return JsonResponse({
            'status': True,
            'message': '退出成功'
        })
    return JsonResponse({'status': False, 'error': '无效的请求方法'})

# 登录检测
@csrf_exempt
def login(request):
    if request.method == 'POST':
        form = logins(request.POST)
        if form.is_valid():
            # 验证码校验
            session_code = request.session.get('code', '')
            input_code = form.cleaned_data.get('code', '')
            if not session_code or session_code.upper() != input_code.upper():
                return JsonResponse({
                    'status': False,
                    'error': {'code': ['验证码错误']}
                })

            # 用户验证
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            try:
                user = User.objects.get(username=username, password=password)
                # 登录成功，设置session
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['role'] = user.role

                # 处理"记住我"功能
                remember_me = request.POST.get('rememberMe')
                if remember_me:
                    request.session.set_expiry(1209600)  # 2周
                else:
                    request.session.set_expiry(0)

                # 获取返回URL
                next_url = request.POST.get('next', '/')
                
                return JsonResponse({
                    'status': True,
                    'message': '登录成功',
                    'next': next_url
                })
            except User.DoesNotExist:
                return JsonResponse({
                    'status': False,
                    'error': {'username': ['用户名或密码错误']}
                })
        else:
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [error for error in error_list]
            return JsonResponse({
                'status': False,
                'error': errors
            })

    return JsonResponse({'status': False, 'error': '无效的请求方法'})

# 注册
@csrf_exempt
def reg_login(request):
    if request.method == 'POST':
        errors = {}
        
        # 1. 验证图片验证码
        session_code = request.session.get('code', '')
        input_code = request.POST.get('code', '')
        if not session_code or session_code.upper() != input_code.upper():
            errors['code'] = ['验证码错误']
        
        # 2. 验证表单其他字段
        form = user_form(request.POST)
        if not form.is_valid():
            for field, error_list in form.errors.items():
                if field != 'code' or 'code' not in errors:
                    errors[field] = [error for error in error_list]
        
        # 3. 如果有任何错误，返回所有错误（不删除邮箱验证码）
        if errors:
            return JsonResponse({
                'status': False,
                'error': errors,
                'form_data': {
                    'email': request.POST.get('email', ''),
                    'email_code': request.POST.get('email_code', ''),
                    'username': request.POST.get('username', '')
                }
            })
        
        # 4. 所有验证通过，保存用户并删除邮箱验证码
        try:
            # 删除邮箱验证码缓存
            if hasattr(form, 'valid_email') and form.valid_email:
                cache_key = f'email_code_{form.valid_email}'
                cache.delete(cache_key)
            
            user = form.save(commit=False)
            user.password = form.cleaned_data['password']
            user.save()
            
            # 注册成功后自动登录
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['role'] = user.role

            next_url = request.POST.get('next', '/')
            return JsonResponse({
                'status': True,
                'message': '注册成功',
                'username': user.username,
                'email': user.email,
                'next': next_url
            })
        except Exception as e:
            logger.error(f"注册失败: {e}")
            return JsonResponse({
                'status': False,
                'error': {'__all__': [f'注册失败: {str(e)}']},
                'form_data': {
                    'email': request.POST.get('email', ''),
                    'email_code': request.POST.get('email_code', ''),
                    'username': request.POST.get('username', '')
                }
            })
    
    return JsonResponse({'status': False, 'error': '无效的请求方法'})# 登录页面视图
def login2(request):
    """新的独立登录页面"""
    if request.session.get('user_id'):
        next_url = request.GET.get('next', '/')
        return redirect(next_url)
    
    return render(request, 'login.html')


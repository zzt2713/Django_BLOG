from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse, redirect, render
import re


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # 定义允许所有用户（包括未登录用户）访问的URL白名单
        public_allowed_paths = [
            r'^/$',  # 主页
            r'^/index/login/$',  # 主页
            r'^/login/$',  # 登录页
            r'^/register/$',  # 注册页
            r'^/image_code/$',  # 图片验证码
            r'^/check_login/$',  # 检查登录状态
            r'^/err/$',  # 错误页面
            r'^/media/',  # 图片
            r'^/picture/$',  # 相册页面
            r'^/content/$',  # 文章列表页（只读）
            r'^/content/article/',
            r'^/leaveList/',
            r'^/send_email_code/', # 邮箱验证码
            r'^/search/',
	    r'^/archives/$'
        ]

        # 定义普通用户（已登录非管理员）允许访问的URL
        user_allowed_paths = [
            r'^/proSet/$',  # 个人设置页面
            r'^/proSet/change_password/$',  # 修改密码
            r'^/proSet/upload_avatar/$',  # 上传头像
            r'^/logout/$',  # 退出登录
        ]

        # 定义管理员专用URL（普通用户不能访问）
        admin_only_paths = [
            r'^/admin/',  # 所有admin开头的路径
            r'^/content/add/',  # 添加文章
            r'^/content/edit/',  # 编辑文章
            r'^/content/delete/',  # 删除文章
            r'^/user/manage/',  # 用户管理
            r'^/picture/manage/',  # 图片管理
            r'^/picture/upload/',  # 图片上传（如果普通用户不能上传）
            r'^/picture/delete/',  # 图片删除
        ]

        # 检查当前路径
        current_path = request.path_info

        # 1. 首先检查是否在公共白名单中（所有人都可以访问）
        for pattern in public_allowed_paths:
            if re.match(pattern, current_path):
                return None  # 允许访问

        # 2. 检查用户是否登录
        info_dict = request.session.get('username')
        if not info_dict:
            return redirect('/err/')  # 未登录重定向到登录页

        # 3. 获取用户角色
        role = request.session.get('role')

        # 4. 如果是管理员（role=1），允许访问所有页面
        if role == 1:
            return None

        # 5. 如果是普通用户（role不等于1）
        # 检查是否在普通用户允许访问的列表中
        for pattern in user_allowed_paths:
            if re.match(pattern, current_path):
                return None  # 允许访问

        # 6. 检查是否在管理员专用列表中，如果是则拒绝访问
        for pattern in admin_only_paths:
            if re.match(pattern, current_path):
                return redirect('/err/')  # 普通用户尝试访问管理页面，重定向到错误页

        # 7. 对于其他未明确配置的路径，默认允许普通用户访问
        # 如果你希望更严格，可以将下面的return None改为return redirect('/err/')
        return None
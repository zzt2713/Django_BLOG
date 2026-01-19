"""
URL configuration for MyBlog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from index.views import login,proSet,pic,contents
from leaveMeg import views
from userAdmin import views as admin_user

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}, name='media'),

    # md编辑器
    path('mdeditor/', include('mdeditor.urls')), 
    
    # 主页
    path('', login.index),
    # 主页登录2
    path('index/login/', login.login2),
    # 主页-登录ajax发送
    path('login/', login.login),
    # 主页-注册
    path('register/', login.reg_login),
    # 主页-登录-注册-图片验证码 
    path('image_code/', login.code),
    # 注册邮箱验证码
    path('send_email_code/', login.send_email_code, name='send_email_code'),
    # 检查登录状态
    path('check_login/', login.check_login),
    # 退出登录
    path('logout/', login.logout),

    # 个人设置
    path('proSet/', proSet.set),
    # 修改密码
    path('proSet/change_password/', proSet.change_password),
    # 上传头像
    path('proSet/upload_avatar/', proSet.upload_avatar),
    # 错误信息返回
    path('err/', proSet.err),

    # 相册
    path('picture/', pic.picture),
    path('upload_pic/', pic.upload_pic),
    # 删除图片
    path('delete_pic/', pic.delete_pic),

    # 文章
    path('content/', contents.content),
    #文章详情页面
    path('content/article/', contents.article),
    #文章点赞
    path('content/article/like/', contents.like),
    # 文章添加
    path('add_content/',contents.add_content),
    path('content/add/', contents.add_content),
    # 删除文章 管理员权限
    path('content/article/delete/', contents.article_delete),
    # 文章编辑
    path('content/article/edit/',contents.article_edit),
    # 文章搜索
    path('search/',contents.content),
    # 标签分类
    path('content/tags/',contents.tag),
    # 文章评论
    path('content/article/comment/', contents.article_comment, name='article_comment'),
    
    
    # 归档
    path('archives/', contents.archives),
    
    # 留言区
    path('leaveList/', views.meg),  # 留言页面
    path('send_danmu/', views.send_danmu),  # 发送弹幕
    path('get_danmus/', views.get_danmus),  # 获取弹幕
    path('send_comment/', views.send_comment),  # 发送留言

    # 后台管理页面
    path('admin_user/', admin_user.admin_user, name='admin_user'),
    # 文章管理
    path('admin_user/content/', admin_user.admin_content, name='admin_content'),
    # 用户管理
    path('admin_user/users/', admin_user.admin_user_manage, name='admin_user_manage'),
    # 留言管理
    path('admin_user/comments/', admin_user.admin_comments, name='admin_comments'),
    # 相册管理
    path('admin_user/pictures/', admin_user.admin_pictures, name='admin_pictures'),
    # 弹幕管理
    path('admin_user/leavemeg/', admin_user.admin_leavemeg, name='admin_leavemeg'),
    # 增删查改
    path('admin/delete_content/<int:content_id>/', admin_user.delete_content, name='delete_content'),
    path('admin/delete_user/<int:user_id>/', admin_user.delete_user, name='delete_user'),
    path('admin/delete_comment/<int:comment_id>/', admin_user.delete_comment, name='delete_comment'),
    path('admin/delete_picture/<int:picture_id>/', admin_user.delete_picture, name='delete_picture'),
    path('admin/delete_leavemeg/<int:leavemeg_id>/', admin_user.delete_leavemeg, name='delete_leavemeg'),
    # 标签管理
    path('admin_user/tags/', admin_user.admin_tags, name='admin_tags'),
    path('admin_user/add_tag/', admin_user.add_tag, name='add_tag'),
    path('admin_user/delete_tag/<int:tag_id>/', admin_user.delete_tag, name='delete_tag'),
    path('admin/edit_tag/<int:tag_id>/', admin_user.edit_tag, name='edit_tag'),
    # 重置密码
    path('admin/reset_password/<int:user_id>/', admin_user.reset_password, name='reset_password'),
    # 用户搜索
    path('admin_user/users/search/', admin_user.admin_user_manage),
    # 公告管理
    path('admin_user/announcements/', admin_user.admin_announcements, name='admin_announcements'),
    path('admin_user/siteinfo/', admin_user.admin_siteinfo, name='admin_siteinfo'),

    # 公告增删改查
    path('admin/add_announcement/', admin_user.add_announcement, name='add_announcement'),
    path('admin/edit_announcement/<int:announcement_id>/', admin_user.edit_announcement, name='edit_announcement'),
    path('admin/delete_announcement/<int:announcement_id>/', admin_user.delete_announcement, name='delete_announcement'),
    path('admin/update_siteinfo/', admin_user.update_siteinfo, name='update_siteinfo'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
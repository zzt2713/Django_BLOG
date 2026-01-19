# userAdmin/views.py
from index import models
from index.models import User, Pic, Content,Tag
from leaveMeg.models import Comment, LeaveMeg
from index.my_class.pagination import MyPage
from index.models import User, Content,Tag
from index.my_class.encrypt import md5
from leaveMeg.models import LeaveMeg
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Announcement, SiteInformation
from index.models import User

def check_admin_permission(request):
    """检查管理员权限"""
    if not request.session.get('user_id'):
        from django.shortcuts import redirect
        return redirect('/login/?next=' + request.path)
    if request.session.get('role') != 1:
        return render(request, 'error.html', {'message': '权限不足'})
    return None

def admin_user(request):
    """后台管理主页面"""
    # 检查权限
    permission_error = check_admin_permission(request)
    if permission_error:
        return permission_error

    # 获取统计数据
    user_count = User.objects.count()
    content_count = Content.objects.count()
    comment_count = Comment.objects.count()
    picture_count = Pic.objects.count()
    tag_count = Tag.objects.count()

    context = {
        'current_section': 'dashboard',
        'user_count': user_count,
        'content_count': content_count,
        'comment_count': comment_count,
        'picture_count': picture_count,
        'tag_count':tag_count,
    }
    return render(request, 'admin.html', context)

def admin_content(request):
    """文章管理"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return permission_error

    contents = Content.objects.all().order_by('-date')
    obj = MyPage(request,contents)
    context = {
        'current_section': 'content',
        'contents': obj.page_queryset,
        'page_string':obj.html()
    }
    return render(request, 'admin.html', context)

def admin_user_manage(request):
    """用户管理"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return permission_error

    data_dict = {}
    data = request.GET.get('search', "")
    if data:
        data_dict['username__contains'] = data
    queryset = models.User.objects.filter(**data_dict)
    obj = MyPage(request, queryset, page_size=10)

    context = {
        'current_section': 'users',
        'users': obj.page_queryset,
        'page_string':obj.html()
    }
    return render(request, 'admin.html', context)

def admin_comments(request):
    """留言管理"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return permission_error

    comments = Comment.objects.all().order_by('-date')
    obj = MyPage(request,comments,page_size=20)

    context = {
        'current_section': 'comments',
        'comments': obj.page_queryset,
        'page_string':obj.html()
    }
    return render(request, 'admin.html', context)

def admin_pictures(request):
    """相册管理"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return permission_error

    pictures = Pic.objects.all().order_by('-date')
    obj = MyPage(request,pictures, page_size=12)
    context = {
        'current_section': 'pictures',
        'pictures': obj.page_queryset,
        'page_string':obj.html()
    }
    return render(request, 'admin.html', context)

def admin_leavemeg(request):
    """弹幕管理"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return permission_error

    leavemegs = LeaveMeg.objects.all().order_by('-id')
    obj = MyPage(request,leavemegs,page_size=20)
    context = {
        'current_section': 'leavemeg',
        'leavemegs': obj.page_queryset,
        'page_string':obj.html()
    }
    return render(request, 'admin.html', context)

# AJAX 删除操作
def delete_content(request, content_id):
    """删除文章"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return JsonResponse({'success': False, 'message': '权限不足'})

    if request.method == 'POST':
        content = get_object_or_404(Content, id=content_id)
        content.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False})

def delete_user(request, user_id):
    """删除用户"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return JsonResponse({'success': False, 'message': '权限不足'})

    if request.method == 'POST':
        # 防止删除自己
        if user_id == request.session.get('user_id'):
            return JsonResponse({'success': False, 'message': '不能删除自己'})

        user = get_object_or_404(User, id=user_id)
        user.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False})

def delete_comment(request, comment_id):
    """删除留言"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return JsonResponse({'success': False, 'message': '权限不足'})

    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        comment.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False})

def delete_picture(request, picture_id):
    """删除图片"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return JsonResponse({'success': False, 'message': '权限不足'})

    if request.method == 'POST':
        picture = get_object_or_404(Pic, id=picture_id)
        picture.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False})

def delete_leavemeg(request, leavemeg_id):
    """删除弹幕"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return JsonResponse({'success': False, 'message': '权限不足'})

    if request.method == 'POST':
        leavemeg = get_object_or_404(LeaveMeg, id=leavemeg_id)
        leavemeg.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False})

def admin_tags(request):
    """标签管理"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return permission_error

    tags = Tag.objects.all()
    obj = MyPage(request,tags)
    context = {
        'current_section': 'tags',
        'tags': obj.page_queryset,
        'page_string':obj.html()
    }
    return render(request, 'admin.html', context)  # 修正模板名称

def add_tag(request):
    """添加标签"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return JsonResponse({'success': False, 'message': '权限不足'})

    if request.method == 'POST':
        tag_name = request.POST.get('tag_name')
        if tag_name:
            Tag.objects.create(tag=tag_name)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def delete_tag(request, tag_id):
    """删除标签"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return JsonResponse({'success': False, 'message': '权限不足'})

    if request.method == 'POST':
        tag = get_object_or_404(Tag, id=tag_id)
        tag.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False})

def edit_tag(request, tag_id):
    """编辑标签"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return JsonResponse({'success': False, 'message': '权限不足'})

    tag = get_object_or_404(Tag, id=tag_id)

    if request.method == 'POST':
        tag_name = request.POST.get('tag_name')
        if tag_name and tag_name.strip():
            tag.tag = tag_name.strip()
            tag.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'message': '标签名称不能为空'})

    # GET 请求时返回标签数据
    return JsonResponse({
        'success': True,
        'data': {
            'id': tag.id,
            'tag': tag.tag
        }
    })

def reset_password(request, user_id):
    """重置用户密码"""
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            new_password = request.POST.get('new_password', '123456')

            # 对密码进行MD5加密
            encrypted_password = md5(new_password)

            # 更新密码
            user.password = encrypted_password
            user.save()

            return JsonResponse({
                'success': True,
                'message': f'密码重置成功！'
            })

        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '用户不存在'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'重置失败: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': '无效的请求方法'
    })


def admin_announcements(request):
    """公告管理"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return permission_error

    announcements = Announcement.objects.all().order_by('-time')
    obj = MyPage(request, announcements)

    context = {
        'current_section': 'announcements',
        'announcements': obj.page_queryset,
        'page_string': obj.html()
    }
    return render(request, 'admin.html', context)


def admin_siteinfo(request):
    """网站信息管理"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return permission_error

    site_info = SiteInformation.objects.first()

    context = {
        'current_section': 'siteinfo',
        'site_info': site_info,
    }
    return render(request, 'admin.html', context)


def add_announcement(request):
    """添加公告"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return JsonResponse({'success': False, 'message': '权限不足'})

    if request.method == 'POST':
        try:
            version = request.POST.get('version', '').strip()
            content = request.POST.get('content', '').strip()

            if not version:
                return JsonResponse({'success': False, 'message': '版本号不能为空'})

            if not content:
                return JsonResponse({'success': False, 'message': '更新内容不能为空'})

            # 创建公告
            announcement = Announcement.objects.create(
                version=version,
                content=content
            )

            return JsonResponse({'success': True, 'message': '公告添加成功'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'服务器错误: {str(e)}'})

    return JsonResponse({'success': False, 'message': '无效的请求方法'})

def edit_announcement(request, announcement_id):
    """编辑公告"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return JsonResponse({'success': False, 'message': '权限不足'})

    try:
        announcement = get_object_or_404(Announcement, id=announcement_id)

        if request.method == 'POST':
            version = request.POST.get('version', '').strip()
            content = request.POST.get('content', '').strip()

            if not version:
                return JsonResponse({'success': False, 'message': '版本号不能为空'})

            if not content:
                return JsonResponse({'success': False, 'message': '更新内容不能为空'})

            announcement.version = version
            announcement.content = content
            announcement.save()

            return JsonResponse({'success': True, 'message': '公告更新成功'})

        # GET 请求返回数据
        return JsonResponse({
            'success': True,
            'data': {
                'id': announcement.id,
                'version': announcement.version,
                'content': announcement.content
            }
        })

    except Exception as e:
        print(f"编辑公告时发生错误: {str(e)}")
        return JsonResponse({'success': False, 'message': f'服务器错误: {str(e)}'})


def delete_announcement(request, announcement_id):
    """删除公告"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return JsonResponse({'success': False, 'message': '权限不足'})

    if request.method == 'POST':
        try:
            announcement = get_object_or_404(Announcement, id=announcement_id)
            announcement.delete()
            return JsonResponse({'success': True, 'message': '公告删除成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'删除失败: {str(e)}'})

    return JsonResponse({'success': False, 'message': '无效的请求方法'})


def update_siteinfo(request):
    """更新网站信息"""
    permission_error = check_admin_permission(request)
    if permission_error:
        return JsonResponse({'success': False, 'message': '权限不足'})

    if request.method == 'POST':
        try:
            site_info = SiteInformation.objects.first()
            if not site_info:
                # 如果没有网站信息，创建一个
                admin_user = User.objects.filter(role=1).first()
                if not admin_user:
                    return JsonResponse({'success': False, 'message': '未找到管理员用户'})

                site_info = SiteInformation.objects.create(
                    admin=admin_user,
                    contents_count=0,
                    site_count=0,
                    site_meg='',
                    signature=''
                )

            # 自动从文章数据中获取文章总浏览量
            from django.db.models import Sum
            total_look_count = Content.objects.aggregate(total_views=Sum('look_count'))['total_views'] or 0

            # 获取其他需要更新的字段（从表单中）
            site_meg = request.POST.get('site_meg', '')
            signature = request.POST.get('signature', '')

            # 自动设置文章访客量为文章总浏览量
            site_info.contents_count = total_look_count
            # 网站访客量保持自动统计，不手动修改
            site_info.site_meg = site_meg
            site_info.signature = signature
            site_info.save()

            return JsonResponse({'success': True, 'message': '网站信息更新成功'})

        except Exception as e:
            print(f"更新网站信息时发生错误: {str(e)}")
            return JsonResponse({'success': False, 'message': f'服务器错误: {str(e)}'})

    return JsonResponse({'success': False, 'message': '无效的请求方法'})
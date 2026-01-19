from MyBlog import settings
from index.my_class.pagination import MyPage
from django import forms
import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import os
import json
from datetime import datetime
from index.models import Pic

class PicUploadForm(forms.ModelForm):
    class Meta:
        model = Pic
        fields = ['title', 'description']

    image = forms.ImageField(
        label='选择图片',
        required=True,
        widget=forms.FileInput(attrs={
            'accept': 'image/*'
        })
    )
    capture_date = forms.DateField(
        label='图片日期',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))


def picture(request):
    """相册主页"""
    pictures = Pic.objects.all().order_by('-id')
    form = MyPage(request, pictures,page_size=10)

    if request.method == 'POST' and request.FILES:
        form = PicUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image']

            # 使用 MEDIA_ROOT 作为基础路径
            pic_dir = os.path.join(settings.MEDIA_ROOT, 'pic')
            if not os.path.exists(pic_dir):
                os.makedirs(pic_dir)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_extension = os.path.splitext(image_file.name)[1]
            filename = f"{timestamp}{file_extension}"

            # 完整的文件路径
            file_path = os.path.join(pic_dir, filename)

            # 保存文件
            with open(file_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            # 创建Pic对象 - 保存相对路径
            pic = Pic(
                title=form.cleaned_data['title'],
                description=form.cleaned_data.get('description', ''),
                path=f"pic/{filename}"  # 相对 MEDIA_ROOT 的路径
            )
            pic.save()

            return JsonResponse({
                'status': 'success',
                'message': '图片上传成功',
                'pic_id': pic.id
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': '表单验证失败',
                'errors': form.errors
            })

    context = {
        'pictures': form.page_queryset,
        'page_string': form.html()
    }
    return render(request, 'pic.html', context)


@csrf_exempt
def upload_pic(request):
    """单独的上传图片API接口"""
    if request.method == 'POST' and request.FILES:
        try:
            image_file = request.FILES['image']
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            capture_date = request.POST.get('capture_date', '')

            if not title:
                return JsonResponse({'status': 'error', 'message': '图片标题不能为空'})

            # 验证文件类型
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if image_file.content_type not in allowed_types:
                return JsonResponse({'status': 'error', 'message': '只支持JPG、PNG、GIF格式的图片'})

            # 验证文件大小（5MB）
            if image_file.size >10 * 1024 * 1024:
                return JsonResponse({'status': 'error', 'message': '图片大小不能超过10MB'})

            # 创建media/pic目录
            pic_dir = 'media/pic'
            if not os.path.exists(pic_dir):
                os.makedirs(pic_dir)

            # 生成唯一文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_extension = os.path.splitext(image_file.name)[1]
            filename = f"{timestamp}{file_extension}"
            file_path = os.path.join('pic/', filename)

            # 保存文件
            fs = FileSystemStorage()
            saved_path = fs.save(file_path, image_file)

            # 创建Pic对象
            pic = Pic(
                title=title,
                description=description,
                path=f"media/{file_path}"
            )
            pic.save()

            return JsonResponse({
                'status': 'success',
                'message': '图片上传成功',
                'pic_id': pic.id,
                'pic_path': saved_path,
                'pic_title': title
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'上传失败: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': '无效的请求'})

# 删除相册图片
def delete_pic(request):
    nid = request.GET.get('nid')
    Pic.objects.filter(id=nid).first().delete()
    return JsonResponse({
        'status': 'success',
    })


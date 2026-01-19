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
from index.models import User, Content
from index.my_class.encrypt import md5
from django.contrib.auth import logout as auth_logout
from mdeditor.fields import MDEditorWidget
import markdown
from index.my_class.pagination import MyPage
from django.db.models import Q
from leaveMeg.models import Art_Comment
import os
import uuid
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

class add_Form(BootstrapModelForm):
    class Meta:
        model = models.Content
        exclude = ['id', 'date', 'like_count', 'look_count', 'comment']
        widgets = {
            'tag': forms.Select(attrs={'class': 'form-control'}),
            'is_top': forms.Select(attrs={'class': 'form-control'}),
            'content': MDEditorWidget(),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入文章标题'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

def content(request):
    data_dict = {}
    data = request.GET.get('q', "")
    if data:
        queryset = models.Content.objects.filter(
            Q(title__contains=data) | Q(content__contains=data)
        ).order_by('is_top', '-id')
    else:
        queryset = models.Content.objects.all().order_by('is_top', '-id')
    obj = MyPage(request, queryset)

    cont = {
        'data': obj.page_queryset,
        'page_string': obj.html(),
    }
    return render(request, 'content.html', cont)

@csrf_exempt
def add_content(request):
    if request.method == 'POST':
        # 检查是否是导入 Markdown 文件的请求
        if 'import_markdown' in request.POST:
            return handle_markdown_import(request)
        
        # 正常的表单提交
        form = add_Form(request.POST, request.FILES)
        if form.is_valid():
            article = form.save()
            return redirect('/content/')
        else:
            return render(request, 'content_add.html', {'form': form, 'title': '发布文章'})
    else:
        form = add_Form()
    
    return render(request, 'content_add.html', {'form': form, 'title': '发布文章'})

@csrf_exempt
def handle_markdown_import(request):
    """处理 Markdown 文件导入，包含图片上传功能"""
    try:
        markdown_file = request.FILES.get('markdown_file')
        use_filename = request.POST.get('use_filename', 'false') == 'true'
        overwrite_content = request.POST.get('overwrite_content', 'false') == 'true'
        
        print(f"收到导入请求: 文件名={markdown_file.name if markdown_file else 'None'}")
        print(f"使用文件名: {use_filename}, 覆盖内容: {overwrite_content}")
        
        if not markdown_file:
            return JsonResponse({'success': False, 'message': '请选择 Markdown 文件'})
        
        # 读取文件内容
        content_text = markdown_file.read().decode('utf-8')
        print(f"原始内容长度: {len(content_text)}")
        print(f"内容预览: {content_text[:200]}...")
        
        # 处理 Markdown 中的图片，上传到媒体目录
        processed_content, image_count = process_and_upload_markdown_images(content_text, request)
        print(f"处理后内容长度: {len(processed_content)}")
        print(f"处理的图片数量: {image_count}")
        
        # 准备返回数据
        result = {
            'success': True,
            'content': processed_content,
            'image_count': image_count
        }
        
        if use_filename:
            filename = os.path.splitext(markdown_file.name)[0]
            result['title'] = filename
            print(f"提取的文件名: {filename}")
        
        print("导入成功，返回数据")
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        print(f"导入错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse(
            {'success': False, 'message': f'导入失败: {str(e)}'},
            json_dumps_params={'ensure_ascii': False}
        )

def process_and_upload_markdown_images(markdown_content, request):
    """处理 Markdown 内容中的图片，将本地图片上传到媒体目录"""
    import re
    import os
    from urllib.parse import urlparse
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    
    # 匹配 Markdown 图片语法 ![alt](url)
    pattern = r'!\[(.*?)\]\((.*?)\)'
    image_count = 0
    
    def replace_image(match):
        nonlocal image_count
        alt_text = match.group(1)
        image_url = match.group(2)
        
        # 如果是网络图片，保持不变
        parsed_url = urlparse(image_url)
        if parsed_url.scheme in ('http', 'https'):
            return match.group(0)
        
        # 如果是本地文件路径，尝试读取并上传
        if os.path.exists(image_url):
            try:
                # 读取图片文件
                with open(image_url, 'rb') as img_file:
                    image_data = img_file.read()
                
                # 生成文件名
                original_filename = os.path.basename(image_url)
                file_extension = os.path.splitext(original_filename)[1].lower()
                if not file_extension:
                    file_extension = '.png'  # 默认扩展名
                
                # 使用 UUID 生成唯一文件名
                new_filename = f"imported_images/{uuid.uuid4()}{file_extension}"
                
                # 保存到媒体目录
                saved_path = default_storage.save(new_filename, ContentFile(image_data))
                
                # 构建新的图片 URL
                if hasattr(default_storage, 'url'):
                    new_url = default_storage.url(saved_path)
                else:
                    # 如果存储后端没有 url 方法，使用 MEDIA_URL
                    from django.conf import settings
                    new_url = f"{settings.MEDIA_URL}{saved_path}"
                
                image_count += 1
                print(f"成功上传图片: {original_filename} -> {new_url}")
                
                return f'![{alt_text}]({new_url})'
                
            except Exception as e:
                print(f"图片上传失败 {image_url}: {e}")
                # 上传失败，返回原始内容
                return match.group(0)
        else:
            print(f"图片文件不存在: {image_url}")
            # 文件不存在，返回原始内容
            return match.group(0)
    
    # 替换所有本地图片
    processed_content = re.sub(pattern, replace_image, markdown_content)
    return processed_content, image_count
    
# 文章内容+浏览量更新
def article(request):
    nid = request.GET.get('nid')
    data = Content.objects.filter(id=nid).first()
    comments = ''
    if data:
        data.look_count += 1
        data.save()
        comments = Art_Comment.objects.filter(article=data).order_by('-date')

    return render(request, 'article.html', {
        "article": data,
        "comments": comments
    })

# 添加评论提交视图
@csrf_exempt
def article_comment(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        content = request.POST.get('content')

        if not request.session.get('user_id'):
            return JsonResponse({'success': False, 'message': '请先登录'})

        if not content or not content.strip():
            return JsonResponse({'success': False, 'message': '评论内容不能为空'})

        try:
            article = Content.objects.get(id=article_id)
            user = User.objects.get(id=request.session['user_id'])

            comment = Art_Comment.objects.create(
                article=article,
                user=user,
                comment=content.strip()
            )
            article.comment += 1
            article.save()
            
            from django.utils.timezone import localtime
            return JsonResponse({
                'success': True,
                'comment': {
                    'username': user.username,
                    'avatar': user.avatar.url if user.avatar else '',
                    'content': content.strip(),
                    'date': localtime(comment.date).strftime('%Y-%m-%d %H:%M')
                }
            })

        except Content.DoesNotExist:
            return JsonResponse({'success': False, 'message': '文章不存在'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': '用户不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': '评论失败'})

    return JsonResponse({'success': False, 'message': '请求方法错误'})

# 点赞
def like(request):
    nid = request.GET.get('nid')
    article = Content.objects.filter(id=nid).first()
    article.like_count += 1
    article.save()
    return JsonResponse({
        'success': True,
        'new_like_count': article.like_count
    })

# 删除文章
def article_delete(request):
    nid = request.GET.get("nid")
    models.Content.objects.filter(id=nid).first().delete()
    return redirect("/content/")

# 编辑文章
def article_edit(request):
    nid = request.GET.get('nid')
    obj = Content.objects.filter(id=nid).first()
    
    if request.method == 'POST':
        # 检查是否是导入 Markdown 文件的请求
        if 'import_markdown' in request.POST:
            return handle_markdown_import(request)
            
        form = add_Form(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('/content/')
        else:
            return render(request, 'content_add.html', {'form': form, 'title': '修改文章'})
    else:
        form = add_Form(instance=obj)
    
    return render(request, 'content_add.html', {'form': form, 'title': '修改文章'})

# 标签分类
def tag(request):
    bq = request.GET.get('tag')
    queryset = models.Content.objects.filter(tag=bq).order_by('is_top', '-id')
    obj = MyPage(request, queryset)
    cont = {
        'data': obj.page_queryset,
        'page_string': obj.html(),
        'tag':models.Tag.objects.filter(id=bq).first()
    }
    return render(request, 'content.html',cont)

def archives(request):
    articles = Content.objects.all().order_by('-date')
    
    articles_by_year = {}
    for article in articles:
        year = article.date.year
        if year not in articles_by_year:
            articles_by_year[year] = []
        articles_by_year[year].append(article)
    
    articles_by_year = dict(sorted(articles_by_year.items(), reverse=True))
    
    context = {
        'articles_by_year': articles_by_year
    }
    
    return render(request, 'archiver.html', context)
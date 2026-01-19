from django.db import models
import datetime
import markdown
from django.utils.safestring import mark_safe
from mdeditor.fields import MDTextField


class User(models.Model):
    Role_Choices = (
        (1, '管理员'),
        (2, '普通用户'),
    )
    username = models.CharField(max_length=32, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=64, verbose_name='密码')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    role = models.IntegerField(choices=Role_Choices, default=2, verbose_name='权限')
    email = models.EmailField(max_length=64, verbose_name='邮箱', blank=True, null=True)

class Pic(models.Model):
    title = models.CharField(max_length=60,verbose_name="图片名")
    path = models.CharField(max_length=128,verbose_name="路径")
    description = models.TextField(verbose_name="图片描述", blank=True, null=True)
    date = models.DateTimeField(verbose_name='上传时间',auto_now_add=True)

class Tag(models.Model):
    tag = models.CharField(verbose_name='标签',max_length=32)
    def __str__(self):
        return self.tag


class Content(models.Model):
    top_Choices=(
        (1,'置顶'),
        (2,"无")
    )

    title = models.CharField(max_length=100,verbose_name="标题")
    tag = models.ForeignKey(to='Tag',verbose_name="标签",to_field="id",on_delete=models.CASCADE,default=8)
    # tag = models.IntegerField(choices=tag_Choices,verbose_name='标签',default=8)
    content = MDTextField(verbose_name='内容')
    date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    cover_img = models.ImageField(upload_to='cover/', null=True, blank=True, verbose_name='封面')
    like_count = models.IntegerField(verbose_name="点赞数",default=0)
    is_top = models.SmallIntegerField(choices=top_Choices,default=2,verbose_name="是否置顶")
    look_count = models.IntegerField(verbose_name="浏览量",default=0)
    comment = models.IntegerField(verbose_name='评论量',default=0)

    def formatted_markdown(self):
        return mark_safe(markdown.markdown(self.content, extensions=[
            'markdown.extensions.extra',  # 表格、围栏代码等扩展
            'markdown.extensions.codehilite',  # 代码高亮
            'markdown.extensions.toc',  # 目录生成
        ]))

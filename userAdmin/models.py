from django.db import models

# Create your models here.

class Announcement(models.Model):
    version = models.CharField(verbose_name='版本号', max_length = 64)
    content = models.CharField(verbose_name="更新内容",max_length = 1024)
    time = models.DateTimeField(verbose_name='更新时间',auto_now_add=True)

class SiteInformation(models.Model):
    admin = models.ForeignKey(
        to="index.User",
        to_field="id",
        verbose_name="管理员id",
        on_delete=models.CASCADE
    )
    contents_count = models.IntegerField(verbose_name='文章访客量')
    site_count = models.IntegerField(verbose_name='网站访客量')
    site_meg = models.CharField(verbose_name='博客公告', max_length = 2048)
    signature = models.CharField(verbose_name='个性签名',max_length = 648)
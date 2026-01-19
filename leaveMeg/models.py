from django.db import models
import datetime
from index.models import User

class LeaveMeg(models.Model):
    """
        弹幕模型
    """
    content = models.CharField(max_length=200,verbose_name='弹幕')
    user = models.ForeignKey(
        to="index.User",
        to_field="id",   
        verbose_name="用户id",
        on_delete=models.CASCADE,
        )

class Comment(models.Model):
    """
        用户留言模型
    """
    user_id = models.ForeignKey(
        to="index.User",
        to_field="id",   
        verbose_name="用户id",
        on_delete=models.CASCADE
    )
    content = models.CharField(verbose_name='留言内容',max_length=800)
    date = models.DateTimeField(verbose_name='留言时间', auto_now_add=True)

class Art_Comment(models.Model):
    """
        文章评论区
    """
    article = models.ForeignKey(
        to="index.Content",
        verbose_name="关联文章",
        on_delete=models.CASCADE,
        to_field="id",
        related_name="comments"
    )
    user = models.ForeignKey(
        to="index.User",
        verbose_name="关联用户",
        to_field="id",
        on_delete=models.CASCADE
    )
    comment = models.CharField(verbose_name="评论内容",max_length=500)
    date =models.DateTimeField(verbose_name='评论时间', auto_now_add=True)

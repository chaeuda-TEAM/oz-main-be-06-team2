from a_common.models import CommonModel

from django.conf import settings
from django.db import models


# 게시글 모델 임시로 만들어놨어요, 수정하거나, 삭제해도 돼욥.. 다른 모델 추가할때 init에 추가해주세요
class Post(CommonModel):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    is_published = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "posts"
        ordering = ["-created_at"]
        verbose_name = "post"
        verbose_name_plural = "posts"

    def __str__(self):
        return self.title

    def increment_view_count(self):
        self.view_count += 1
        self.save()

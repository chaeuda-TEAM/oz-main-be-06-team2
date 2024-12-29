from a_common.models import CommonModel
from a_user.models import User

from django.conf import settings
from django.db import models


class Cost(CommonModel):
    id = models.AutoField(primary_key=True, verbose_name="관리비용 ID")
    cost_type = models.CharField(max_length=36, verbose_name="관리비명")
    mg_cost = models.IntegerField(verbose_name="관리비용")

    class Meta:
        db_table = "cost"
        verbose_name = "관리비용"
        verbose_name_plural = "관리비용"

    def __str__(self):
        return self.cost_type


class ProductAddress(CommonModel):
    id = models.AutoField(primary_key=True, verbose_name="매물주소 ID")
    add_new = models.CharField(max_length=255, verbose_name="도로명주소")
    add_old = models.CharField(max_length=255, verbose_name="구주소")
    latitude = models.DecimalField(max_digits=10, decimal_places=6, verbose_name="위도")
    longitude = models.DecimalField(
        max_digits=10, decimal_places=6, verbose_name="경도"
    )

    class Meta:
        db_table = "product_address"
        verbose_name = "주소"

    def __str__(self):
        return self.add_new


class ProductVideo(CommonModel):
    id = models.AutoField(primary_key=True, verbose_name="동영상 ID")
    video_url = models.FileField(
        upload_to="video/", null=True, blank=True, verbose_name="동영상 URL"
    )

    class Meta:
        db_table = "product_video"
        verbose_name = "동영상"

    def __str__(self):
        return self.video_url.url


class ProductDetail(CommonModel):
    HEAT_CHOICES = [
        ("gas", "가스보일러"),
        ("oil", "기름보일러"),
        ("briquet", "연탄보일러"),
        ("heat_etc", "기타"),
    ]
    TYPE_CHOICES = [
        ("detached", "단독주택"),
        ("multi", "다세대주택"),
        ("type_etc", "기타"),
    ]
    id = models.AutoField(primary_key=True, verbose_name="매물 ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="유저 ID")
    pro_title = models.CharField(max_length=50, verbose_name="제목")
    pro_price = models.IntegerField(verbose_name="매물금액")
    pro_supply_a = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="공급면적"
    )
    pro_site_a = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="부지면적"
    )
    pro_heat = models.CharField(
        max_length=10, choices=HEAT_CHOICES, verbose_name="난방방식"
    )
    pro_type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, verbose_name="건물유형"
    )
    pro_floor = models.CharField(max_length=10, verbose_name="층")
    pro_intro = models.TextField(verbose_name="상세설명")
    sale = models.BooleanField(default=True, verbose_name="판매여부")
    cost = models.ForeignKey(Cost, on_delete=models.CASCADE, verbose_name="관리비용 ID")
    address = models.ForeignKey(
        ProductAddress, on_delete=models.CASCADE, verbose_name="주소 ID"
    )
    video = models.ForeignKey(
        ProductVideo,
        on_delete=models.CASCADE,
        verbose_name="동영상 ID",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "product_detail"
        verbose_name = "매물정보"
        verbose_name_plural = "매물정보목록"

    def __str__(self):
        return self.pro_title


class ProductImg(CommonModel):
    id = models.AutoField(primary_key=True, verbose_name="이미지 ID")
    img_url = models.FileField(upload_to="img/", verbose_name="이미지 URL")
    product_detail = models.ForeignKey(
        ProductDetail, on_delete=models.CASCADE, verbose_name="상품 ID"
    )

    class Meta:
        db_table = "product_img"
        verbose_name = "이미지"

    def __str__(self):
        return self.img_url.url

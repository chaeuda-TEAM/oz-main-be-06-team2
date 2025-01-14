from a_common.models import CommonModel
from a_user.models import User

from django.conf import settings
from django.db import models


class ProductAddress(CommonModel):
    add_new = models.CharField(max_length=200, verbose_name="도로명주소")
    add_old = models.CharField(max_length=200, verbose_name="구주소")
    latitude = models.FloatField(verbose_name="위도")
    longitude = models.FloatField(verbose_name="경도")
    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")

    class Meta:
        db_table = "product_address"
        verbose_name = "주소"
        verbose_name_plural = "주소"

    def __str__(self):
        return self.add_new


class ProductVideo(CommonModel):
    id = models.BigAutoField(primary_key=True, verbose_name="동영상 ID")
    video_url = models.FileField(
        upload_to="video/", null=True, blank=True, verbose_name="동영상 URL"
    )
    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")

    class Meta:
        db_table = "product_video"
        verbose_name = "동영상"
        verbose_name_plural = "동영상"

    def __str__(self):
        return self.video_url.url


class ProductDetail(CommonModel):
    HEAT_CHOICES = [
        ("gas", "가스보일러"),
        ("oil", "기름보일러"),
        ("briquette", "연탄보일러"),
        ("heat_etc", "기타"),
    ]
    TYPE_CHOICES = [
        ("detached", "단독주택"),
        ("multi", "다세대주택"),
        ("type_etc", "기타"),
    ]
    id = models.BigAutoField(primary_key=True, verbose_name="매물 ID")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="유저 ID", db_column="user"
    )
    pro_title = models.CharField(max_length=50, verbose_name="제목")
    pro_price = models.IntegerField(verbose_name="매물금액")
    management_cost = models.IntegerField(verbose_name="관리비", null=True, blank=True)
    pro_supply_a = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="공급면적(평수)"
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
    pro_floor = models.IntegerField(verbose_name="층")
    description = models.TextField(verbose_name="상세설명")
    sale = models.BooleanField(default=True, verbose_name="판매여부")

    # 새로운 필드명으로 변경
    pro_rooms = models.IntegerField(verbose_name="방 갯수")
    pro_bathrooms = models.IntegerField(verbose_name="욕실 갯수")
    pro_construction_year = models.IntegerField(verbose_name="건축연도")

    address = models.ForeignKey(
        ProductAddress,
        on_delete=models.CASCADE,
        verbose_name="주소 ID",
        related_name="product_address",
    )
    video = models.ForeignKey(
        ProductVideo,
        on_delete=models.CASCADE,
        verbose_name="동영상 ID",
        null=True,
        blank=True,
        related_name="product_video",
    )
    likes = models.ManyToManyField(
        User,
        through="ProductLikes",
        verbose_name="유저-매물 찜 목록",
        related_name="product_likes",
    )
    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")

    class Meta:
        db_table = "product_detail"
        verbose_name = "매물정보"
        verbose_name_plural = "매물정보"

    def __str__(self):
        return self.pro_title

    def get_user_info(self):
        return f"{self.user.email}"  # 또는 원하는 사용자 정보 표시 형식

    get_user_info.short_description = "사용자"  # admin에서 보여질 컬럼명


class ProductImg(CommonModel):
    id = models.BigAutoField(primary_key=True, verbose_name="이미지 ID")
    img_url = models.FileField(upload_to="img/", verbose_name="이미지 URL")
    product_detail = models.ForeignKey(
        ProductDetail,
        on_delete=models.CASCADE,
        verbose_name="매물 ID",
        related_name="product_images",
    )
    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")

    class Meta:
        db_table = "product_img"
        verbose_name = "이미지"
        verbose_name_plural = "이미지"

    def __str__(self):
        return self.img_url.url


# 중간 테이블 모델
class ProductLikes(CommonModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="유저 ID",
        related_name="user_likes",  # 유저 -> 찜한 매물 접근
    )
    product = models.ForeignKey(
        ProductDetail,
        on_delete=models.CASCADE,
        verbose_name="매물 ID",
        related_name="product_likes",  # 매물 -> 찜한 유저 접근
    )
    is_liked = models.BooleanField(default=False, verbose_name="찜 여부")
    is_deleted = models.BooleanField(default=False, verbose_name="삭제 여부")

    class Meta:
        db_table = "product_like"
        verbose_name = "찜한 매물"
        verbose_name_plural = "찜 목록"
        # 동일한 유저가 같은 매물을 중복해서 찜하지 못하도록
        unique_together = ("user", "product")

from a_apis.models.email_verification import EmailVerification
from a_apis.models.products import (
    ProductAddress,
    ProductDetail,
    ProductImg,
    ProductVideo,
)

from django.contrib import admin

# EmailVerification 모델 등록
admin.site.register(EmailVerification)


# ProductAddress 관리자 클래스
@admin.register(ProductAddress)
class ProductAddressAdmin(admin.ModelAdmin):
    list_display = ("id", "add_new", "add_old", "latitude", "longitude")
    search_fields = ("add_new", "add_old")


# ProductImg 관리자 클래스
@admin.register(ProductImg)
class ProductImgAdmin(admin.ModelAdmin):
    list_display = ("id", "img_url")
    search_fields = ("id", "img_url")



# ProductVideo 관리자 클래스
@admin.register(ProductVideo)
class ProductVideoAdmin(admin.ModelAdmin):
    list_display = ("id", "video_url")
    search_fields = ("id", "video_url")



# ProductDetail 관리자 클래스
@admin.register(ProductDetail)
class ProductDetailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "pro_title",
        "pro_price",
        "pro_type",
        "sale",
    )
    list_filter = ("pro_type", "pro_heat", "sale")
    search_fields = ("pro_title", "pro_intro")

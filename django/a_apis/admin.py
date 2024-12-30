from a_apis.models.email_verification import EmailVerification
from a_apis.models.products import (
    Cost,
    ProductAddress,
    ProductDetail,
    ProductImg,
    ProductVideo,
)

from django.contrib import admin

# EmailVerification 모델 등록
admin.site.register(EmailVerification)


# Cost 관리자 클래스
@admin.register(Cost)
class CostAdmin(admin.ModelAdmin):
    list_display = ("cost_id", "cost_type", "mg_cost")
    search_fields = ("cost_type",)


# ProductAddress 관리자 클래스
@admin.register(ProductAddress)
class ProductAddressAdmin(admin.ModelAdmin):
    list_display = ("address_id", "add_new", "add_old", "latitude", "longitude")
    search_fields = ("add_new", "add_old")


# ProductImg 관리자 클래스
@admin.register(ProductImg)
class ProductImgAdmin(admin.ModelAdmin):
    list_display = ("img_id", "img_url")
    search_fields = ("img_id",)


# ProductVideo 관리자 클래스
@admin.register(ProductVideo)
class ProductVideoAdmin(admin.ModelAdmin):
    list_display = ("video_id", "video_url")
    search_fields = ("video_id",)


# ProductDetail 관리자 클래스
@admin.register(ProductDetail)
class ProductDetailAdmin(admin.ModelAdmin):
    list_display = (
        "product_id",
        "user_no",
        "pro_title",
        "pro_price",
        "pro_type",
        "sale",
    )
    list_filter = ("pro_type", "pro_heat", "sale")
    search_fields = ("pro_title", "pro_intro")
    raw_id_fields = (
        "user_no",
        "cost_id",
        "address_id",
    )

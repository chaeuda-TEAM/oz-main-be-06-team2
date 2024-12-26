from a_apis.models.email_verification import EmailVerification
from a_apis.models.products import Cost, ProductAddress, ProductContents, ProductDetail

from django.contrib import admin

# EmailVerification 모델 등록
admin.site.register(EmailVerification)


# Cost 관리자 클래스
@admin.register(Cost)
class CostAdmin(admin.ModelAdmin):
    list_display = ("cost_id", "cost_type", "mg_cost", "created_at", "updated_at")
    search_fields = ("cost_type",)
    list_filter = ("created_at",)


# ProductAddress 관리자 클래스
@admin.register(ProductAddress)
class ProductAddressAdmin(admin.ModelAdmin):
    list_display = ("address_id", "add_new", "add_old", "latitude", "longitude")
    search_fields = ("add_new", "add_old")


# ProductContents 관리자 클래스
@admin.register(ProductContents)
class ProductContentsAdmin(admin.ModelAdmin):
    list_display = ("contents", "img_url", "video_url")


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
    raw_id_fields = ("user_no", "cost_id", "address_id", "contents")

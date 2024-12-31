from ninja import NinjaAPI

from .auth import router as auth_router
from .health import router as health_router
from .legal import router as legal_router
from .products import public_router as product_public_router
from .products import router as product_router
from .users import nomal_router as user_nomal_router
from .users import router as user_router

api = NinjaAPI(
    title="chaeuda API",
    description="chaeuda API documentation",
    version="1.0.0",
)

api.add_router("/auth/", auth_router, tags=["Auth"])
api.add_router("/users/", user_router, tags=["Users"])
api.add_router("/users/", user_nomal_router, tags=["Users"])
api.add_router("/legal/", legal_router, tags=["Test"])
api.add_router("/", health_router, tags=["Test"])
api.add_router("/product/", product_router, tags=["Products"])
api.add_router("/product/", product_public_router, tags=["Products"])

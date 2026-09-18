from django.conf import settings


def business_identity(request):
    """
    Makes the business name and service brand available in every
    template as {{ business_name }} / {{ service_brand_name }}, so
    branding lives in configuration (spec section 5) instead of being
    hard-coded into templates one by one.
    """
    return {
        "business_name": settings.BUSINESS_NAME,
        "service_brand_name": settings.SERVICE_BRAND_NAME,
        "support_email": settings.SUPPORT_EMAIL,
    }
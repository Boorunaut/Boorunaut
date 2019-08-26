from booru.models import Configuration
from django.conf import settings


def site_title(request):
    return {"SITE_TITLE": Configuration.objects.get(code_name="site_title").value}

def site_description(request):
    return {"SITE_DESCRIPTION": Configuration.objects.get(code_name="site_description").value}

def announcement(request):
    return {"SITE_ANNOUNCEMENT": Configuration.objects.get(code_name="announcement").value}

def custom_code(request):
    return {"INCLUDE_HEADER_CODE": settings.BOORUNAUT_INCLUDE_HEADER_CODE,
            "ADS_CODE": settings.BOORUNAUT_ADS_CODE}

def preferences(request):
    return {"EMBED_MODE": settings.BOORUNAUT_EMBED_MODE}

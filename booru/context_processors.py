from booru.models import Configuration


def site_title(request):
    return {"SITE_TITLE": Configuration.objects.get(code_name="site_title").value}

def announcement(request):
    return {"SITE_ANNOUNCEMENT": Configuration.objects.get(code_name="announcement").value}

def custom_code(request):
    return {"SITE_CUSTOM_CODE": Configuration.objects.get(code_name="custom_code").value}

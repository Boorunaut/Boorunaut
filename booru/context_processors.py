from booru.models import Configuration


def site_title(request):
    return {"SITE_TITLE": Configuration.objects.get(code_name="site_title").value}

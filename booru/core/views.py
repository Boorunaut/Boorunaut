from django.views.generic import TemplateView

from booru.models import Configuration


class TermsOfServiceView(TemplateView):
    template_name = "booru/core/terms_of_service.html"

    def get_context_data(self, **kwargs):
        context = super(TermsOfServiceView, self).get_context_data(**kwargs)
        context['terms_of_service'] = Configuration.objects.filter(code_name="terms_of_service").first().value
        return context

class PrivacyPolicyView(TemplateView):
    template_name = "booru/core/privacy_policy.html"

    def get_context_data(self, **kwargs):
        context = super(PrivacyPolicyView, self).get_context_data(**kwargs)
        context['privacy_policy'] = Configuration.objects.filter(code_name="privacy_policy").first().value
        return context

from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class HomeOrLoginView(UserPassesTestMixin, TemplateView):
    template_name = 'home.html'
    login_url = reverse_lazy('login')  # Redirect to login page if user fails the test function

    def test_func(self):
        return self.request.user.is_authenticated

    # Optionally, if you have additional logic to add, you can override the `get` method
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

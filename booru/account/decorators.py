from django.shortcuts import redirect

def user_is_not_blocked(function):
    def wrap(request, *args, **kwargs):
        if hasattr(request, 'request'):
            user_request = request.request.user # work as self.request.user
        else:
            user_request = request.user

        if user_request.is_authenticated and not user_request.has_priv("can_login"):
            return redirect('account:logout')
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap

from django.shortcuts import render

def sign_in(request):
    return render(request, 'account/sign_in.html', {"current_menu": "sign-in"})

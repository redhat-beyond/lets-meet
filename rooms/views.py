from django.shortcuts import render

def board(request):
    return render(request, 'rooms/welcome_page.html')

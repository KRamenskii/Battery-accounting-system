from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Event

def events_list(request):
    events = Event.objects.all()

    paginator = Paginator(events, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "events/events_list.html", {
        "page_obj": page_obj
    })
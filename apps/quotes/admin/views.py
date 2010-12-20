from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from apps.quotes.models import Quote, QueueQuote

def approve(request, quote_id):
    q = Quote.objects.get(pk=quote_id)
    q.approve()
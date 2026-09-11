from django.http import JsonResponse

from .models import Book


def n_plus_one(request):
    # One query for the books, then one more per book for its author.
    names = [book.author.name for book in Book.objects.all()]
    return JsonResponse({"authors": names})


def select_related(request):
    names = [book.author.name for book in Book.objects.select_related("author")]
    return JsonResponse({"authors": names})

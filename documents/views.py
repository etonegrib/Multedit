import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Document, DocumentImage

def index(request):
    docs = Document.objects.order_by("-updated_at")
    return render(request, "documents/index.html", {"docs": docs})

def create_doc(request):
    if request.method == "POST":
        title = request.POST.get("title") or "Без названия"
        doc = Document.objects.create(title=title)
        return redirect("doc_view", doc_id=doc.id)
    return render(request, "documents/create.html")

def doc_view(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    return render(request, "documents/editor.html", {"doc": doc})

@csrf_exempt
def upload_image(request, doc_id):
    if request.method == "POST" and request.FILES.get("image"):
        doc = get_object_or_404(Document, id=doc_id)
        img = DocumentImage.objects.create(document=doc, image=request.FILES["image"])
        return JsonResponse({"url": img.image.url})
    return JsonResponse({"error": "No image provided"}, status=400)
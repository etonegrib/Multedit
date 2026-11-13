from django.shortcuts import render, get_object_or_404, redirect
from .models import Document

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
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FornecedorForm
from .models import Fornecedor


def admin_required(view):
    return user_passes_test(
        lambda u: u.is_superuser or u.groups.filter(name="Administrador").exists()
    )(view)


@login_required
def lista(request):
    q = request.GET.get("q", "").strip()
    qs = Fornecedor.objects.all()
    if q:
        qs = qs.filter(
            Q(razao_social__icontains=q)
            | Q(nome_fantasia__icontains=q)
            | Q(cnpj__icontains=q)
            | Q(telefone__icontains=q)
            | Q(email__icontains=q)
        )
    pode_editar = request.user.is_superuser or request.user.groups.filter(name="Administrador").exists()
    return render(request, "suppliers/lista.html", {"fornecedores": qs, "q": q, "pode_editar": pode_editar})


@login_required
def detalhe(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    pode_editar = request.user.is_superuser or request.user.groups.filter(name="Administrador").exists()
    form = None

    if pode_editar and (request.method == "POST" or request.GET.get("editar") == "1"):
        form = FornecedorForm(request.POST or None, instance=fornecedor)
        if request.method == "POST" and form.is_valid():
            form.save()
            messages.success(request, "Fornecedor atualizado.")
            return redirect("fornecedor_detalhe", pk=fornecedor.pk)

    return render(request, "suppliers/detalhe.html", {
        "fornecedor": fornecedor,
        "form": form,
        "pode_editar": pode_editar,
    })


@login_required
@admin_required
def criar(request):
    form = FornecedorForm(request.POST or None)
    if form.is_valid():
        fornecedor = form.save()
        messages.success(request, "Fornecedor cadastrado.")
        return redirect("fornecedor_detalhe", pk=fornecedor.pk)
    return render(request, "shared/form.html", {"form": form, "titulo": "Novo fornecedor"})


@login_required
@admin_required
def editar(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    form = FornecedorForm(request.POST or None, instance=fornecedor)
    if form.is_valid():
        form.save()
        messages.success(request, "Fornecedor atualizado.")
        return redirect("fornecedor_detalhe", pk=fornecedor.pk)
    return render(request, "shared/form.html", {"form": form, "titulo": "Editar fornecedor"})

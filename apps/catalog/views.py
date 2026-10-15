from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .models import Produto, Categoria, FichaBotanica
from .forms import ProdutoForm, CategoriaForm, FichaBotanicaForm
from apps.core.models import RegistroAuditoria
def admin_required(view): return user_passes_test(lambda u:u.is_superuser or u.groups.filter(name="Administrador").exists())(view)
@login_required
def lista(request):
    q=request.GET.get("q","").strip()
    qs=Produto.objects.select_related("categoria").all()
    if q: qs=qs.filter(Q(nome__icontains=q)|Q(sku__icontains=q)|Q(categoria__nome__icontains=q))
    if request.GET.get("estoque")=="baixo": qs=qs.filter(estoque__lte=__import__("django").db.models.F("estoque_minimo"))
    return render(request,"catalog/lista.html",{"produtos":qs,"q":q})
@login_required
def detalhe(request,pk):
    p=get_object_or_404(Produto.objects.select_related("categoria"),pk=pk)
    return render(request,"catalog/detalhe.html",{"produto":p})
@login_required
@admin_required
def criar(request):
    form=ProdutoForm(request.POST or None,request.FILES or None)
    if form.is_valid():
        p=form.save()
        RegistroAuditoria.objects.create(usuario=request.user,acao="produto_criado",entidade="Produto",entidade_id=p.pk)
        messages.success(request,"Produto cadastrado com sucesso."); return redirect("catalogo_lista")
    return render(request,"shared/form.html",{"form":form,"titulo":"Novo produto"})
@login_required
@admin_required
def editar(request,pk):
    p=get_object_or_404(Produto,pk=pk); form=ProdutoForm(request.POST or None,request.FILES or None,instance=p)
    if form.is_valid(): form.save(); messages.success(request,"Produto atualizado."); return redirect("catalogo_lista")
    return render(request,"shared/form.html",{"form":form,"titulo":"Editar produto"})
@login_required
@admin_required
def arquivar(request,pk):
    if request.method=="POST":
        p=get_object_or_404(Produto,pk=pk); p.ativo=False; p.save(update_fields=["ativo","atualizado_em"])
        messages.success(request,"Produto arquivado.")
    return redirect("catalogo_lista")

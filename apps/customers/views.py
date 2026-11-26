from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404,redirect,render
from .models import Cliente
from .forms import ClienteForm
def admin_required(view): return user_passes_test(lambda u:u.is_superuser or u.groups.filter(name="Administrador").exists())(view)
@login_required
def lista(request):
 q=request.GET.get("q","").strip(); qs=Cliente.objects.all()
 if q: qs=qs.filter(Q(nome__icontains=q)|Q(telefone__icontains=q)|Q(email__icontains=q))
 return render(request,"customers/lista.html",{"clientes":qs,"q":q})
@login_required
def detalhe(request,pk): return render(request,"customers/detalhe.html",{"cliente":get_object_or_404(Cliente,pk=pk)})
@login_required
@admin_required
def criar(request):
 f=ClienteForm(request.POST or None)
 if f.is_valid(): f.save(); messages.success(request,"Cliente cadastrado."); return redirect("clientes_lista")
 return render(request,"shared/form.html",{"form":f,"titulo":"Novo cliente"})
@login_required
@admin_required
def editar(request,pk):
 c=get_object_or_404(Cliente,pk=pk); f=ClienteForm(request.POST or None,instance=c)
 if f.is_valid(): f.save(); messages.success(request,"Cliente atualizado."); return redirect("clientes_lista")
 return render(request,"shared/form.html",{"form":f,"titulo":"Editar cliente"})

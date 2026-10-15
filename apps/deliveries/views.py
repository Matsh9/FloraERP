from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from .models import Entrega
from .forms import EntregaForm
def admin_required(view): return user_passes_test(lambda u:u.is_superuser or u.groups.filter(name="Administrador").exists())(view)
@login_required
def lista(request):
 qs=Entrega.objects.select_related("pedido","cliente").all()
 if request.GET.get("status"): qs=qs.filter(status=request.GET["status"])
 if request.GET.get("inicio"): qs=qs.filter(data_entrega__gte=request.GET["inicio"])
 if request.GET.get("fim"): qs=qs.filter(data_entrega__lte=request.GET["fim"])
 return render(request,"deliveries/lista.html",{"entregas":qs,"status":request.GET.get("status","")})
@login_required
@admin_required
def criar(request):
 f=EntregaForm(request.POST or None)
 if f.is_valid():
  e=f.save(commit=False)
  if e.status=="entregue": e.entregue_em=timezone.now()
  e.full_clean(); e.save(); messages.success(request,"Entrega registrada."); return redirect("entregas_lista")
 return render(request,"shared/form.html",{"form":f,"titulo":"Agendar entrega"})
@login_required
@admin_required
def editar(request,pk):
 e=get_object_or_404(Entrega,pk=pk); f=EntregaForm(request.POST or None,instance=e)
 if f.is_valid():
  obj=f.save(commit=False)
  if obj.status=="entregue" and not obj.entregue_em: obj.entregue_em=timezone.now()
  obj.full_clean(); obj.save(); messages.success(request,"Entrega atualizada."); return redirect("entregas_lista")
 return render(request,"shared/form.html",{"form":f,"titulo":"Atualizar entrega"})

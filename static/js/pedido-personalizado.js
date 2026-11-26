(function () {
  const grid = document.getElementById('pedidoProductGrid');
  if (!grid) return;

  const cart = new Map();
  const items = document.getElementById('pedidoCartItems');
  const payload = document.getElementById('pedidoCartPayload');
  const count = document.getElementById('pedidoCartCount');
  const subtotalEl = document.getElementById('pedidoSubtotal');
  const submit = document.getElementById('pedidoSubmit');
  const form = document.getElementById('pedidoPersonalizadoForm');

  const parseMoney = value => {
    const number = Number.parseFloat(String(value || '').replace(',', '.'));
    return Number.isFinite(number) ? number : 0;
  };
  const money = value => value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

  grid.addEventListener('click', event => {
    const button = event.target.closest('.pedido-product');
    if (!button) return;

    const key = button.dataset.id ? `p-${button.dataset.id}` : `k-${button.dataset.kit}`;
    const existing = cart.get(key);
    if (existing) {
      existing.quantity += 1;
    } else {
      cart.set(key, {
        key,
        produto_id: button.dataset.id ? Number(button.dataset.id) : undefined,
        kit_id: button.dataset.kit ? Number(button.dataset.kit) : undefined,
        name: button.dataset.name,
        price: parseMoney(button.dataset.price),
        quantity: 1,
      });
    }
    render();
  });

  document.getElementById('pedidoProductSearch').addEventListener('input', event => {
    const query = event.target.value.toLocaleLowerCase('pt-BR');
    grid.querySelectorAll('.pedido-product').forEach(button => {
      const searchable = `${button.dataset.name} ${button.dataset.sku || ''}`.toLocaleLowerCase('pt-BR');
      button.hidden = !searchable.includes(query);
    });
  });

  function render() {
    items.innerHTML = '';
    let subtotal = 0;
    let totalQuantity = 0;

    cart.forEach(item => {
      subtotal += item.price * item.quantity;
      totalQuantity += item.quantity;

      const row = document.createElement('div');
      row.className = 'cart-item';

      const description = document.createElement('div');
      const name = document.createElement('strong');
      name.textContent = item.name;
      const unit = document.createElement('small');
      unit.textContent = `${money(item.price)} cada`;
      description.append(name, document.createElement('br'), unit);

      const controls = document.createElement('div');
      controls.style.textAlign = 'right';
      const quantity = document.createElement('input');
      quantity.type = 'number';
      quantity.min = '0.01';
      quantity.step = '0.01';
      quantity.value = item.quantity;
      quantity.setAttribute('aria-label', `Quantidade de ${item.name}`);
      quantity.addEventListener('change', () => {
        const value = Number(quantity.value);
        if (!Number.isFinite(value) || value <= 0) {
          quantity.value = item.quantity;
          alert('Informe uma quantidade maior que zero.');
          return;
        }
        item.quantity = value;
        render();
      });

      const remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'btn secondary';
      remove.textContent = 'Remover';
      remove.addEventListener('click', () => {
        cart.delete(item.key);
        render();
      });

      controls.append(quantity, document.createElement('br'), remove);
      row.append(description, controls);
      items.append(row);
    });

    if (!cart.size) {
      items.innerHTML = '<div class="empty-state">Selecione um produto para começar.</div>';
    }

    subtotalEl.textContent = money(subtotal);
    count.textContent = `${totalQuantity} itens`;
    payload.value = JSON.stringify([...cart.values()].map(item => ({
      produto_id: item.produto_id,
      kit_id: item.kit_id,
      quantidade: item.quantity,
    })));

    const clienteSelecionado = form.querySelector('[name="cliente"]')?.value;
    submit.disabled = !cart.size || !clienteSelecionado;
  }

  form.querySelector('[name="cliente"]').addEventListener('change', render);
  form.addEventListener('submit', event => {
    if (!cart.size) {
      event.preventDefault();
      return;
    }
    if (!form.querySelector('[name="cliente"]').value) {
      event.preventDefault();
      alert('Selecione um cliente para cadastrar o pedido.');
      return;
    }
    if (!confirm('Cadastrar este pedido personalizado?')) event.preventDefault();
  });

  render();
})();

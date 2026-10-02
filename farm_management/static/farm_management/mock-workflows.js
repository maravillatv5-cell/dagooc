(() => {
    const catalogElement = document.getElementById('mock-product-catalog');
    if (!catalogElement) return;

    let products;
    try {
        products = JSON.parse(catalogElement.textContent);
    } catch {
        return;
    }

    const movementKey = 'dagoocFarmMockInventoryMovements';
    const salesKey = 'dagoocFarmMockSalesTransactions';
    const memoryStore = {};

    function readList(key) {
        try {
            const value = JSON.parse(localStorage.getItem(key) || '[]');
            return Array.isArray(value) ? value : [];
        } catch {
            return memoryStore[key] || [];
        }
    }

    function writeList(key, value) {
        memoryStore[key] = value;
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch {
            return;
        }
    }

    function getProduct(productId) {
        return products.find((product) => product.id === productId);
    }

    function currentStock(productId) {
        const product = getProduct(productId);
        if (!product || !product.inventory_tracked) return null;

        return readList(movementKey).reduce((stock, movement) => {
            if (movement.productId !== productId) return stock;
            const addsStock = movement.type === 'INBOUND' || movement.type === 'HARVEST';
            return stock + (addsStock ? movement.quantity : -movement.quantity);
        }, product.stock);
    }

    function updateStockRows() {
        document.querySelectorAll('[data-stock-row]').forEach((row) => {
            const stock = currentStock(row.dataset.productId);
            const reorderLevel = Number(row.dataset.reorderLevel);
            const lowStock = stock <= reorderLevel;
            const valueCell = row.querySelector('[data-stock-value]');
            const statusCell = row.querySelector('[data-stock-status]');

            if (valueCell) valueCell.textContent = `${stock} ${row.dataset.unit}`;
            if (statusCell) statusCell.textContent = lowStock ? 'Low stock' : 'Healthy';
            row.classList.toggle('warning-row', lowStock);

            const statusRow = document.querySelector(`[data-stock-status-row="${row.dataset.productId}"] strong`);
            if (statusRow) statusRow.textContent = lowStock ? 'Low stock' : 'Healthy';
        });
    }

    function appendCell(row, value) {
        const cell = document.createElement('td');
        cell.textContent = value || '—';
        row.appendChild(cell);
    }

    function updateMovementHistory() {
        const tableBody = document.getElementById('inventory-log-rows');
        if (!tableBody) return;

        const movements = readList(movementKey).slice().reverse();
        tableBody.replaceChildren();
        if (!movements.length) {
            const emptyRow = document.createElement('tr');
            const emptyCell = document.createElement('td');
            emptyCell.colSpan = 6;
            emptyCell.textContent = 'No stock movement records in this browser.';
            emptyRow.appendChild(emptyCell);
            tableBody.appendChild(emptyRow);
            return;
        }

        movements.forEach((movement) => {
            const row = document.createElement('tr');
            appendCell(row, movement.productName);
            appendCell(row, movement.type);
            appendCell(row, `${movement.quantity} ${movement.unit}`);
            appendCell(row, movement.supplier);
            appendCell(row, movement.loggedBy);
            appendCell(row, movement.reason);
            tableBody.appendChild(row);
        });
    }

    function fillSelect(select, options, placeholder, getLabel) {
        select.replaceChildren(new Option(placeholder, ''));
        options.forEach((option) => select.add(new Option(getLabel(option), option)));
        select.disabled = options.length === 0;
    }

    function initInventoryForm() {
        const form = document.getElementById('inventory-movement-form');
        if (!form) return;

        const inventoryProducts = products.filter((product) => product.inventory_tracked);
        const categories = [...new Set(inventoryProducts.map((product) => product.category))];
        const categorySelect = document.getElementById('inventory-category');
        const productSelect = document.getElementById('inventory-product');
        const movementSelect = document.getElementById('movement-type');
        const supplierField = document.getElementById('supplier-field');
        const supplierInput = document.getElementById('movement-supplier');
        const message = document.getElementById('inventory-movement-message');

        categories.forEach((category) => categorySelect.add(new Option(category, category)));

        categorySelect.addEventListener('change', () => {
            const matches = inventoryProducts.filter((product) => product.category === categorySelect.value);
            const placeholder = !categorySelect.value
                ? 'Choose a category first'
                : matches.length ? 'Select product' : 'No stock-tracked products';
            productSelect.replaceChildren(new Option(placeholder, ''));
            matches.forEach((product) => productSelect.add(new Option(product.name, product.id)));
            productSelect.disabled = matches.length === 0;
        });

        movementSelect.addEventListener('change', () => {
            const inbound = movementSelect.value === 'INBOUND';
            supplierField.hidden = !inbound;
            if (!inbound) supplierInput.value = '';
        });

        form.addEventListener('submit', (event) => {
            event.preventDefault();
            const product = getProduct(productSelect.value);
            const quantity = Number(document.getElementById('movement-quantity').value);
            const type = movementSelect.value;
            const actor = form.dataset.actor;

            if (!product || !Number.isInteger(quantity) || quantity <= 0 || !actor) {
                message.textContent = 'Choose a category, product, movement, and positive whole-number quantity.';
                return;
            }

            if (type !== 'INBOUND' && quantity > currentStock(product.id)) {
                message.textContent = `Only ${currentStock(product.id)} ${product.unit} is available.`;
                return;
            }

            const movement = {
                id: `movement-${Date.now()}`,
                productId: product.id,
                productName: product.name,
                category: product.category,
                type,
                quantity,
                unit: product.unit,
                supplier: type === 'INBOUND' ? supplierInput.value.trim() : '',
                reason: document.getElementById('movement-reason').value.trim(),
                loggedBy: actor,
                createdAt: new Date().toISOString(),
            };

            writeList(movementKey, [...readList(movementKey), movement]);
            form.reset();
            categorySelect.dispatchEvent(new Event('change'));
            movementSelect.dispatchEvent(new Event('change'));
            message.textContent = 'Mock inventory movement saved in this browser.';
            updateStockRows();
            updateMovementHistory();
        });
    }

    function initSalesForm() {
        const form = document.getElementById('sales-transaction-form');
        if (!form) return;

        const categorySelect = document.getElementById('sale-category');
        const productSelect = document.getElementById('sale-product');
        const quantityInput = document.getElementById('sale-quantity');
        const addButton = document.getElementById('add-sale-item');
        const completeButton = document.getElementById('complete-sale');
        const cartList = document.getElementById('sale-cart');
        const message = document.getElementById('sales-message');
        const cart = [];
        const categories = [...new Set(products.map((product) => product.category))];
        const money = new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' });

        categories.forEach((category) => categorySelect.add(new Option(category, category)));

        categorySelect.addEventListener('change', () => {
            const matches = products.filter((product) => product.category === categorySelect.value);
            productSelect.replaceChildren(new Option('Select product', ''));
            matches.forEach((product) => {
                const stockNote = product.inventory_tracked ? ` - ${currentStock(product.id)} ${product.unit} available` : '';
                productSelect.add(new Option(`${product.name} (${money.format(product.price)}${stockNote})`, product.id));
            });
            productSelect.disabled = matches.length === 0;
        });

        function renderCart() {
            cartList.replaceChildren();
            cart.forEach((line, index) => {
                const row = document.createElement('li');
                const label = document.createElement('span');
                const amount = document.createElement('strong');
                const remove = document.createElement('button');
                label.textContent = `${line.name} (${line.category}) x${line.quantity}`;
                amount.textContent = money.format(line.quantity * line.price);
                remove.type = 'button';
                remove.className = 'tiny-btn';
                remove.textContent = 'Remove';
                remove.setAttribute('aria-label', `Remove ${line.name}`);
                remove.addEventListener('click', () => {
                    cart.splice(index, 1);
                    renderCart();
                });
                row.append(label, amount, remove);
                cartList.appendChild(row);
            });

            if (!cart.length) {
                const empty = document.createElement('li');
                empty.textContent = 'No items added. Add at least one item to complete a transaction.';
                cartList.appendChild(empty);
            }

            const subtotal = cart.reduce((sum, line) => sum + line.quantity * line.price, 0);
            const tax = Math.round(subtotal * 0.08 * 100) / 100;
            document.getElementById('sale-subtotal').textContent = money.format(subtotal);
            document.getElementById('sale-tax').textContent = money.format(tax);
            document.getElementById('sale-total').textContent = money.format(subtotal + tax);
            completeButton.disabled = cart.length === 0;
        }

        addButton.addEventListener('click', () => {
            const product = getProduct(productSelect.value);
            const quantity = Number(quantityInput.value);
            if (!product || !Number.isInteger(quantity) || quantity <= 0) {
                message.textContent = 'Choose a product and enter a positive whole-number quantity.';
                return;
            }

            if (product.inventory_tracked) {
                const alreadyInCart = cart
                    .filter((line) => line.productId === product.id)
                    .reduce((sum, line) => sum + line.quantity, 0);
                if (alreadyInCart + quantity > currentStock(product.id)) {
                    message.textContent = `Only ${currentStock(product.id) - alreadyInCart} ${product.unit} is available to add.`;
                    return;
                }
            }

            cart.push({
                productId: product.id,
                name: product.name,
                category: product.category,
                quantity,
                unit: product.unit,
                price: product.price,
            });
            message.textContent = '';
            renderCart();
        });

        form.addEventListener('submit', (event) => {
            event.preventDefault();
            if (!cart.length) {
                message.textContent = 'A transaction must contain at least one item.';
                return;
            }

            const actor = form.dataset.actor;
            if (!actor) {
                message.textContent = 'The demo user could not be identified.';
                return;
            }

            for (const line of cart) {
                const product = getProduct(line.productId);
                if (product.inventory_tracked && line.quantity > currentStock(product.id)) {
                    message.textContent = `${product.name} no longer has enough stock to complete this sale.`;
                    return;
                }
            }

            const subtotal = cart.reduce((sum, line) => sum + line.quantity * line.price, 0);
            const tax = Math.round(subtotal * 0.08 * 100) / 100;
            const receipt = `DEMO-${Date.now()}`;
            const transaction = {
                receipt,
                customer: document.getElementById('sale-customer').value.trim(),
                paymentMethod: document.getElementById('sale-payment').value,
                notes: document.getElementById('sale-notes').value.trim(),
                items: cart.map((line) => ({ ...line })),
                subtotal,
                tax,
                total: subtotal + tax,
                processedBy: actor,
                createdAt: new Date().toISOString(),
            };

            writeList(salesKey, [...readList(salesKey), transaction]);
            const saleMovements = cart
                .filter((line) => getProduct(line.productId).inventory_tracked)
                .map((line) => ({
                    id: `movement-${Date.now()}-${line.productId}`,
                    productId: line.productId,
                    productName: line.name,
                    category: line.category,
                    type: 'SALE',
                    quantity: line.quantity,
                    unit: line.unit,
                    supplier: '',
                    reason: `Sales transaction ${receipt}`,
                    loggedBy: actor,
                    createdAt: new Date().toISOString(),
                }));
            writeList(movementKey, [...readList(movementKey), ...saleMovements]);

            cart.splice(0, cart.length);
            form.reset();
            categorySelect.dispatchEvent(new Event('change'));
            renderCart();
            message.textContent = `Mock sale ${receipt} completed in this browser.`;
        });

        renderCart();
    }

    initInventoryForm();
    initSalesForm();
    updateStockRows();
    updateMovementHistory();
})();
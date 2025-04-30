console.log('=== main.js loaded ===');

// Global variables
let currentCustomerId = null;

// Global functions
function editCustomer(id) {
    const modal = document.getElementById('addCustomerModal');
    const form = document.getElementById('customerForm');

    fetch(`/api/customers/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load customer data');
            }
            return response.json();
        })
        .then(customer => {
            document.getElementById('name').value = customer.name;
            document.getElementById('city').value = customer.city;
            document.getElementById('industry').value = customer.industry;
            document.getElementById('cargoType').value = customer.cargo_type;
            document.getElementById('size').value = customer.size;

            modal.style.display = 'block';

            form.onsubmit = function(e) {
                e.preventDefault();

                const formData = {
                    name: document.getElementById('name').value,
                    city: document.getElementById('city').value,
                    industry: document.getElementById('industry').value,
                    cargo_type: document.getElementById('cargoType').value,
                    size: document.getElementById('size').value
                };

                fetch(`/api/customers/${id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to update customer');
                    }
                    return response.json();
                })
                .then(() => {
                    modal.style.display = 'none';
                    form.reset();
                    loadCustomers();
                    form.onsubmit = null;
                })
                .catch(error => {
                    alert('Error updating customer: ' + error.message);
                });
            };
        })
        .catch(error => {
            alert('Error loading customer data: ' + error.message);
        });
}

function deleteCustomer(id) {
    if (confirm('Are you sure you want to delete this customer?')) {
        fetch(`/api/customers/${id}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to delete customer');
            }
            return response.json();
        })
        .then(() => {
            loadCustomers();
        })
        .catch(error => {
            alert('Error deleting customer: ' + error.message);
        });
    }
}

function loadCustomers() {
    fetch('/api/customers/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load customers');
            }
            return response.json();
        })
        .then(customers => {
            const tableBody = document.getElementById('customerTableBody');
            tableBody.innerHTML = '';

            customers.forEach(customer => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${customer.name}</td>
                    <td>${customer.city}</td>
                    <td>${customer.industry}</td>
                    <td>${customer.cargo_type}</td>
                    <td>${customer.size}</td>
                    <td class="action-buttons">
                        <button class="edit-btn" onclick="window.editCustomer(${customer.id})">Edit</button>
                        <button class="delete-btn" onclick="window.deleteCustomer(${customer.id})">Delete</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            alert('Error loading customers: ' + error.message);
        });
}

async function loadSizeOptions() {
    console.log('Loading size options');
    const sizeSelect = document.getElementById('size');

    try {
        const response = await fetch('/api/customers/size-options/');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (!data.options) {
            throw new Error('Invalid response format');
        }

        sizeSelect.innerHTML = data.options.map(option =>
            `<option value="${option.value}">${option.label}</option>`
        ).join('');

        console.log('Size options loaded successfully');
    } catch (error) {
        console.error('Error loading size options:', error);
        alert('Error loading size options. Please refresh the page.');
    }
}

// Make functions globally available
window.editCustomer = editCustomer;
window.deleteCustomer = deleteCustomer;
window.loadCustomers = loadCustomers;
window.loadSizeOptions = loadSizeOptions;

// Initialize the application
function initializeApp() {
    console.log('=== Initializing application ===');

    // Get DOM elements
    const modal = document.getElementById('addCustomerModal');
    const addBtn = document.getElementById('addCustomerBtn');
    const closeBtn = document.querySelector('.close');
    const form = document.getElementById('customerForm');
    const modalTitle = document.getElementById('modalTitle');
    const submitBtn = document.getElementById('submitBtn');

    if (!modal || !addBtn || !closeBtn || !form || !modalTitle || !submitBtn) {
        console.error('Required DOM elements not found');
        return;
    }

    // Event listeners for modal
    addBtn.addEventListener('click', () => {
        console.log('Opening modal for new customer');
        modalTitle.textContent = 'Add New Customer';
        currentCustomerId = null;
        form.reset();
        modal.style.display = 'block';
    });

    closeBtn.addEventListener('click', () => {
        console.log('Closing modal');
        modal.style.display = 'none';
        form.reset();
    });

    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            console.log('Closing modal (outside click)');
            modal.style.display = 'none';
            form.reset();
        }
    });

    // 添加重试函数
    async function fetchWithRetry(url, options, maxRetries = 3) {
        for (let i = 0; i < maxRetries; i++) {
            try {
                console.log(`Attempt ${i + 1} of ${maxRetries} for ${url}`);
                const response = await fetch(url, options);
                console.log(`Response received for ${url}:`, {
                    status: response.status,
                    statusText: response.statusText
                });
                return response;
            } catch (error) {
                console.error(`Attempt ${i + 1} failed:`, error);
                if (i === maxRetries - 1) throw error;
                await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1))); // 递增延迟
            }
        }
    }

    // Form submission handler
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        console.log('Form submitted');

        const formData = {
            name: document.getElementById('name').value,
            city: document.getElementById('city').value,
            industry: document.getElementById('industry').value,
            cargo_type: document.getElementById('cargoType').value,
            size: document.getElementById('size').value
        };

        try {
            const url = currentCustomerId
                ? `/api/customers/${currentCustomerId}`
                : '/api/customers';

            const method = currentCustomerId ? 'PUT' : 'POST';
            console.log('Sending request:', { url, method, formData });

            const response = await fetchWithRetry(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Error response:', {
                    status: response.status,
                    statusText: response.statusText,
                    body: errorText
                });
                try {
                    const errorData = JSON.parse(errorText);
                    throw new Error(errorData.detail || `Server error: ${response.status}`);
                } catch (e) {
                    throw new Error(`Server error: ${response.status} - ${errorText || response.statusText}`);
                }
            }

            const result = await response.json();
            console.log('Save successful:', result);

            modal.style.display = 'none';
            form.reset();
            await loadCustomers();

        } catch (error) {
            console.error('Error saving customer:', error);
            alert('Error saving customer: ' + error.message);
        }
    });

    // Load initial data
    loadSizeOptions();
    loadCustomers();
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

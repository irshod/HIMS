(function () {
    "use strict";

    // Sidebar toggle functionality
    document.addEventListener("DOMContentLoaded", function () {
        const sidebarToggle = document.getElementById('sidebarCollapse');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', toggleSidebar);
        }
    });

    // Loader functionality
    window.addEventListener('load', function () {
        document.querySelector(".loading").style.display = "none";
    });

    // Fullscreen toggle functionality
    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }

    const fullscreenToggle = document.getElementById('fullscreenToggle');
    if (fullscreenToggle) {
        fullscreenToggle.addEventListener('click', toggleFullscreen);
    }

    
    // Dual-list box setup
    function setupDualListBox(availableId, selectedId, addButtonId, removeButtonId, totalPriceId = null) {
        const availableSelect = document.getElementById(availableId);
        const selectedSelect = document.getElementById(selectedId);
        const btnAdd = document.getElementById(addButtonId);
        const btnRemove = document.getElementById(removeButtonId);
        const totalPriceElement = totalPriceId ? document.getElementById(totalPriceId) : null;

        if (!availableSelect || !selectedSelect || !btnAdd || !btnRemove) {
            console.error("Dual list box setup failed: Missing DOM elements.");
            return;
        }

        function moveOptions(fromSelect, toSelect) {
            Array.from(fromSelect.selectedOptions).forEach(option => {
                toSelect.add(option);
                option.selected = true;
            });
            updateTotalPrice();
        }

        function updateTotalPrice() {
            if (totalPriceElement) {
                const totalPrice = Array.from(selectedSelect.options).reduce((sum, option) => {
                    return sum + parseFloat(option.getAttribute('data-price') || 0);
                }, 0);
                totalPriceElement.textContent = totalPrice.toFixed(2);
            }
        }

        btnAdd.addEventListener('click', () => moveOptions(availableSelect, selectedSelect));
        btnRemove.addEventListener('click', () => moveOptions(selectedSelect, availableSelect));
        updateTotalPrice(); // Initialize total price
    }


    // Dynamic Dual-Box Initialization
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".dual-box-init").forEach(element => {
            setupDualListBox(
                element.getAttribute("data-available-id"),
                element.getAttribute("data-selected-id"),
                element.getAttribute("data-add-button-id"),
                element.getAttribute("data-remove-button-id"),
                element.getAttribute("data-total-price-id")
            );
        });
    });

    // Dynamic dual-box setup for services
    document.addEventListener('DOMContentLoaded', function () {
        const departmentSelect = document.getElementById('id_department');
        const doctorSelect = document.getElementById('id_doctor');
        const availableServicesSelect = document.getElementById('availableServices');
        const assignedServicesSelect = document.getElementById('selectedServices');

        if (departmentSelect && doctorSelect && availableServicesSelect && assignedServicesSelect) {
            // Handle department change
            departmentSelect.addEventListener('change', function () {
                const departmentId = this.value;

                // Reset fields if no department is selected
                if (!departmentId) {
                    doctorSelect.innerHTML = '<option value="">Select a department first</option>';
                    availableServicesSelect.innerHTML = '';
                    return;
                }

                // Fetch doctors and services dynamically
                fetch(`/appointments/get_doctors_and_services/?department_id=${departmentId}`)
                    .then(response => response.json())
                    .then(data => {
                        // Populate doctors
                        doctorSelect.innerHTML = '<option value="">Select a doctor</option>';
                        data.doctors.forEach(doctor => {
                            const option = document.createElement('option');
                            option.value = doctor.id;
                            option.textContent = doctor.name;
                            doctorSelect.appendChild(option);
                        });

                        // Populate available services
                        availableServicesSelect.innerHTML = '';
                        data.services.forEach(service => {
                            const option = document.createElement('option');
                            option.value = service.id;
                            option.textContent = `${service.name} - $${service.price}`;
                            option.setAttribute('data-price', service.price);
                            availableServicesSelect.appendChild(option);
                        });

                        // Reinitialize dual-box after dynamic update
                        setupDualListBox(
                            "availableServices",
                            "selectedServices",
                            "btn-add",
                            "btn-remove",
                            "totalPrice"
                        );
                    })
                    .catch(error => console.error('Error fetching doctors and services:', error));
            });

            // Handle doctor change (if additional filtering by doctor is needed)
            doctorSelect.addEventListener('change', function () {
                const doctorId = this.value;

                // Reset fields if no doctor is selected
                if (!doctorId) {
                    availableServicesSelect.innerHTML = '';
                    return;
                }

                // Optional: Implement service filtering based on doctor here
            });
        }
    });

    // CSRF Token Retrieval
    const csrfTokenMeta = document.querySelector('meta[name="csrfmiddlewaretoken"]');
    const csrfToken = csrfTokenMeta ? csrfTokenMeta.getAttribute('content') : null;

    if (!csrfToken) {
        console.error("CSRF token meta tag is missing.");
    }

    // Handle Payment
    document.addEventListener('DOMContentLoaded', function () {
        const payButton = document.getElementById('pay-button');
        const paymentStatus = document.getElementById('payment-status');
    
        if (payButton) {
            payButton.addEventListener('click', function () {
                fetch(processPaymentURL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrfmiddlewaretoken"]').getAttribute('content'),
                    },
                    body: JSON.stringify({}) // Simplified since no payment amount is entered manually
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.success) {
                            paymentStatus.innerText = 'Paid';
                            alert('Payment marked as successful!');
                        } else {
                            alert(`Error: ${data.error}`);
                        }
                    })
                    .catch(error => console.error('Error processing payment:', error));
            });
        }
    });
    
    function printInvoice() {
        const pdfUrl = generatePdfInvoiceURL; // Dynamically passed from the template
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.src = pdfUrl;
        document.body.appendChild(iframe);
        iframe.onload = function () {
            iframe.contentWindow.print();
            setTimeout(() => document.body.removeChild(iframe), 1000);
        };
    }
    
    
    
})();

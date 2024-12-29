// Global AJAX Setup
$.ajaxSetup({
    headers: {
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    }
});

// Utility Functions
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('tr-TR', {
        style: 'currency',
        currency: 'TRY'
    }).format(amount);
};

const formatDate = (date) => {
    return moment(date).format('DD/MM/YYYY');
};

// Sidebar Toggle
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('show');
        });
    }
});

// DataTable Defaults
$.extend(true, $.fn.dataTable.defaults, {
    language: {
        url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/tr.json'
    },
    pageLength: 10,
    responsive: true,
    dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
         '<"row"<"col-sm-12"tr>>' +
         '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
    buttons: ['copy', 'excel', 'pdf', 'print']
});

// Form Validation
const validateForm = (formElement) => {
    const form = document.querySelector(formElement);
    if (!form) return true;

    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
};

// Toast Notifications
const showNotification = (message, type = 'info') => {
    toastr[type](message);
};

// Dynamic Search
const initDynamicSearch = (inputSelector, url, resultSelector) => {
    let timeout = null;
    const input = document.querySelector(inputSelector);
    if (!input) return;

    input.addEventListener('input', (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            const query = e.target.value;
            if (query.length < 2) return;

            fetch(`${url}?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    const resultsContainer = document.querySelector(resultSelector);
                    resultsContainer.innerHTML = '';
                    data.forEach(item => {
                        const element = document.createElement('div');
                        element.classList.add('search-result-item');
                        element.innerHTML = `
                            <div class="d-flex align-items-center p-2 border-bottom">
                                <div>
                                    <h6 class="mb-0">${item.name}</h6>
                                    <small class="text-muted">${item.details}</small>
                                </div>
                            </div>
                        `;
                        resultsContainer.appendChild(element);
                    });
                })
                .catch(error => {
                    console.error('Search error:', error);
                    showNotification('Search failed', 'error');
                });
        }, 300);
    });
};

// Chart Creation Helper
const createChart = (canvasId, config) => {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    return new Chart(ctx, {
        ...config,
        options: {
            ...config.options,
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
};

// File Upload Preview
const initFilePreview = (inputSelector, previewSelector) => {
    const input = document.querySelector(inputSelector);
    const preview = document.querySelector(previewSelector);
    if (!input || !preview) return;

    input.addEventListener('change', function() {
        preview.innerHTML = '';
        const files = Array.from(this.files);

        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = e => {
                    preview.innerHTML += `
                        <div class="preview-item">
                            <img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px">
                            <p class="mt-1 mb-0">${file.name}</p>
                        </div>
                    `;
                };
                reader.readAsDataURL(file);
            }
        });
    });
};

// Export Functions
const exportTable = (tableId, format) => {
    const table = $(`#${tableId}`).DataTable();
    
    switch(format) {
        case 'excel':
            table.button('.buttons-excel').trigger();
            break;
        case 'pdf':
            table.button('.buttons-pdf').trigger();
            break;
        case 'print':
            table.button('.buttons-print').trigger();
            break;
    }
};

// Initialize Components
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Initialize all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

    // Initialize Select2
    $('.select2').select2({
        theme: 'bootstrap-5'
    });

    // Initialize DataTables
    $('.datatable').DataTable();
});

// Yapilacaklar Panel
$("#yapilacaklarBtn").click(function () {
    $("#yapilacaklarPanel").toggle();
});

// Add Yapilacak
$("#addYapilacakBtn").click(function () {
    var yapilacak = $("#yapilacakInput").val();
    var detay = $("#detayInput").val();
    $.post("{% url 'musteri:add_yapilacak' %}", { yapilacak: yapilacak, detay: detay }, function (data) {
        if (data.success) {
            var yapilacakItem = "<li>" + yapilacak + ": " + detay + '<button class="tamamlandiBtn">✔️</button>' + "</li>";
            $("#yapilacaklarList").prepend(yapilacakItem);
            $("#yapilacakInput").val("");
            $("#detayInput").val("");
        }
    });
});

// Tamamlandi Button
$("#yapilacaklarList").on("click", ".tamamlandiBtn", function () {
    var id = $(this).parent().attr("id");
    var btn = $(this);
    $.post(completeYapilacakUrlBase + id, function (data) {
        if (data.success) {
            btn.parent().css("text-decoration", "line-through");
            btn.parent().css("color", "#ccc");
        }
    });
});

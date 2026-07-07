/**
 * LABO.COS App — JavaScript Principal
 * Gère : sidebar toggle, horloge topbar, DataTables par défaut,
 * confirmations de suppression, initialisation des tooltips Bootstrap.
 */

(function($) {
    'use strict';

    /* ============================================================
       1. SIDEBAR TOGGLE
       ============================================================ */
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-collapsed');
            // Persister l'état dans localStorage
            const collapsed = document.body.classList.contains('sidebar-collapsed');
            localStorage.setItem('labocsSidebarCollapsed', collapsed);

            // Fermer les sous-menus ouverts si la sidebar est repliée
            if (collapsed) {
                $('.sidebar-nav .collapse.show').each(function() {
                    bootstrap.Collapse.getOrCreateInstance(this).hide();
                });
            }
        });
    }

    // Restaurer l'état de la sidebar au chargement
    if (localStorage.getItem('labocsSidebarCollapsed') === 'true') {
        document.body.classList.add('sidebar-collapsed');
    }

    // Overlay mobile : fermer la sidebar si on clique en dehors
    document.addEventListener('click', function(e) {
        if (window.innerWidth < 992) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                document.body.classList.remove('sidebar-open');
            }
        }
    });

    if (sidebarToggle && window.innerWidth < 992) {
        sidebarToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            document.body.classList.toggle('sidebar-open');
        });
    }

    /* ============================================================
       2. HORLOGE TOPBAR
       ============================================================ */
    function updateClock() {
        const el = document.getElementById('topbarClock');
        if (!el) return;
        const now = new Date();
        const h = String(now.getHours()).padStart(2, '0');
        const m = String(now.getMinutes()).padStart(2, '0');
        const s = String(now.getSeconds()).padStart(2, '0');
        el.textContent = `${h}:${m}:${s}`;
    }

    updateClock();
    setInterval(updateClock, 1000);

    /* ============================================================
       3. DATATABLES — Configuration globale par défaut
       ============================================================ */
    if (typeof $.fn.DataTable !== 'undefined') {
        $.extend(true, $.fn.dataTable.defaults, {
            language: {
                url: 'https://cdn.datatables.net/plug-ins/2.1.8/i18n/fr-FR.json'
            },
            pageLength: 25,
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, 'Tout']],
            dom: '<"row align-items-center mb-3"<"col-md-6"l><"col-md-6"f>>rtip',
            responsive: true,
            stateSave: true,
            processing: true,
            columnDefs: [
                { orderable: false, targets: -1 }  // Dernière colonne (actions) non triable
            ],
        });

        // Initialiser toutes les tables avec class .labocos-table
        $(document).ready(function() {
            $('.labocos-table').each(function() {
                if (!$.fn.DataTable.isDataTable(this)) {
                    $(this).DataTable();
                }
            });
        });
    }

    /* ============================================================
       4. CONFIRMATIONS DE SUPPRESSION
       ============================================================ */
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('[data-confirm-delete]');
        if (!btn) return;

        e.preventDefault();

        const message = btn.getAttribute('data-confirm-delete') ||
            'Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.';

        if (confirm(message)) {
            // Si c'est un bouton dans un formulaire, soumettre le form
            const form = btn.closest('form');
            if (form) {
                form.submit();
            } else if (btn.href) {
                window.location.href = btn.href;
            }
        }
    });

    /* ============================================================
       5. TOOLTIPS BOOTSTRAP
       ============================================================ */
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].forEach(el => {
        new bootstrap.Tooltip(el, { trigger: 'hover' });
    });

    /* ============================================================
       6. AUTO-DISMISS DES MESSAGES DJANGO
       ============================================================ */
    setTimeout(function() {
        document.querySelectorAll('.messages-container .alert').forEach(function(alert) {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        });
    }, 5000);

    /* ============================================================
       7. SPINNER DE CHARGEMENT SUR SOUMISSION FORMULAIRE
       ============================================================ */
    document.querySelectorAll('form[data-submit-spinner]').forEach(function(form) {
        form.addEventListener('submit', function() {
            const btn = form.querySelector('[type="submit"]');
            if (btn) {
                btn.disabled = true;
                const originalHtml = btn.innerHTML;
                btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Traitement...';
                // Réactiver après 10s en cas d'erreur
                setTimeout(() => {
                    btn.disabled = false;
                    btn.innerHTML = originalHtml;
                }, 10000);
            }
        });
    });

    /* ============================================================
       8. MISE EN ÉVIDENCE DU LIEN ACTIF DANS LA SIDEBAR
       ============================================================ */
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
            // Ouvrir le collapse parent si existant (uniquement si la sidebar est dépliée)
            const collapse = link.closest('.collapse');
            if (collapse && !document.body.classList.contains('sidebar-collapsed')) {
                collapse.classList.add('show');
                const trigger = document.querySelector(`[href="#${collapse.id}"]`);
                if (trigger) {
                    trigger.classList.remove('collapsed');
                    trigger.setAttribute('aria-expanded', 'true');
                }
            }
        }
    });

})(jQuery);

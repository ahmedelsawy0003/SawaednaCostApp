// ==========================================================================
// Atlantis UX Enhancements for Sawaedna Cost App - Core UI Logic
// ==========================================================================

class AtlantisUX {
    constructor() {
        // تهيئة التفاعل الأساسي بعد تحميل الـ DOM
        this.initSidebarToggle();
        this.initAnimations(); 
        this.handleFlashMessages(); // معالجة رسائل الفلاش
        this.setupAdvancedTooltips(); // تهيئة الـ Tooltips
        this.setupDropdowns(); // تهيئة القوائم الفرعية (Sub-menus)
    }
    
    // إعداد الـ Intersection Observer لتحريك العناصر عند الظهور
    initAnimations() {
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                root: null,
                rootMargin: '0px',
                threshold: 0.1
            });

            document.querySelectorAll('.animate-fade-in-up').forEach(element => {
                observer.observe(element);
            });
        }
    }

    // تهيئة وظيفة فتح/إغلاق القائمة الجانبية (للجوال وسطح المكتب)
    initSidebarToggle() {
        const sidebarToggler = document.getElementById('sidebarToggler');
        const sidebar = document.getElementById('sidebar');
        const sidebarClose = document.getElementById('sidebarClose');
        const mainContent = document.querySelector('.modern-main'); 

        const closeSidebar = () => {
            if (sidebar) {
                sidebar.classList.remove('show');
                document.body.classList.remove('sidebar-open');
            }
        };

        const openSidebar = () => {
            if (sidebar) {
                sidebar.classList.add('show');
                document.body.classList.add('sidebar-open');
            }
        };

        if (sidebarToggler) {
            sidebarToggler.addEventListener('click', openSidebar);
        }
        
        if (sidebarClose) {
            sidebarClose.addEventListener('click', closeSidebar);
        }

        // إغلاق القائمة عند النقر على منطقة المحتوى الرئيسية في وضع الجوال
        if (mainContent) {
            mainContent.addEventListener('click', (e) => {
                // نغلق القائمة إذا كانت مفتوحة ونحن في وضع الجوال
                if (document.body.classList.contains('sidebar-open') && window.innerWidth < 992) {
                    // نتأكد أن النقر لم يكن على زر الفتح نفسه أو داخل القائمة
                    if (e.target.closest('#sidebar') === null && e.target.closest('#sidebarToggler') === null) {
                        closeSidebar();
                    }
                }
            });
        }
    }

    // تهيئة القوائم المنسدلة (Sub-menus) في شريط التنقل
    setupDropdowns() {
        const navDropdowns = document.querySelectorAll('.nav-list .has-submenu');
        
        navDropdowns.forEach(dropdown => {
            const toggler = dropdown.querySelector('.sidebar-toggler');
            const submenu = dropdown.querySelector('.sidebar-submenu');
            
            if (!toggler || !submenu) return;

            // تعيين الحالة الأولية للقوائم المفتوحة
            if (submenu.style.maxHeight && submenu.style.maxHeight !== '0px') {
                submenu.style.maxHeight = submenu.scrollHeight + "px";
                dropdown.classList.add('open');
            }

            toggler.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Toggle the 'open' class
                dropdown.classList.toggle('open');

                if (dropdown.classList.contains('open')) {
                    // Open with animation
                    submenu.style.maxHeight = submenu.scrollHeight + "px";
                } else {
                    // Close with animation
                    submenu.style.maxHeight = 0;
                }
            });
        });
    }

    // تهيئة الـ Tooltips (Bootstrap)
    setupAdvancedTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                trigger: 'hover focus',
                placement: 'auto'
            });
        });
    }

    // معالجة رسائل الفلاش (Flash Messages) - تحويلها إلى توست (Toasts)
    handleFlashMessages() {
        // نعتمد الآن على رسائل الفلاش الموجودة في base.html
        const notificationsContainer = document.getElementById('flash-messages-container');
        if (!notificationsContainer) return;
        
        const flashMessages = notificationsContainer.querySelectorAll('.modern-alert');
        
        // إذا كان لديك دالة showToast معرفة في script.js، يمكنك استخدامها هنا
        if (window.showToast) {
            flashMessages.forEach(alertEl => {
                 const categoryClass = alertEl.className.match(/alert-(success|danger|warning|info|secondary|primary)/);
                 const category = categoryClass ? categoryClass[1] : 'info';
                 const messageSpan = alertEl.querySelector('span');
                 const message = messageSpan ? messageSpan.textContent.trim() : 'رسالة نظام';
                 
                 window.showToast(message, category);
                 
                 // إخفاء العنصر القديم من الـ DOM فوراً
                 alertEl.style.display = 'none';
            });
            // إخفاء الحاوية القديمة بعد معالجة الرسائل
            if (flashMessages.length > 0) {
                 setTimeout(() => notificationsContainer.style.display = 'none', 500);
            }
        }
    }
}

// تهيئة نظام أتلانتس عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    new AtlantisUX();
});
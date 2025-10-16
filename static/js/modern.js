// ==========================================================================
// Atlantis UX Enhancements for Sawaedna Cost App
// ==========================================================================

class AtlantisUX {
    constructor() {
        this.initSidebarToggle();
        this.initDropdowns();
        this.initAnimations();
        this.handleFlashMessages();
    }

    // تهيئة وظيفة فتح/إغلاق القائمة الجانبية
    initSidebarToggle() {
        const sidebarToggler = document.getElementById('sidebarToggler');
        const sidebar = document.getElementById('sidebar');
        const sidebarClose = document.getElementById('sidebarClose');
        const mainContent = document.querySelector('.modern-main'); // المحتوى الرئيسي للنقر خارج القائمة

        // دالة إغلاق القائمة
        const closeSidebar = () => {
            if (sidebar) {
                sidebar.classList.remove('show');
                document.body.classList.remove('sidebar-open');
            }
        };

        // دالة فتح القائمة
        const openSidebar = () => {
            if (sidebar) {
                sidebar.classList.add('show');
                document.body.classList.add('sidebar-open');
            }
        };

        // ربط زر الفتح (في الشريط العلوي)
        if (sidebarToggler && sidebar) {
            sidebarToggler.addEventListener('click', openSidebar);
        }
        
        // ربط زر الإغلاق (في القائمة الجانبية نفسها)
        if (sidebarClose && sidebar) {
            sidebarClose.addEventListener('click', closeSidebar);
        }

        // إغلاق القائمة عند النقر على منطقة المحتوى الرئيسية في وضع الجوال
        if (mainContent) {
            mainContent.addEventListener('click', (e) => {
                // نغلق القائمة فقط إذا كانت مفتوحة ونحن على جهاز صغير (< 992px)
                if (document.body.classList.contains('sidebar-open') && window.innerWidth < 992) {
                    // نتأكد أن النقر لم يكن على زر الفتح نفسه (للتجنب تداخُل الإجراءات)
                    if (e.target.closest('#sidebarToggler') === null) {
                        closeSidebar();
                    }
                }
            });
        }
    }

    // تهيئة القوائم المنسدلة (Sub-menus) في شريط التنقل
    initDropdowns() {
        const navLinks = document.querySelectorAll('.nav-dropdown > a');
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const parentItem = this.parentElement;
                
                // إغلاق أي قوائم مفتوحة أخرى
                document.querySelectorAll('.nav-dropdown.open').forEach(openItem => {
                    if (openItem !== parentItem) {
                        openItem.classList.remove('open');
                        const submenu = openItem.querySelector('.nav-submenu');
                        if (submenu) submenu.style.maxHeight = 0;
                    }
                });

                // فتح أو إغلاق القائمة الحالية
                parentItem.classList.toggle('open');
                const submenu = parentItem.querySelector('.nav-submenu');
                
                if (parentItem.classList.contains('open')) {
                    // لفتح القائمة، نحسب ارتفاعها الفعلي
                    submenu.style.maxHeight = submenu.scrollHeight + "px";
                } else {
                    // للإغلاق، نعيد ارتفاعها إلى صفر
                    submenu.style.maxHeight = 0;
                }
            });
            
            // تهيئة حالة الـ max-height للعناصر المفتوحة افتراضياً عند التحميل
            if (link.parentElement.classList.contains('open')) {
                const submenu = link.parentElement.querySelector('.nav-submenu');
                if (submenu) {
                    submenu.style.maxHeight = submenu.scrollHeight + "px";
                }
            }
        });
    }

    // تهيئة الحركات البصرية (مثل التلاشي التدريجي)
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
                root: null, // تتبع الإطار العرضي (Viewport)
                rootMargin: '0px',
                threshold: 0.1 // يبدأ الحركة عندما يكون 10% من العنصر مرئيًا
            });

            document.querySelectorAll('.animate-fade-in-up').forEach(element => {
                observer.observe(element);
            });
        }
    }

    // معالجة رسائل الفلاش (Flash Messages) - إخفاءها تلقائياً بعد فترة
    handleFlashMessages() {
        const alerts = document.querySelectorAll('.flash-messages-container .alert');
        alerts.forEach(alert => {
            // إخفاء الرسائل بعد 5 ثوانٍ
            setTimeout(() => {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) {
                    bsAlert.close();
                } else {
                    alert.remove(); // في حال لم يتم تحميل Bootstrap JS بعد
                }
            }, 5000);
        });
    }
}

// تهيئة نظام أتلانتس عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    new AtlantisUX();
});
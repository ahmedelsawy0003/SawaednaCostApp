// Atlantis Enhancements for Sawaedna Cost App
class AtlantisUX { // الفئة الجديدة لنظام أتلانتس
    constructor() {
        this.init();
    }

    init() {
        this.setupVisualAnimations(); 
        this.setupAdvancedTooltips(); 
        this.handleFlashMessages(); // وظيفة جديدة لمعالجة رسائل Flash القديمة وعرضها كـ Toasts
    }

    setupVisualAnimations() {
        // إضافة Intersection Observer لتحريك العناصر عند التمرير (Fade-in-up)
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in-up');
                }
            });
        }, observerOptions);

        // مراقبة البطاقات وحاويات الجداول
        document.querySelectorAll('.card, .table-responsive').forEach(el => {
            observer.observe(el);
        });
    }

    setupAdvancedTooltips() {
        // تهيئة الـ Tooltips (Bootstrap)
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                trigger: 'hover focus',
                placement: 'auto'
            });
        });
    }

    handleFlashMessages() {
        // العثور على حاوية التنبيهات القديمة من ملف base.html
        const notificationsContainer = document.querySelector('.modern-notifications');
        
        if (notificationsContainer) {
            // التحقق مما إذا كانت هناك رسائل Flash موجودة داخلها
            const flashMessages = notificationsContainer.querySelectorAll('.modern-alert');
            
            // المرور على كل رسالة وعرضها باستخدام نظام showToast الجديد
            flashMessages.forEach(alert => {
                // استخراج نوع الرسالة (success, danger, etc.)
                const categoryClass = alert.className.match(/alert-(success|danger|warning|info)/);
                const category = categoryClass ? categoryClass[1] : 'info';
                
                // استخراج نص الرسالة
                const messageSpan = alert.querySelector('span');
                const message = messageSpan ? messageSpan.textContent.trim() : 'رسالة نظام';

                // استخدام دالة showToast المعرفة عالمياً في script.js
                if (window.showToast) {
                     window.showToast(message, category);
                }
                
                // إخفاء الرسالة القديمة فوراً بعد معالجتها
                alert.style.display = 'none';
            });
            
            // إزالة الحاوية من DOM بعد فترة قصيرة
            if (flashMessages.length > 0) {
                 setTimeout(() => notificationsContainer.remove(), 500);
            }
        }
    }
}

// تهيئة نظام أتلانتس عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    new AtlantisUX();
    
    // تهيئة قائمة الجوال (متبقي لضمان عمل زر الإغلاق والفتح)
    const sidebarToggler = document.getElementById('sidebarToggler');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggler && sidebar) {
        sidebarToggler.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            document.body.classList.toggle('sidebar-open');
        });
        
        const sidebarClose = document.getElementById('sidebarClose');
        if (sidebarClose) {
            sidebarClose.addEventListener('click', function() {
                sidebar.classList.remove('show');
                document.body.classList.remove('sidebar-open');
            });
        }
    }
});
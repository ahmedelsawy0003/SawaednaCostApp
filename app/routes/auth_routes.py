from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.models.project import Project
from app.extensions import db
# --- START: إضافة استيراد النموذج ---
from app.forms import LoginForm
# --- END: إضافة استيراد النموذج ---

auth_bp = Blueprint("auth", __name__)

# ... (كل الدوال الأخرى تبقى كما هي) ...

# --- START: تعديل دالة تسجيل الدخول ---
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("project.get_projects"))
    
    form = LoginForm() # 1. إنشاء نسخة من النموذج
    
    # 2. التحقق من أن النموذج تم إرساله وصالح
    if form.validate_on_submit():
        # 3. الوصول إلى البيانات من النموذج
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("تم تسجيل الدخول بنجاح!", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for("project.get_projects"))
        else:
            flash("اسم المستخدم أو كلمة المرور غير صحيحة.", "danger")
            
    # 4. تمرير النموذج إلى القالب
    return render_template("auth/login.html", form=form)
# --- END: تعديل دالة تسجيل الدخول ---


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("project.get_projects"))
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        
        if User.query.filter_by(username=username).first():
            flash("اسم المستخدم موجود بالفعل.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("البريد الإلكتروني موجود بالفعل.", "danger")
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash("تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("تم تسجيل الخروج بنجاح.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/profile")
@login_required
def profile():
    return render_template("auth/profile.html")

@auth_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)
    users = User.query.all()
    return render_template("admin/dashboard.html", users=users)

@auth_bp.route('/admin/user/<int:user_id>/promote', methods=['POST'])
@login_required
def promote_user(user_id):
    if current_user.role != 'admin':
        abort(403)
    user_to_promote = User.query.get_or_404(user_id)
    user_to_promote.role = 'admin'
    db.session.commit()
    flash(f"تمت ترقية المستخدم {user_to_promote.username} إلى Admin بنجاح.", "success")
    return redirect(url_for('auth.admin_dashboard'))

@auth_bp.route('/admin/user/<int:user_id>/demote', methods=['POST'])
@login_required
def demote_user(user_id):
    if current_user.role != 'admin':
        abort(403)
    user_to_demote = User.query.get_or_404(user_id)
    if user_to_demote.id == current_user.id:
        flash("لا يمكنك تخفيض صلاحيات حسابك.", "danger")
        return redirect(url_for('auth.admin_dashboard'))
    user_to_demote.role = 'user'
    db.session.commit()
    flash(f"تم تخفيض صلاحيات المستخدم {user_to_demote.username} إلى User بنجاح.", "warning")
    return redirect(url_for('auth.admin_dashboard'))

@auth_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        abort(403)
    user_to_delete = User.query.get_or_404(user_id)
    if user_to_delete.id == current_user.id:
        flash("لا يمكنك حذف حسابك الخاص.", "danger")
        return redirect(url_for('auth.admin_dashboard'))
    db.session.delete(user_to_delete)
    db.session.commit()
    flash(f"تم حذف المستخدم {user_to_delete.username} بنجاح.", "success")
    return redirect(url_for('auth.admin_dashboard'))

@auth_bp.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        abort(403)
    
    user_to_edit = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user_to_edit.username = request.form['username']
        user_to_edit.email = request.form['email']
        new_password = request.form.get('password')
        if new_password:
            user_to_edit.set_password(new_password)
        
        assigned_project_ids = request.form.getlist('projects')
        user_to_edit.projects.clear()
        for project_id in assigned_project_ids:
            project = Project.query.get(project_id)
            if project:
                user_to_edit.projects.append(project)

        db.session.commit()
        flash(f"تم تحديث بيانات المستخدم {user_to_edit.username} بنجاح.", "success")
        return redirect(url_for('auth.admin_dashboard'))

    projects = Project.query.all()
    return render_template('admin/edit_user.html', user=user_to_edit, projects=projects)
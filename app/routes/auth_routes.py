from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.extensions import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("project.get_projects"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("تم تسجيل الدخول بنجاح!", "success")
            # Redirect to the intended page or projects page
            next_page = request.args.get('next')
            return redirect(next_page or url_for("project.get_projects"))
        else:
            flash("اسم المستخدم أو كلمة المرور غير صحيحة.", "danger")
    return render_template("auth/login.html")

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

# START: New Admin Dashboard Route
@auth_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    # This line ensures only admins can access this page
    if current_user.role != 'admin':
        abort(403)  # Forbidden error

    users = User.query.all()
    return render_template("admin/dashboard.html", users=users)
# END: New Admin Dashboard Route
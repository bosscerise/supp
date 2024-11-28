from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.routes import auth_bp
from app.models.user import User
from app.forms.auth import LoginForm, RegistrationForm
from datetime import datetime

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    
    GET: Display login form
    POST: Process login form submission
    
    Returns:
        GET: Rendered login template
        POST: Redirect to next page or index
    """
    # Redirect if user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Find user by email
        user = User.query.filter_by(email=form.email.data).first()
        
        # Check if user exists and password is correct
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user account is active
        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        # Log in user and update last login timestamp
        login_user(user, remember=form.remember_me.data)
        user.update_last_login()
        
        # Redirect to next page or index
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        flash('Successfully logged in!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Handle user logout.
    
    Returns:
        Redirect to index page
    """
    logout_user()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle new user registration.
    
    GET: Display registration form
    POST: Process registration form submission
    
    Returns:
        GET: Rendered registration template
        POST: Redirect to login page
    """
    # Redirect if user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user instance
        user = User(
            username=form.username.data,
            email=form.email.data,
            company_name=form.company_name.data,
            address=form.address.data,
            phone=form.phone.data,
            nif=form.nif.data,
            nis=form.nis.data,
            rc=form.rc.data,
            art=form.art.data,
            created_at=datetime.utcnow(),
            is_active=True
        )
        user.set_password(form.password.data)
        
        # Save user to database
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """
    Display user profile information.
    
    Returns:
        Rendered profile template
    """
    return render_template('auth/profile.html', title='Profile', user=current_user)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Handle password change requests.
    
    GET: Display password change form
    POST: Process password change
    
    Returns:
        GET: Rendered password change template
        POST: Redirect to profile page
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Invalid current password.', 'error')
    
    return render_template('auth/change_password.html', title='Change Password', form=form)

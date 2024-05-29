from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import or_
from app import db
from app.models import User, Ticket, Group, Status
from app.forms import TicketForm_edit, TicketForm_create, GroupForm, UserForm
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/tickets', methods=['GET'])
@login_required
def tickets():
        
    if current_user.group_id == 1:
        return render_template('tickets.html', tickets=Ticket.query.all())

    user_tickets = Ticket.query.filter(
        or_(
            Ticket.assigned_user_id == current_user.id,
            Ticket.assigned_group_id == current_user.group_id
        )
    ).all()
    return render_template('tickets.html', tickets=user_tickets)

@bp.route('/create_ticket', methods=['GET', 'POST'])
@login_required
def create_ticket():
    form = TicketForm_create()
    form.assigned_user_id.choices = form.assigned_user_id.choices + [(user.id, user.username) for user in User.query.all()]
    form.assigned_group_id.choices = form.assigned_group_id.choices + [(group.id, f'group {group.name}') for group in Group.query.all()]
    if form.validate_on_submit():
        note = form.note.data
        assigned_user_id = form.assigned_user_id.data if form.assigned_user_id.data != 0 else None
        assigned_group_id = form.assigned_group_id.data if form.assigned_group_id.data != 0 else None
        ticket = Ticket(note=note, assigned_user_id=assigned_user_id, assigned_group_id=assigned_group_id)
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket created successfully', 'success')
        return redirect(url_for('main.tickets'))
    return render_template('create_ticket.html', form=form)

@bp.route('/edit_ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def edit_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    form = TicketForm_edit(obj=ticket)

    if form.validate_on_submit():
        ticket.note = form.note.data
        ticket.status = Status[form.status.data]
        db.session.commit()
        flash('Ticket updated successfully', 'success')
        return redirect(url_for('main.tickets'))
    return render_template('edit_ticket.html', form=form, ticket=ticket)


@bp.route('/groups', methods=['GET'])
@login_required
def groups():
        
    if current_user.group_id == 1:
        return render_template('groups.html', groups=Group.query.all())

    return render_template('groups.html', tickets=[])

@bp.route('/edit_create_group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def edit_create_group(group_id):
    
    if group_id != 0:
        group = Group.query.get_or_404(group_id)
        form = GroupForm(obj=group)
    else:
        form = GroupForm()
        group = Group()

    if form.validate_on_submit():
        name = form.name.data
        group.name = name
        db.session.add(group)
        db.session.commit()
        flash('Group created/updated successfully', 'success')
        return redirect(url_for('main.groups'))
    return render_template('edit_create_group.html', form=form)

@bp.route('/users', methods=['GET'])
@login_required
def users():
    if current_user.group_id != 1:
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('main.index'))

    users = User.query.all()
    return render_template('users.html', users=users)

@bp.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.group_id != 1:
        flash('You do not have permission to create users.', 'danger')
        return redirect(url_for('main.index'))

    form = UserForm()
    form.group.choices=[(group.id, group.name) for group in Group.query.all()]

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            group_id=form.group.data
        )
        user.password_hash = generate_password_hash(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully', 'success')
        return redirect(url_for('main.index'))
    return render_template('create_user.html', form=form)

@bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.group_id != 1:
        flash('You do not have permission to edit users.', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.group.choices=[(group.id, group.name) for group in Group.query.all()]
    if not form.group.data:
        form.group.data = user.group_id    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.group_id = form.group.data
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('main.index'))
    return render_template('edit_user.html', form=form, user=user)
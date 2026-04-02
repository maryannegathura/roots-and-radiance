from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import db
from app.models import ChatSession, Order

admin_bp = Blueprint('admin', __name__)

def login_required(f):
    def wrap(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    from app.config import config  # Avoid circular
    cfg = config['default']()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == cfg.ADMIN_USERNAME and password == cfg.ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        flash('Invalid credentials')
    return render_template('admin_login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin_dashboard.html')

@admin_bp.route('/conversations')
@login_required
def conversations():
    sessions = db.session.query(ChatSession, db.func.count(ChatMessage.id).label('msg_count')).\
        outerjoin(ChatMessage).group_by(ChatSession.id).order_by(ChatSession.created_at.desc()).all()
    return render_template('admin_conversations.html', sessions=sessions)

@admin_bp.route('/orders')
@login_required
def orders():
    orders_list = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin_orders.html', orders=orders_list)

@admin_bp.route('/orders/<int:order_id>/status', methods=['PATCH'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = request.json.get('status')
    if status in ['pending', 'confirmed', 'shipped', 'delivered']:
        order.status = status
        db.session.commit()
        return jsonify({'success': True, 'status': status})
    return jsonify({'error': 'Invalid status'}), 400


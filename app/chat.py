import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from groq import Groq
from app import db, mail
from app.models import ChatSession, ChatMessage, Order
from flask import current_app
from flask_mail import Message
from config import config

api_bp = Blueprint('api', __name__)

SYSTEM_PROMPT = """
You are a helpful customer support assistant for Roots & Radiance, a herbal hair care brand. The product is a 2-in-1 Herbal Shampoo & Conditioner, 250ml, priced at Rs. 1,250 (down from Rs. 1,500). It contains 19 natural herbs including Amla, Aloe Vera, Reetha, Rosemary, Shikakai, Balchar, Alsi, Bael, Brahmi, and Fenugreek. It is free from parabens, sulphates, silicones, and artificial colors. Benefits include strengthening roots, reducing hair fall by up to 70%, removing dandruff, and adding shine. Usage: wet hair, apply and massage for 1 minute, leave 2–3 minutes, rinse. Use 2–3 times per week. Avoid hot water. Payment is Cash on Delivery. Shipping is free. Contact: rootsradiance008@gmail.com, +92 3314141478, Sui Gas Road, Gujranwala, Pakistan. Instagram: @rootsandradiance5. Only answer questions related to this product and brand. If unsure, direct the user to the contact details.
"""

client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

@api_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    session_id = data.get('session_id')

    if not message:
        return jsonify({'error': 'Message required'}), 400

    if not session_id:
        session_id = str(uuid.uuid4())
        session = ChatSession(session_id=session_id)
        db.session.add(session)
    else:
        session = ChatSession.query.filter_by(session_id=session_id).first()

    # Save user message
    user_msg = ChatMessage(session_id=session_id, sender='user', message=message)
    db.session.add(user_msg)
    db.session.commit()

    # Groq AI reply
    try:
        history = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp).all()
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        for msg in history:
            messages.append({'role': msg.sender, 'content': msg.message})

        completion = client.chat.completions.create(
            model='llama3-8b-8192',
            messages=messages
        )
        reply = completion.choices[0].message.content

        # Save bot reply
        bot_msg = ChatMessage(session_id=session_id, sender='bot', message=reply)
        db.session.add(bot_msg)
        db.session.commit()

        return jsonify({'reply': reply, 'session_id': session_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/chat/history/<session_id>')
def chat_history(session_id):
    session = ChatSession.query.filter_by(session_id=session_id).first_or_404()
    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.timestamp).all()
    history = [{'sender': m.sender, 'message': m.message, 'timestamp': m.timestamp.isoformat()} for m in messages]
    return jsonify({'session_id': session_id, 'history': history})

@api_bp.route('/product', methods=['GET'])
def product():
    product_info = {
        'name': 'Roots & Radiance 2-in-1 Herbal Shampoo & Conditioner',
        'volume': '250ml',
        'price': 1250,
        'original_price': 1500,
        'ingredients': ['Amla', 'Aloe Vera', 'Reetha', 'Rosemary', 'Shikakai', 'Balchar', 'Alsi', 'Bael', 'Brahmi', 'Fenugreek'],
        'benefits': ['Strengthens roots', 'Reduces hair fall by up to 70%', 'Removes dandruff', 'Adds shine']
    }
    return jsonify(product_info)

@api_bp.route('/order', methods=['POST'])
def create_order():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    address = data.get('address')
    city = data.get('city')
    country = data.get('country', 'Pakistan')
    quantity = data.get('quantity', 1)

    if not all([name, phone, email, address, city]):
        return jsonify({'error': 'Missing required fields'}), 400

    total_price = quantity * 1250

    order = Order(
        name=name, phone=phone, email=email, address=address,
        city=city, country=country, quantity=quantity, total_price=total_price
    )
    db.session.add(order)
    db.session.commit()

    # Send confirmation email
    msg = Message('New Order - Roots & Radiance', sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=['rootsradiance008@gmail.com'])
    msg.body = f'New order #{order.id}: {name}, {phone}, {city}, Qty: {quantity}, Total: Rs. {total_price}'
    mail.send(msg)

    return jsonify({'order_id': order.id, 'message': 'Order placed successfully'})


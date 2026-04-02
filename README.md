# Roots & Radiance Chatbot Backend + Widget

Complete Flask backend with Groq AI chatbot, orders, admin dashboard. Serves existing static site at root. Injectable chat widget.

## Local Setup

1. **Virtual Environment**:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate  # Windows
   ```

2. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Environment**:
   Copy `.env.example` to `.env` and fill:
   - `GROQ_API_KEY`: Get from [console.groq.com](https://console.groq.com)
   - `FLASK_SECRET_KEY`: `openssl rand -hex 32`
   - `MAIL_PASSWORD`: Gmail App Password for rootsradiance008@gmail.com
   - Others as-is for dev.

4. **Database** (SQLite dev.db auto):
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Run**:
   ```
   python run.py
   ```
   Open http://localhost:5000 (existing site + /chatbot.js auto).

6. **Inject Widget to HTMLs** (manual, no overwrite):
   Add before `</body>` in each .html (Home page.html etc.):
   ```
   <script src="chatbot.js"></script>
   ```
   Refresh - floating green bubble bottom-right.

7. **Test**:
   - Site: http://localhost:5000/Home page.html
   - Chat: Click bubble, send msg → AI reply
   - Admin: http://localhost:5000/admin (admin/password)
   - API: curl -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d '{"message":"hi"}'

## Admin
- /admin/login → Dashboard → Conversations/Orders
- Orders: Update status dropdown.

## Production: Render Deploy

1. Push to GitHub (all files + this README).

2. **New Web Service** (Python):
   - **Build Command**: `pip install -r requirements.txt && flask db upgrade`
   - **Start Command**: `gunicorn run:app`

3. **Environment Vars** (Render dashboard):
   ```
   GROQ_API_KEY=...
   DATABASE_URL=postgres://... (Render PostgreSQL)
   FLASK_SECRET_KEY=...
   MAIL_USERNAME=rootsradiance008@gmail.com
   MAIL_PASSWORD=...
   MAIL_DEFAULT_SENDER=rootsradiance008@gmail.com
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=changeme
   PYTHON_VERSION=3.12.*
   ```

4. Deploy → https://your-app.onrender.com (site + APIs + admin).

## Notes
- Widget injectable anywhere: `<script src="/chatbot.js"></script>`
- DB prod: Render Postgres (free tier).
- Email: Gmail App Pass (not regular pass).
- Customize colors in chatbot.css.

Enjoy! 🌿


# LearnMate AI – Personalized Course Pathways

> **An AI-powered learning platform** that generates personalized learning roadmaps, recommends curated courses, and provides a 24/7 AI tutor — all powered by **IBM Granite via watsonx.ai**.

---

## ✨ Features

| Feature | Status |
|---|---|
| Student Registration & Login | ✅ Implemented |
| Profile & Skill Assessment | ✅ Implemented |
| Career Interest Selection | ✅ Implemented |
| IBM Granite AI Learning Roadmap | ✅ Implemented |
| Course Recommendations | ✅ Implemented |
| AI Learning Chatbot | ✅ Implemented |
| Learning Progress Tracking | ✅ Implemented |

---

## 🛠 Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login
- **Frontend:** HTML5, CSS3, Bootstrap 5.3, JavaScript (Vanilla)
- **Database:** SQLite (via SQLAlchemy ORM)
- **AI:** IBM Granite (`ibm/granite-13b-chat-v2`) via IBM watsonx.ai
- **Auth:** Werkzeug password hashing, Flask-Login sessions

---

## 📁 Project Structure

```
LearnMate-AI/
├── app.py                  # Flask application, routes, models
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── README.md
├── templates/
│   ├── base.html           # Shared layout with sidebar nav
│   ├── index.html          # Landing page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── onboarding.html     # Profile setup (goal + skills)
│   ├── dashboard.html      # Student dashboard
│   ├── roadmap.html        # AI learning roadmap
│   ├── courses.html        # Course library
│   ├── chatbot.html        # AI tutor chat
│   └── profile.html        # User profile
└── static/
    ├── css/
    │   └── style.css       # Full custom design system
    └── js/
        └── main.js         # Frontend interactivity
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
cd LearnMate-AI
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and fill in your IBM watsonx.ai credentials:

```env
WATSONX_API_KEY=your_actual_ibm_api_key
WATSONX_PROJECT_ID=your_actual_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
SECRET_KEY=any-random-string-you-generate
```

**Get credentials from:** [IBM watsonx.ai Console](https://dataplatform.cloud.ibm.com/)

### 3. Run the Application

```bash
python app.py
```

Visit → **http://localhost:5000**

---

## 🔑 IBM watsonx.ai Setup

1. Log into [IBM Cloud](https://cloud.ibm.com)
2. Create a **watsonx.ai** service instance
3. Navigate to **Manage → Access → API Keys** → Generate an API key
4. Open **watsonx.ai Studio** → create a project → copy the **Project ID**
5. Paste both values into your `.env` file

---

## 📡 API Endpoints

| Method | Route | Description |
|---|---|---|
| `POST` | `/api/chat` | Send message to IBM Granite AI tutor |
| `POST` | `/api/progress` | Update course progress status |

### `/api/chat` Request

```json
{ "message": "What Python courses should I take first?" }
```

### `/api/chat` Response

```json
{ "reply": "Based on your goals, I recommend starting with..." }
```

---

## 🎨 Design System

The UI uses a custom design system (`style.css`) with:

- **Color tokens** via CSS custom properties
- **Dark sidebar** navigation with active state highlighting
- **Gradient hero** for landing page
- **Card components** with hover transitions
- **Responsive layout** — mobile sidebar slide-in overlay
- **AI chat bubbles** with typing indicators
- **Progress bars** and status badges

---

## 🔒 Security

- Passwords are hashed using Werkzeug's `pbkdf2:sha256`
- All sensitive routes protected with `@login_required`
- API keys stored in `.env` (never committed to git)
- `.env` is excluded via `.gitignore`

---

## 📈 Roadmap (Upcoming Features)

- [ ] Email verification on registration
- [ ] OAuth login (Google)
- [ ] AI-generated project recommendations
- [ ] Streak / gamification system
- [ ] Admin dashboard
- [ ] Course progress with module-level tracking
- [ ] Export learning roadmap as PDF

---

## 📄 License

MIT © 2025 LearnMate AI

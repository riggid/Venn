# Centroid

# 🧭 Social Compass

Find the perfect meeting spot that's fair for everyone.

## 🚀 Quick Start

```bash
streamlit run main.py
```

## 📁 Project Structure

```
SocialCompass/
├── main.py                 # Application entry point
├── app/
│   ├── data/              # Data layer (repositories)
│   │   ├── accounts.py
│   │   ├── groups.py
│   │   └── credentials.py
│   ├── services/          # Business logic layer
│   │   ├── oauth.py
│   │   ├── geocoding.py
│   │   ├── latlong_api.py
│   │   ├── meeting_optimizer.py
│   │   └── finding_places.py
│   └── ui/                # UI layer
│       ├── styles.py      # Minimal map-themed CSS
│       ├── map_utils.py
│       └── pages/         # Page components
│           ├── landing.py
│           ├── dashboard.py
│           ├── profile.py
│           ├── groups.py
│           ├── find_meeting.py
│           └── sidebar.py
├── accounts.json          # User data
├── groups.json            # Group data
└── credentials.json       # API credentials
```

## 🎨 Design

- **Minimal & Sleek**: Clean, modern interface
- **Map Theme**: Subtle grid overlay and navigation-inspired styling
- **Dark Mode**: Easy on the eyes

## 🔧 Configuration

Create `credentials.json` with:
```json
{
  "installed": {
    "client_id": "YOUR_GOOGLE_CLIENT_ID",
    "client_secret": "YOUR_GOOGLE_CLIENT_SECRET",
    "redirect_uris": ["http://localhost:5000/"],
    "latlong_api_key": "YOUR_LATLONG_API_KEY"
  }
}
```

## 📦 Requirements

See `requirements.txt` for dependencies.
>>>>>>> d6f9f42 (A Lot)

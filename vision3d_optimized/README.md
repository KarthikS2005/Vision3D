# Vision3D Optimized - Text to 3D Generation Platform

A high-performance text-to-3D model generation application with advanced optimization algorithms, caching mechanisms, and a premium modern UI.

## 🚀 Features

- **Optimized Model Generation**: Advanced caching and batch processing
- **Premium UI/UX**: Modern design with smooth animations
- **Performance Monitoring**: Real-time metrics and analytics
- **Smart Caching**: Hash-based deduplication and LRU cache
- **Error Recovery**: Automatic retry with exponential backoff

## 📁 Project Structure

```
vision3d_optimized/
├── backend/              # Django REST API
│   ├── vision3d_backend/ # Main Django project
│   ├── generator/        # 3D generation app with optimizations
│   ├── requirements.txt
│   └── manage.py
└── frontend/             # React + Vite UI
    ├── src/
    ├── package.json
    └── vite.config.js
```

## 🛠️ Setup Instructions

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start development server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

4. Open browser to `http://localhost:5173`

## 🎯 Usage

1. Enter a text prompt (e.g., "a low poly dragon")
2. Click "Generate 3D" button
3. View the generated 3D model with interactive controls
4. Repeated prompts use cached results for instant loading

## ⚡ Optimization Features

- **Request Caching**: Identical prompts return cached models instantly
- **Hash-based Deduplication**: Prevents redundant generation
- **Performance Metrics**: Track generation time and cache hit rate
- **Progressive Loading**: Fast initial response with lazy loading
- **Client-side Cache**: Browser-level caching for better UX

## 📊 Performance

- First generation: ~2-5 seconds (depending on model complexity)
- Cached requests: <100ms
- Cache hit rate: Typically >60% in production

## 🔧 Configuration

Backend settings can be configured in `backend/vision3d_backend/settings.py`:
- Cache timeout duration
- Maximum cache size
- API rate limiting
- CORS settings

## 📝 API Documentation

### Generate 3D Model
- **Endpoint**: `POST /api/generate/`
- **Body**: `{ "prompt": "your text prompt" }`
- **Response**: `{ "success": true, "model_url": "/generated/model_xxx.glb", "cached": false, "generation_time": 2.34 }`

## 🤝 Contributing

This is an optimized version of the Vision3D platform with enhanced performance and user experience.

## 📄 License

MIT License

# F1 ML Predictions - Architecture Overview

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
│  (Chrome, Firefox, Safari, Edge)                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP Requests
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    FLASK WEB SERVER                          │
│                      (app.py)                                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              ROUTE HANDLERS                          │  │
│  │  • /                    (Home Page)                  │  │
│  │  • /binary-classification                            │  │
│  │  • /multiclass-classification                        │  │
│  │  • /regression-position                              │  │
│  │  • /clustering                                       │  │
│  │  • /race-prediction                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API ENDPOINTS                           │  │
│  │  • POST /api/predict-podium                          │  │
│  │  • POST /api/predict-result-class                    │  │
│  │  • POST /api/predict-position                        │  │
│  │  • GET  /api/get-clusters                            │  │
│  │  • POST /api/predict-race                            │  │
│  │  • GET  /api/stats                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           ML MODEL INTEGRATION LAYER                 │  │
│  │  (Currently: Rule-based Demo)                        │  │
│  │  (Future: Trained scikit-learn/XGBoost models)       │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Data Access
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    DATA LAYER                                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  prepared_data.csv                                   │  │
│  │  • 26,000+ race results                              │  │
│  │  • 1950-2024 seasons                                 │  │
│  │  • 16 features per record                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Request Flow

### Example: Podium Prediction

```
1. USER ACTION
   └─> User fills form on binary_classification.html
   └─> Clicks "Predict Podium Finish"

2. FRONTEND (JavaScript)
   └─> Collects form data
   └─> Sends POST request to /api/predict-podium
   └─> Shows loading spinner

3. BACKEND (Flask)
   └─> Receives JSON data
   └─> Validates inputs
   └─> Calls prediction function
   └─> Returns JSON response

4. ML LAYER
   └─> Processes features
   └─> Makes prediction
   └─> Calculates probability

5. RESPONSE
   └─> Backend sends JSON
   └─> Frontend receives data
   └─> Updates UI with results
   └─> Renders charts
```

## 📊 Data Flow Diagram

```
┌─────────────┐
│   CSV File  │
│ (26k rows)  │
└──────┬──────┘
       │
       │ Load on startup
       │
┌──────▼──────┐
│   Pandas    │
│  DataFrame  │
└──────┬──────┘
       │
       │ Query/Sample
       │
┌──────▼──────┐
│  Feature    │
│ Extraction  │
└──────┬──────┘
       │
       │ Transform
       │
┌──────▼──────┐
│  ML Model   │
│ Prediction  │
└──────┬──────┘
       │
       │ Format
       │
┌──────▼──────┐
│    JSON     │
│  Response   │
└──────┬──────┘
       │
       │ HTTP
       │
┌──────▼──────┐
│  Frontend   │
│   Display   │
└─────────────┘
```

## 🎨 Frontend Architecture

```
templates/
│
├── base.html (Master Template)
│   ├── Navigation Bar
│   ├── CSS Styles
│   ├── JavaScript Libraries
│   └── Footer
│
├── index.html (Home Page)
│   ├── Statistics Dashboard
│   ├── Model Cards
│   └── Feature Highlights
│
├── binary_classification.html
│   ├── Input Form (8 fields)
│   ├── Prediction Display
│   ├── Probability Chart
│   └── Quick Presets
│
├── multiclass_classification.html
│   ├── Input Form (4 fields)
│   ├── Class Probabilities
│   └── Bar Chart
│
├── regression_position.html
│   ├── Input Form (4 fields)
│   ├── Position Display
│   └── Confidence Interval
│
├── clustering.html
│   ├── Scatter Plot
│   └── Cluster Descriptions
│
└── race_prediction.html
    ├── Driver Input Form
    ├── Driver List
    └── Results Table
```

## 🔌 API Structure

### Request Format
```json
POST /api/predict-podium
Content-Type: application/json

{
  "grid": 1,
  "qualifying_position": 1,
  "driver_standing_pos": 1,
  "driver_points_cum": 350,
  "driver_wins_cum": 8,
  "constructor_standing_pos": 1,
  "constructor_points_cum": 600,
  "constructor_wins_cum": 12
}
```

### Response Format
```json
{
  "prediction": 1,
  "probability": 0.85,
  "message": "Podium finish predicted!"
}
```

## 🧩 Component Breakdown

### Backend Components

```
app.py
├── Flask App Initialization
├── Data Loading (CSV → DataFrame)
├── Route Handlers
│   ├── Page Routes (render_template)
│   └── API Routes (jsonify)
├── Prediction Functions
│   ├── predict_podium()
│   ├── predict_result_class()
│   ├── predict_position()
│   ├── get_clusters()
│   └── predict_race()
└── Error Handling
```

### Frontend Components

```
Each Page Template
├── HTML Structure
│   ├── Header
│   ├── Input Form
│   ├── Results Section
│   └── Footer
├── CSS Styling
│   ├── Bootstrap Classes
│   └── Custom Styles
└── JavaScript
    ├── Form Handling
    ├── AJAX Requests
    ├── Chart Rendering
    └── UI Updates
```

## 🔐 Security Layers

```
┌─────────────────────────────────────┐
│  Input Validation (Frontend)        │
│  • Type checking                    │
│  • Range validation                 │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│  Request Validation (Backend)       │
│  • JSON parsing                     │
│  • Data type verification           │
│  • Range checking                   │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│  Error Handling                     │
│  • Try-catch blocks                 │
│  • Graceful degradation             │
│  • User-friendly messages           │
└─────────────────────────────────────┘
```

## 📈 Scalability Considerations

### Current (Development)
```
Single Flask Process
├── Handles ~100 requests/second
├── In-memory data storage
└── Synchronous processing
```

### Future (Production)
```
Load Balancer
├── Multiple Flask Workers
│   ├── Worker 1
│   ├── Worker 2
│   └── Worker N
├── Redis Cache
│   ├── Prediction cache
│   └── Session storage
├── Database
│   ├── PostgreSQL (predictions)
│   └── MongoDB (logs)
└── CDN
    └── Static assets
```

## 🔄 Model Integration Flow

### Current (Demo)
```
User Input → Rule-based Logic → Response
```

### With Real Models
```
User Input
    ↓
Feature Engineering
    ↓
Load Trained Model (pickle)
    ↓
Model.predict()
    ↓
Post-processing
    ↓
JSON Response
```

## 📦 Deployment Architecture

### Local Development
```
localhost:5000
└── Flask Development Server
```

### Production Options

#### Option 1: Traditional Server
```
Nginx (Reverse Proxy)
    ↓
Gunicorn (WSGI Server)
    ↓
Flask Application
    ↓
PostgreSQL Database
```

#### Option 2: Cloud Platform
```
Heroku / AWS / Azure
├── Web Dyno/Instance
├── Database Service
└── Static File Storage
```

#### Option 3: Containerized
```
Docker Container
├── Flask App
├── Nginx
└── Dependencies
    ↓
Kubernetes Cluster
```

## 🎯 Technology Stack Summary

```
┌─────────────────────────────────────┐
│         PRESENTATION LAYER          │
│  • HTML5                            │
│  • CSS3 (Bootstrap 5)               │
│  • JavaScript (Vanilla + Chart.js)  │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│         APPLICATION LAYER           │
│  • Flask (Python Web Framework)     │
│  • Jinja2 (Template Engine)         │
│  • RESTful API                      │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│         BUSINESS LOGIC LAYER        │
│  • ML Models (scikit-learn)         │
│  • Data Processing (pandas)         │
│  • Numerical Computing (numpy)      │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│         DATA LAYER                  │
│  • CSV Files                        │
│  • Pickle Files (models)            │
└─────────────────────────────────────┘
```

## 🔍 Monitoring & Logging

### Current
```
Console Logging
└── Flask debug output
```

### Production Ready
```
Logging Framework
├── Application Logs
│   ├── Request/Response
│   ├── Errors
│   └── Performance
├── ML Model Logs
│   ├── Predictions
│   ├── Confidence scores
│   └── Feature importance
└── System Logs
    ├── CPU/Memory usage
    └── Response times
```

## 🎓 Design Patterns Used

1. **MVC Pattern**
   - Model: Data + ML logic
   - View: HTML templates
   - Controller: Flask routes

2. **RESTful API**
   - Resource-based URLs
   - HTTP methods (GET, POST)
   - JSON responses

3. **Template Inheritance**
   - base.html as parent
   - Child templates extend base

4. **Separation of Concerns**
   - Frontend (templates/)
   - Backend (app.py)
   - Data (CSV files)

## 🚀 Performance Optimization

### Current
- In-memory data loading
- Simple rule-based predictions
- Client-side rendering

### Future Optimizations
- Redis caching
- Model prediction caching
- Database connection pooling
- Async processing
- CDN for static assets
- Lazy loading
- Code minification

---

This architecture provides a solid foundation for a production-ready ML web application! 🏎️

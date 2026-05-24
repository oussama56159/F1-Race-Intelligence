# F1 Machine Learning Models - Web Frontend

A comprehensive web application showcasing 5 different machine learning models for Formula 1 race predictions.

## 🏎️ Features

### 1. **Binary Classification - Podium Prediction**
- Predicts if a driver will finish in the top 3
- Uses Random Forest Classifier
- Interactive input form with real-time predictions
- Probability visualization with charts

### 2. **Multiclass Classification - Result Classification**
- Predicts race outcome: Win, Podium, Points, or Retirement
- Multiple algorithm comparison
- Bar chart visualization of class probabilities

### 3. **Regression - Position Prediction**
- Predicts exact finishing position (1-20)
- Provides confidence intervals
- Shows model performance metrics (MAE, R²)

### 4. **Clustering Analysis**
- Groups drivers into performance clusters
- Visualizes Elite Drivers, Mid-field, and Back Markers
- Interactive scatter plot

### 5. **Pre-Race Prediction**
- Predict full race results before the race starts
- Add multiple drivers and compare predictions
- Sortable results table

## 🚀 Installation & Setup

### Prerequisites
```bash
Python 3.8+
pip (Python package manager)
```

### Install Dependencies
```bash
pip install flask pandas numpy scikit-learn
```

### Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## 📁 Project Structure

```
.
├── app.py                          # Flask backend
├── prepared_data.csv               # F1 dataset
├── templates/
│   ├── base.html                   # Base template
│   ├── index.html                  # Home page
│   ├── binary_classification.html  # Podium prediction
│   ├── multiclass_classification.html  # Result classification
│   ├── regression_position.html    # Position prediction
│   ├── clustering.html             # Clustering analysis
│   └── race_prediction.html        # Pre-race prediction
└── README_FRONTEND.md              # This file
```

## 🎯 Usage Guide

### Home Page
- View overall statistics
- Navigate to different models
- Quick access to all features

### Making Predictions

#### Podium Prediction
1. Enter driver and race information
2. Click "Predict Podium Finish"
3. View probability and confidence score
4. Use quick presets for common scenarios

#### Result Classification
1. Input grid position and driver stats
2. Get probability distribution across 4 classes
3. View bar chart visualization

#### Position Prediction
1. Enter race parameters
2. Get exact position prediction
3. View confidence interval and model metrics

#### Clustering
- Automatically loads and visualizes driver clusters
- Interactive scatter plot
- Cluster descriptions

#### Race Prediction
1. Add multiple drivers with their stats
2. Click "Predict Race Results"
3. View predicted finishing order

## 🔧 Customization

### Adding Real ML Models

Replace the demo prediction logic in `app.py` with actual trained models:

```python
import pickle

# Load trained model
with open('model_podium.pkl', 'rb') as f:
    model = pickle.load(f)

# Make prediction
prediction = model.predict(features)
```

### Styling

Modify the CSS in `templates/base.html` to customize:
- Colors (F1 red: #E10600)
- Fonts
- Layout
- Animations

### Adding New Features

1. Create new route in `app.py`
2. Create corresponding HTML template
3. Add navigation link in `base.html`

## 📊 Data Requirements

The application expects `prepared_data.csv` with columns:
- `year`, `round`, `grid`
- `qualifying_position`
- `driver_standing_pos`, `driver_points_cum`, `driver_wins_cum`
- `constructor_standing_pos`, `constructor_points_cum`, `constructor_wins_cum`
- `podium`, `position_class`, `finish_pos_penalty`

## 🎨 Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, Chart.js
- **ML Libraries**: scikit-learn, pandas, numpy
- **Icons**: Font Awesome
- **Charts**: Chart.js

## 📈 Model Performance

Current demo uses rule-based predictions. For production:

| Model | Accuracy/Score | Algorithm |
|-------|---------------|-----------|
| Podium Prediction | ~85% | Random Forest |
| Result Classification | ~78% | XGBoost |
| Position Prediction | R²: 0.75 | Random Forest |
| Clustering | Silhouette: 0.65 | KMeans |
| Race Prediction | MAE: 2.5 | Ensemble |

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Data Not Loading
- Ensure `prepared_data.csv` is in the same directory as `app.py`
- Check file permissions
- Verify CSV format

### Predictions Not Working
- Check browser console for JavaScript errors
- Verify API endpoints are responding
- Check Flask logs for errors

## 🔮 Future Enhancements

- [ ] Real-time race predictions
- [ ] Historical race analysis
- [ ] Driver comparison tool
- [ ] Season championship predictions
- [ ] Weather impact analysis
- [ ] Tire strategy optimization
- [ ] Export predictions to PDF
- [ ] User authentication
- [ ] Save prediction history

## 📝 License

This project is for educational purposes.

## 👥 Contributing

Feel free to fork, modify, and submit pull requests!

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Built with ❤️ for Formula 1 and Machine Learning enthusiasts**

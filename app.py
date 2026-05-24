"""
F1 ML Models Web Application
Flask backend — uses real trained models (pickle files in models/)
"""

import warnings
warnings.filterwarnings('ignore')

import os
import pickle
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────
# Load data & models at startup
# ─────────────────────────────────────────────────────────────
print("Loading dataset...")
try:
    df = pd.read_csv('prepared_data.csv')
    # Pre-encode country so it's always available
    if 'country' in df.columns:
        _le_country_global = LabelEncoder()
        df['country_encoded'] = _le_country_global.fit_transform(df['country'].astype(str))
    print(f"  Dataset loaded: {df.shape}")
except Exception as e:
    print(f"  ERROR loading dataset: {e}")
    df = None
    _le_country_global = None

def _load(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

print("Loading models...")
try:
    model_binary     = _load('models/model_binary.pkl')
    meta_binary      = _load('models/features_binary.pkl')

    model_multiclass = _load('models/model_multiclass.pkl')
    meta_multiclass  = _load('models/features_multiclass.pkl')

    model_regression = _load('models/model_regression.pkl')
    meta_regression  = _load('models/features_regression.pkl')

    model_clustering = _load('models/model_clustering.pkl')
    cluster_data     = _load('models/cluster_data.pkl')

    model_prerace    = _load('models/model_prerace.pkl')
    meta_prerace     = _load('models/features_prerace.pkl')

    print("  All models loaded ✓")
except Exception as e:
    print(f"  ERROR loading models: {e}")
    model_binary = model_multiclass = model_regression = None
    model_clustering = model_prerace = None
    meta_binary = meta_multiclass = meta_regression = None
    meta_prerace = cluster_data = None

# ─────────────────────────────────────────────────────────────
# Helper: build a one-row DataFrame with the right columns
# ─────────────────────────────────────────────────────────────
def _make_row(data: dict, feature_names: list) -> pd.DataFrame:
    """Return a single-row DataFrame aligned to feature_names."""
    row = {col: [data.get(col, np.nan)] for col in feature_names}
    return pd.DataFrame(row)

# ─────────────────────────────────────────────────────────────
# Page routes
# ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/binary-classification')
def binary_classification():
    return render_template('binary_classification.html',
                           metrics=meta_binary.get('metrics', {}) if meta_binary else {})

@app.route('/multiclass-classification')
def multiclass_classification():
    return render_template('multiclass_classification.html',
                           metrics=meta_multiclass.get('metrics', {}) if meta_multiclass else {})

@app.route('/regression-position')
def regression_position():
    return render_template('regression_position.html',
                           metrics=meta_regression.get('metrics', {}) if meta_regression else {})

@app.route('/clustering')
def clustering():
    return render_template('clustering.html',
                           silhouette=cluster_data.get('silhouette', 0) if cluster_data else 0,
                           explained_var=cluster_data.get('explained_variance', 0) if cluster_data else 0)

@app.route('/race-prediction')
def race_prediction():
    return render_template('race_prediction.html',
                           metrics=meta_prerace.get('metrics', {}) if meta_prerace else {})

# ─────────────────────────────────────────────────────────────
# API — Binary Classification (Podium)
# ─────────────────────────────────────────────────────────────
@app.route('/api/predict-podium', methods=['POST'])
def predict_podium():
    if model_binary is None:
        return jsonify({'error': 'Model not loaded'}), 500
    try:
        data = request.json
        feature_names = meta_binary['feature_names']

        # country → country_encoded if needed
        if 'country' in feature_names and 'country' not in data:
            data['country'] = 'Unknown'

        X = _make_row(data, feature_names)
        prediction  = int(model_binary.predict(X)[0])
        probability = float(model_binary.predict_proba(X)[0][1])

        return jsonify({
            'prediction': prediction,
            'probability': round(probability, 4),
            'message': 'Podium finish predicted! 🏆' if prediction == 1 else 'No podium predicted',
            'metrics': meta_binary.get('metrics', {})
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ─────────────────────────────────────────────────────────────
# API — Multiclass Classification
# ─────────────────────────────────────────────────────────────
@app.route('/api/predict-result-class', methods=['POST'])
def predict_result_class():
    if model_multiclass is None:
        return jsonify({'error': 'Model not loaded'}), 500
    try:
        data = request.json
        feature_names = meta_multiclass['feature_names']
        class_map     = meta_multiclass['class_map']          # {0:'win',1:'podium',...}

        # Encode country if present in features
        le_country = meta_multiclass.get('le_country')
        if 'country_encoded' in feature_names and 'country_encoded' not in data:
            country_str = data.get('country', 'Unknown')
            if le_country is not None:
                try:
                    data['country_encoded'] = int(le_country.transform([country_str])[0])
                except Exception:
                    data['country_encoded'] = 0

        X = _make_row(data, feature_names)
        pred_class   = int(model_multiclass.predict(X)[0])
        proba        = model_multiclass.predict_proba(X)[0]
        classes      = model_multiclass.classes_

        probabilities = {class_map.get(int(c), str(c)): round(float(p), 4)
                         for c, p in zip(classes, proba)}

        return jsonify({
            'prediction': class_map.get(pred_class, str(pred_class)),
            'probabilities': probabilities,
            'metrics': meta_multiclass.get('metrics', {})
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ─────────────────────────────────────────────────────────────
# API — Regression (finish position)
# ─────────────────────────────────────────────────────────────
@app.route('/api/predict-position', methods=['POST'])
def predict_position():
    if model_regression is None:
        return jsonify({'error': 'Model not loaded'}), 500
    try:
        data = request.json
        feature_names = meta_regression['feature_names']

        # Model uses country as raw string (OneHotEncoded in pipeline)
        # position_class_encoded: derive from position_class if not provided
        if 'position_class_encoded' in feature_names and 'position_class_encoded' not in data:
            # Default to 2 (points zone) if unknown
            data['position_class_encoded'] = data.get('position_class', 2)

        X = _make_row(data, feature_names)
        predicted = float(model_regression.predict(X)[0])
        predicted = max(1.0, min(20.0, predicted))

        # Rough confidence interval (±1 MAE)
        mae = meta_regression['metrics'].get('mae', 3.0)
        ci_low  = max(1,  int(round(predicted - mae)))
        ci_high = min(20, int(round(predicted + mae)))

        return jsonify({
            'predicted_position': round(predicted, 1),
            'confidence_interval': [ci_low, ci_high],
            'metrics': meta_regression.get('metrics', {})
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ─────────────────────────────────────────────────────────────
# API — Clustering
# ─────────────────────────────────────────────────────────────
@app.route('/api/get-clusters', methods=['GET'])
def get_clusters():
    if cluster_data is None:
        return jsonify({'error': 'Cluster data not loaded'}), 500
    try:
        return jsonify({
            'pca_coords':       cluster_data['pca_coords'],
            'labels':           cluster_data['labels'],
            'cluster_names':    cluster_data['cluster_names'],
            'silhouette':       round(cluster_data['silhouette'], 4),
            'explained_variance': round(cluster_data['explained_variance'], 4)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/predict-cluster', methods=['POST'])
def predict_cluster():
    """Assign a new data point to a cluster."""
    if model_clustering is None:
        return jsonify({'error': 'Model not loaded'}), 500
    try:
        data = request.json
        feature_names = model_clustering['feature_names']
        X_raw = _make_row(data, feature_names)

        imp    = model_clustering['imputer']
        scaler = model_clustering['scaler']
        pca    = model_clustering['pca']
        km     = model_clustering['kmeans']

        X_imp    = imp.transform(X_raw)
        X_sc     = scaler.transform(X_imp)
        X_pca    = pca.transform(X_sc)
        cluster  = int(km.predict(X_pca)[0])
        names    = cluster_data['cluster_names']

        return jsonify({
            'cluster': cluster,
            'cluster_name': names[cluster] if cluster < len(names) else f'Cluster {cluster}',
            'pca_x': float(X_pca[0][0]),
            'pca_y': float(X_pca[0][1])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ─────────────────────────────────────────────────────────────
# API — Pre-Race Regression
# Model predicts positions_gagnees (grid - finish), then we
# convert back: predicted_finish = grid - positions_gagnees
# ─────────────────────────────────────────────────────────────
@app.route('/api/predict-race', methods=['POST'])
def predict_race():
    if model_prerace is None:
        return jsonify({'error': 'Model not loaded'}), 500
    try:
        data    = request.json
        drivers = data.get('drivers', [])
        feature_names = meta_prerace['feature_names']

        predictions = []
        for driver in drivers:
            d = dict(driver)
            grid = float(d.get('grid', 10))

            # Engineered features — use grid as proxy for rolling averages
            # when historical data is not available from the frontend
            if 'avg_pos_gagnees_3' not in d:
                d['avg_pos_gagnees_3'] = 0.0   # neutral: no positions gained/lost
            if 'avg_grid_3' not in d:
                d['avg_grid_3'] = grid
            if 'grid_driver_interaction' not in d:
                d['grid_driver_interaction'] = grid * float(d.get('driver_standing_pos', 10))

            X = _make_row(d, feature_names)
            positions_gained = float(model_prerace.predict(X)[0])

            # Convert back to finish position: finish = grid - positions_gained
            predicted_finish = grid - positions_gained
            predicted_finish = max(1.0, min(20.0, predicted_finish))

            predictions.append({
                'driver_name':        driver.get('name', 'Unknown'),
                'predicted_position': round(predicted_finish, 1),
                'positions_gained':   round(positions_gained, 1),
                'grid_position':      driver.get('grid', '?')
            })

        predictions.sort(key=lambda x: x['predicted_position'])
        for i, p in enumerate(predictions):
            p['rank'] = i + 1

        return jsonify({
            'predictions': predictions,
            'metrics': meta_prerace.get('metrics', {})
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ─────────────────────────────────────────────────────────────
# API — Dataset statistics
# ─────────────────────────────────────────────────────────────
@app.route('/api/stats')
def get_stats():
    if df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    try:
        return jsonify({
            'total_records':    int(df.shape[0]),
            'years_covered':    f"{int(df['year'].min())} – {int(df['year'].max())}",
            'num_countries':    int(df['country'].nunique()) if 'country' in df.columns else 0,
            'podium_rate':      round(float(df['podium'].mean() * 100), 1),
            'avg_grid':         round(float(df['grid'].mean()), 1),
            'models_available': 5,
            'model_metrics': {
                'binary':     meta_binary.get('metrics', {})     if meta_binary     else {},
                'multiclass': meta_multiclass.get('metrics', {}) if meta_multiclass else {},
                'regression': meta_regression.get('metrics', {}) if meta_regression else {},
                'clustering': {'silhouette': cluster_data.get('silhouette', 0)} if cluster_data else {},
                'prerace':    meta_prerace.get('metrics', {})    if meta_prerace    else {}
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

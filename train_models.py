"""
Train all 5 F1 ML models and save them as pickle files.
Replicates the exact preprocessing and best models from each notebook.
"""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split, StratifiedKFold, KFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.svm import SVC, SVR
from sklearn.linear_model import LinearRegression
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score,
    mean_absolute_error, r2_score, silhouette_score
)
from xgboost import XGBClassifier, XGBRegressor

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
os.makedirs('models', exist_ok=True)

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
print("Loading data...")
df = pd.read_csv('prepared_data.csv')
print(f"  Shape: {df.shape}")

# ─────────────────────────────────────────────
# OBJECTIVE 1 — Binary Classification (Podium)
# Matches notebook 04_obj1_binary_classification.ipynb exactly:
# - Best model: XGBoost Grid Search (Accuracy 0.913, AUC 0.948)
# - Leakage: position_class, finish_pos_penalty, position_class_encoded
# - Uses ColumnTransformer with OneHotEncoder for categorical features
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("OBJECTIVE 1 — Binary Classification (Podium)")
print("="*60)

TARGET_BIN = 'podium'
LEAKAGE_BIN = ['position_class', 'finish_pos_penalty', 'position_class_encoded']

X_bin = df.drop(columns=[TARGET_BIN] + [c for c in LEAKAGE_BIN if c in df.columns])
y_bin = df[TARGET_BIN].astype(int)

numeric_features_bin = X_bin.select_dtypes(include='number').columns.tolist()
categorical_features_bin = X_bin.select_dtypes(include=['object', 'category']).columns.tolist()

numeric_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])
categorical_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])
preprocessor_bin = ColumnTransformer([
    ('num', numeric_transformer, numeric_features_bin),
    ('cat', categorical_transformer, categorical_features_bin)
])

X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(
    X_bin, y_bin, test_size=0.2, stratify=y_bin, random_state=RANDOM_STATE
)

# Best model from notebook: XGBoost Grid Search
# (learning_rate=0.05, n_estimators=200)
pipeline_bin = Pipeline([
    ('preprocessor', preprocessor_bin),
    ('model', XGBClassifier(
        eval_metric='logloss',
        learning_rate=0.05,
        n_estimators=200,
        random_state=RANDOM_STATE,
        n_jobs=-1
    ))
])
pipeline_bin.fit(X_train_b, y_train_b)

y_pred_b = pipeline_bin.predict(X_test_b)
y_prob_b = pipeline_bin.predict_proba(X_test_b)[:, 1]
acc_b  = accuracy_score(y_test_b, y_pred_b)
f1_b   = f1_score(y_test_b, y_pred_b, average='weighted')
auc_b  = roc_auc_score(y_test_b, y_prob_b)
print(f"  Accuracy: {acc_b:.4f} | F1-weighted: {f1_b:.4f} | ROC-AUC: {auc_b:.4f}")

with open('models/model_binary.pkl', 'wb') as f:
    pickle.dump(pipeline_bin, f)
with open('models/features_binary.pkl', 'wb') as f:
    pickle.dump({
        'feature_names': X_bin.columns.tolist(),
        'numeric_features': numeric_features_bin,
        'categorical_features': categorical_features_bin,
        'target': TARGET_BIN,
        'metrics': {'accuracy': acc_b, 'f1_weighted': f1_b, 'roc_auc': auc_b}
    }, f)
print("  ✓ Saved models/model_binary.pkl")

# ─────────────────────────────────────────────
# OBJECTIVE 2 — Multiclass Classification
# Matches notebook 05_obj2_multiclass_classification.ipynb exactly:
# - Best model: XGBoost Grid Search (Accuracy 0.68, F1-macro 0.59)
# - Leakage: podium, finish_pos_penalty, position_class_encoded
# - country encoded via LabelEncoder (notebook encodes all object cols)
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("OBJECTIVE 2 — Multiclass Classification (position_class)")
print("="*60)

TARGET_MC = 'position_class'
LEAKAGE_MC = ['podium', 'finish_pos_penalty', 'position_class_encoded',
              'positionOrder', 'points', 'laps', 'rank', 'statusId', 'is_top3']

class_map = {0: 'win', 1: 'podium', 2: 'points', 3: 'retirement'}

df_mc = df.copy()
if 'country' in df_mc.columns:
    le_country = LabelEncoder()
    df_mc['country_encoded'] = le_country.fit_transform(df_mc['country'].astype(str))
    df_mc = df_mc.drop(columns=['country'])
else:
    le_country = None

X_mc = df_mc.drop(columns=[TARGET_MC] + [c for c in LEAKAGE_MC if c in df_mc.columns])
y_mc = df_mc[TARGET_MC].astype(int)

numeric_features_mc = X_mc.select_dtypes(include='number').columns.tolist()

preprocessor_mc = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

X_train_mc, X_test_mc, y_train_mc, y_test_mc = train_test_split(
    X_mc, y_mc, test_size=0.2, stratify=y_mc, random_state=RANDOM_STATE
)

# Best model from notebook: XGBoost Grid Search
# (Accuracy 0.68, F1-macro 0.59) — best params from grid:
# n_estimators, max_depth, learning_rate, subsample, colsample_bytree
n_classes_mc = len(y_mc.unique())
pipeline_mc = Pipeline([
    ('preprocessor', preprocessor_mc),
    ('model', XGBClassifier(
        objective='multi:softprob',
        num_class=n_classes_mc,
        eval_metric='mlogloss',
        tree_method='hist',
        n_estimators=500,
        max_depth=8,
        learning_rate=0.1,
        subsample=1.0,
        colsample_bytree=1.0,
        random_state=RANDOM_STATE,
        n_jobs=-1
    ))
])
pipeline_mc.fit(X_train_mc, y_train_mc)

y_pred_mc = pipeline_mc.predict(X_test_mc)
acc_mc = accuracy_score(y_test_mc, y_pred_mc)
f1_mc  = f1_score(y_test_mc, y_pred_mc, average='macro')
print(f"  Accuracy: {acc_mc:.4f} | F1-macro: {f1_mc:.4f}")

with open('models/model_multiclass.pkl', 'wb') as f:
    pickle.dump(pipeline_mc, f)
with open('models/features_multiclass.pkl', 'wb') as f:
    pickle.dump({
        'feature_names': X_mc.columns.tolist(),
        'class_map': class_map,
        'le_country': le_country,
        'metrics': {'accuracy': acc_mc, 'f1_macro': f1_mc}
    }, f)
print("  ✓ Saved models/model_multiclass.pkl")

# ─────────────────────────────────────────────
# OBJECTIVE 3 — Regression (finish_pos_penalty)
# Matches notebook 06_obj3_regression_position.ipynb exactly:
# - All features kept (including qualifying_position, country via OneHotEncoder)
# - Leakage cols: podium, position_class, position_class_encoded
# - Best model: XGBoost with Grid Search params (MAE ~1.72, R² ~0.87)
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("OBJECTIVE 3 — Regression (finish_pos_penalty)")
print("="*60)

TARGET_REG = 'finish_pos_penalty'
LEAKAGE_REG = [
    'podium', 'position_class',
]

df_reg = df.copy()

# Drop only the leakage cols the notebook dropped: podium, position_class
# Keep position_class_encoded, country_encoded, country, qualifying_position (imputed)
X_reg = df_reg.drop(columns=[TARGET_REG] + [c for c in LEAKAGE_REG if c in df_reg.columns])
y_reg = df_reg[TARGET_REG].astype(float)

print(f"  X shape: {X_reg.shape}")

numeric_features_reg = X_reg.select_dtypes(include=['number', 'bool']).columns.tolist()
categorical_features_reg = X_reg.select_dtypes(include=['object', 'category']).columns.tolist()

numeric_transformer_reg = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])
try:
    ohe_reg = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
except TypeError:
    ohe_reg = OneHotEncoder(handle_unknown='ignore', sparse=False)

categorical_transformer_reg = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', ohe_reg)
])

preprocessor_reg = ColumnTransformer([
    ('num', numeric_transformer_reg, numeric_features_reg),
    ('cat', categorical_transformer_reg, categorical_features_reg)
], remainder='drop')

X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(
    X_reg, y_reg, test_size=0.2, random_state=RANDOM_STATE
)

# Best model from notebook: XGBoost with Grid Search best params
# (MAE ~1.72, R² ~0.87)
pipeline_reg = Pipeline([
    ('preprocessor', preprocessor_reg),
    ('model', XGBRegressor(
        objective='reg:squarederror',
        n_estimators=300,
        max_depth=7,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=1.0,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        tree_method='hist'
    ))
])
pipeline_reg.fit(X_train_r, y_train_r)

y_pred_r = pipeline_reg.predict(X_test_r)
mae_r = mean_absolute_error(y_test_r, y_pred_r)
r2_r  = r2_score(y_test_r, y_pred_r)
print(f"  MAE: {mae_r:.4f} | R²: {r2_r:.4f}")

with open('models/model_regression.pkl', 'wb') as f:
    pickle.dump(pipeline_reg, f)
with open('models/features_regression.pkl', 'wb') as f:
    pickle.dump({
        'feature_names': X_reg.columns.tolist(),
        'numeric_features': numeric_features_reg,
        'categorical_features': categorical_features_reg,
        'metrics': {'mae': mae_r, 'r2': r2_r}
    }, f)
print("  ✓ Saved models/model_regression.pkl")

# ─────────────────────────────────────────────
# OBJECTIVE 4 — Clustering
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("OBJECTIVE 4 — Clustering (KMeans + PCA)")
print("="*60)

df_cl = df.copy()
if 'country' in df_cl.columns:
    df_cl = df_cl.drop(columns=['country'])

X_cl = df_cl.select_dtypes(include='number')

imputer_cl = SimpleImputer(strategy='mean')
scaler_cl  = StandardScaler()
pca_cl     = PCA(n_components=2, random_state=RANDOM_STATE)
kmeans_cl  = KMeans(n_clusters=4, random_state=RANDOM_STATE, n_init=10)

X_imputed = imputer_cl.fit_transform(X_cl)
X_scaled  = scaler_cl.fit_transform(X_imputed)
X_pca     = pca_cl.fit_transform(X_scaled)
labels    = kmeans_cl.fit_predict(X_pca)

sil = silhouette_score(X_pca, labels)
print(f"  Silhouette Score: {sil:.4f}")
print(f"  Explained variance (PCA): {pca_cl.explained_variance_ratio_.sum():.4f}")

# Build a sample for the frontend scatter plot
sample_idx = np.random.choice(len(X_pca), size=min(500, len(X_pca)), replace=False)
cluster_data = {
    'pca_coords': X_pca[sample_idx].tolist(),
    'labels': labels[sample_idx].tolist(),
    'cluster_names': ['Elite Drivers', 'Podium Contenders', 'Mid-field', 'Back Markers'],
    'silhouette': float(sil),
    'explained_variance': float(pca_cl.explained_variance_ratio_.sum())
}

with open('models/model_clustering.pkl', 'wb') as f:
    pickle.dump({
        'imputer': imputer_cl,
        'scaler': scaler_cl,
        'pca': pca_cl,
        'kmeans': kmeans_cl,
        'feature_names': X_cl.columns.tolist()
    }, f)
with open('models/cluster_data.pkl', 'wb') as f:
    pickle.dump(cluster_data, f)
print("  ✓ Saved models/model_clustering.pkl + cluster_data.pkl")

# ─────────────────────────────────────────────
# OBJECTIVE 5 — Pre-Race Regression
# Matches notebook 08_obj5_regression_race_prediction.ipynb exactly:
# - Target: positions_gagnees = grid - finish_pos_penalty
# - Features: base pre-race + 3 engineered (rolling avg, interaction)
# - Temporal split (first 80% train, last 20% test)
# - Best model: SVR (MAE ~0.96) — best by MAE
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("OBJECTIVE 5 — Pre-Race Regression (positions_gagnees)")
print("="*60)

df_pr = df.copy()

# Target: positions gained/lost = grid - finish position
df_pr['positions_gagnees'] = df_pr['grid'] - df_pr['finish_pos_penalty']

# Engineered features (rolling on full dataset before split, as notebook does)
df_pr['avg_pos_gagnees_3'] = df_pr['positions_gagnees'].rolling(3, min_periods=1).mean()
df_pr['avg_grid_3'] = df_pr['grid'].rolling(3, min_periods=1).mean()
df_pr['grid_driver_interaction'] = df_pr['grid'] * df_pr['driver_standing_pos']

PRERACE_FEATURES = [
    'grid',
    'driver_standing_pos', 'driver_points_cum', 'driver_wins_cum',
    'constructor_standing_pos', 'constructor_points_cum', 'constructor_wins_cum',
    'country_encoded',
    'avg_pos_gagnees_3', 'avg_grid_3', 'grid_driver_interaction'
]
TARGET_PR = 'positions_gagnees'

available_pr = [c for c in PRERACE_FEATURES if c in df_pr.columns]
X_pr = df_pr[available_pr]
y_pr = df_pr[TARGET_PR].astype(float)

# Temporal split: first 80% train, last 20% test (no shuffle)
split_idx = int(len(df_pr) * 0.8)
X_train_pr = X_pr.iloc[:split_idx]
X_test_pr  = X_pr.iloc[split_idx:]
y_train_pr = y_pr.iloc[:split_idx]
y_test_pr  = y_pr.iloc[split_idx:]

num_cols_pr = X_train_pr.select_dtypes(include=['number', 'bool']).columns.tolist()
cat_cols_pr = X_train_pr.select_dtypes(include=['object', 'category']).columns.tolist()

numeric_transformer_pr = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])
try:
    ohe_pr = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
except TypeError:
    ohe_pr = OneHotEncoder(handle_unknown='ignore', sparse=False)
categorical_transformer_pr = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', ohe_pr)
])
preprocessor_pr = ColumnTransformer([
    ('num', numeric_transformer_pr, num_cols_pr),
    ('cat', categorical_transformer_pr, cat_cols_pr)
], remainder='drop')

# Best model from notebook: XGBoost Fast (best R² = 0.91)
pipeline_pr = Pipeline([
    ('preprocessor', preprocessor_pr),
    ('model', XGBRegressor(
        objective='reg:squarederror',
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        tree_method='hist'
    ))
])
pipeline_pr.fit(X_train_pr, y_train_pr)

y_pred_pr = pipeline_pr.predict(X_test_pr)
mae_pr = mean_absolute_error(y_test_pr, y_pred_pr)
r2_pr  = r2_score(y_test_pr, y_pred_pr)
print(f"  MAE: {mae_pr:.4f} | R²: {r2_pr:.4f}")

with open('models/model_prerace.pkl', 'wb') as f:
    pickle.dump(pipeline_pr, f)
with open('models/features_prerace.pkl', 'wb') as f:
    pickle.dump({
        'feature_names': available_pr,
        'target': TARGET_PR,  # 'positions_gagnees'
        'metrics': {'mae': mae_pr, 'r2': r2_pr}
    }, f)
print("  ✓ Saved models/model_prerace.pkl")

# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("ALL MODELS TRAINED AND SAVED")
print("="*60)
print(f"  Binary Classification  → Accuracy {acc_b:.3f}, AUC {auc_b:.3f}")
print(f"  Multiclass             → Accuracy {acc_mc:.3f}, F1-macro {f1_mc:.3f}")
print(f"  Regression (full)      → MAE {mae_r:.3f}, R² {r2_r:.3f}")
print(f"  Clustering             → Silhouette {sil:.3f}")
print(f"  Pre-Race Regression    → MAE {mae_pr:.3f}, R² {r2_pr:.3f}")
print("\nFiles in models/:")
for f in sorted(os.listdir('models')):
    size = os.path.getsize(f'models/{f}') / 1024
    print(f"  {f:40s} {size:8.1f} KB")

# F1 Race Intelligence (Flask + ML)

A Flask web app that serves **5 Formula 1 prediction/analysis models** with a simple UI (Bootstrap + Chart.js).

## What’s inside

- **Binary classification**: podium prediction (top 3)
- **Multiclass classification**: outcome category prediction (win / podium / points / retirement)
- **Regression**: finish position prediction (1–20) with a rough confidence interval
- **Clustering**: driver performance clustering + PCA visualization
- **Pre-race prediction**: predicts finishing order for a set of drivers

The backend loads **trained models** from the `models/` folder (pickle files) at startup.

## Requirements

- Python 3.8+
- `prepared_data.csv` present in the project root

## Quickstart

### Windows (one command)

```bat
start.bat
```

### Manual

```bash
pip install -r requirements.txt
python app.py
```

Open: http://localhost:5000

## Run tests

In terminal 1:

```bash
python app.py
```

In terminal 2:

```bash
python test_app.py
```

## Project layout (high level)

- `app.py` — Flask server (routes + API endpoints)
- `templates/` — HTML pages (Jinja templates)
- `static/` — JS, images, 3D assets
- `models/` — trained model artifacts (`*.pkl`) + feature metadata
- Notebooks (`*.ipynb`) — training / experimentation

## Notes

- If port 5000 is busy, change the `port=` in `app.py`.
- This repo includes binary assets (model pickles and 3D files). If you later hit GitHub file-size limits, you may need Git LFS.

## Docs

- `QUICKSTART.md` — step-by-step run guide
- `ARCHITECTURE.md` — architecture overview and API list
- `PROJECT_SUMMARY.md` — feature summary
- `README_FRONTEND.md` — frontend details

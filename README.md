# A rigorous statistical benchmark of global neural time-series models for multi-horizon air pollutant forecasting

This repository contains the official implementation and reproducibility scripts for the study benchmarking fifteen forecasting models on atmospheric pollutant data (CAMS reanalysis).

## 🚀 Overview
The project evaluates the predictive performance of Global Neural Architectures (N-HiTS, N-BEATS) against boosting and classical statistical models across multiple horizons (1 to 30 days).

## 📂 Project Structure
- `data/`: Contains scripts to interface with the Copernicus Atmosphere Monitoring Service (CAMS) API.
- `notebooks/01_models.ipynb`: Pipeline for rolling-origin cross-validation, model training (Nixtla/NeuralForecast), and forecasting.
- `notebooks/02_figures.ipynb`: Statistical framework implementation, including:
    - Friedman-Nemenyi tests.
    - Diebold-Mariano tests with HAC variance and HLN correction.
    - Generation of Critical Difference (CD) diagrams and ranking frequency plots.
- `requirements.txt`: Python dependencies required to run the experiments.

## 🛠️ Installation
```bash
git clone [https://github.com/seu-usuario/air-quality-neural-benchmark.git](https://github.com/seu-usuario/Global-Air-Quality-Forecasting-Benckmark.git)
cd Global-Air-Quality-Forecasting-Benckmark
pip install -r requirements.txt
```

## 📊 Data Source
Atmospheric data is retrieved from the CAMS global reanalysis (EAC4). To reproduce the extraction, you will need a CAMS API key.

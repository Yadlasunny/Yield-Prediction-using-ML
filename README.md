# Crop Yield Prediction using PySpark & Machine Learning

A real-world machine learning project to predict crop yields using distributed computing. This repository demonstrates how to build a scalable data pipeline with PySpark, perform EDA and feature engineering, train regression models (scikit-learn), visualize results, and prepare the solution for deployment to help farmers and agricultural analysts make data-driven decisions.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [Data](#data)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Spark + S3 configuration](#spark--s3-configuration)
- [Usage](#usage)
  - [1. Start a Spark session](#1-start-a-spark-session)
  - [2. Load data](#2-load-data)
  - [3. Exploratory Data Analysis (EDA)](#3-exploratory-data-analysis-eda)
  - [4. Feature engineering](#4-feature-engineering)
  - [5. Model training & evaluation](#5-model-training--evaluation)
  - [6. Visualizations & artifacts](#6-visualizations--artifacts)
- [Metrics & Sample Results](#metrics--sample-results)
- [Project Structure](#project-structure)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Project Overview
This project builds a predictive pipeline that uses environmental and economic features (e.g., area, production, rainfall, year, crop type, soil factors) to estimate crop yields. The pipeline is implemented with PySpark for scalable data ingestion and preprocessing, with model training performed using scikit-learn regressors for quick experimentation and interpretability.

## Problem Statement
Agricultural productivity depends on multiple environmental and socioeconomic factors. Accurate crop yield prediction empowers farmers and decision-makers to:
- Optimize crop selection
- Allocate resources (water, fertilizer)
- Forecast production and inform supply-chain decisions

The goal is to predict yield (e.g., tonnes/ha) given features such as cultivated area, rainfall, production history, seasonality, and regional attributes.

## Key Features
- Scalable data ingestion via PySpark (supports S3)
- Exploratory Data Analysis (Seaborn, Matplotlib)
- Feature engineering (missing value handling, scaling, encoding)
- Model training and comparison (Linear Regression, Decision Tree Regressor)
- Evaluation using RMSE and R²
- Visual outputs saved to visuals/ for reporting

## Data
Place raw or cleaned CSV/Parquet files in `data/` (or point Spark to S3). Typical fields:
- year
- state / district
- crop
- area (ha)
- production (tonnes)
- rainfall (mm)
- additional soil / climate features (optional)
Make sure CSVs include headers for auto schema inference.

## Architecture & Tech Stack
- Language: Python 3.8+
- Distributed processing: PySpark
- Local analysis & plotting: pandas, seaborn, matplotlib
- Modeling: scikit-learn (LinearRegression, DecisionTreeRegressor)
- Storage: Local filesystem or Amazon S3 (via Hadoop fs.s3a)
- Notebook: Jupyter / VS Code

## Getting Started

### Prerequisites
- Java 8/11 (required for Spark)
- Python 3.8+
- Apache Spark compatible with your PySpark version
- If using S3: AWS credentials with read permissions for the bucket

### Installation
1. Clone the repository
2. Create and activate a virtual environment
   - python -m venv .venv
   - source .venv/bin/activate  (or `.venv\Scripts\activate` on Windows)
3. Install dependencies
   - pip install -r requirements.txt

A sample requirements.txt might include:
- pyspark
- pandas
- numpy
- scikit-learn
- matplotlib
- seaborn
- boto3
- joblib

### Spark + S3 configuration
To access S3 via s3a, configure Hadoop settings in your Spark session or environment. Example (Python snippet shown in the notebook):

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("CropYieldPrediction") \
    .config("spark.hadoop.fs.s3a.impl","org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.aws.credentials.provider","org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
    .getOrCreate()

hadoop_conf = spark._jsc.hadoopConfiguration()
hadoop_conf.set("fs.s3a.access.key", "<AWS_ACCESS_KEY_ID>")
hadoop_conf.set("fs.s3a.secret.key", "<AWS_SECRET_ACCESS_KEY>")
hadoop_conf.set("fs.s3a.endpoint", "s3.amazonaws.com")
```

Alternatively export environment variables:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_DEFAULT_REGION

Avoid hardcoding credentials in code—use IAM roles or environment variables for production.

## Usage

### 1. Start a Spark session
Open the Jupyter notebook `CropYield.ipynb` or run a Python script that creates a SparkSession as shown above.

### 2. Load data
Example:
```python
df = spark.read.csv("s3a://my-bucket/path/to/crop_data.csv", header=True, inferSchema=True)
# or local
df = spark.read.csv("data/crop_data.csv", header=True, inferSchema=True)
```

Convert to pandas for scikit-learn-based modeling (only for datasets that fit in memory):
```python
pdf = df.toPandas()
```

For very large datasets, consider Spark MLlib or distributed training.

### 3. Exploratory Data Analysis (EDA)
- Inspect distributions: `pdf.describe()`, `sns.histplot()`
- Correlations: `sns.heatmap(pdf.corr(), annot=True)`
- Scatter plots: `sns.scatterplot(x="area", y="yield", hue="crop", data=pdf)`
- Detect outliers and missing values and log decisions in the notebook.

### 4. Feature engineering
- Handle missing values (impute median/mean or drop)
- Encode categorical variables (OneHotEncoder or pd.get_dummies)
- Create derived features (e.g., production/area -> yield)
- Scale numeric features (StandardScaler in sklearn pipeline)

### 5. Model training & evaluation
Example using scikit-learn:
```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

X = pdf[feature_cols]
y = pdf["yield"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

lr = LinearRegression()
lr.fit(X_train_scaled, y_train)
y_pred_lr = lr.predict(X_test_scaled)

dt = DecisionTreeRegressor(random_state=42)
dt.fit(X_train, y_train)
y_pred_dt = dt.predict(X_test)

def rmse(y_true, y_pred): return np.sqrt(mean_squared_error(y_true, y_pred))

print("Linear Regression RMSE:", rmse(y_test, y_pred_lr), "R2:", r2_score(y_test, y_pred_lr))
print("Decision Tree RMSE:", rmse(y_test, y_pred_dt), "R2:", r2_score(y_test, y_pred_dt))
```

Save models:
```python
import joblib
joblib.dump(lr, "models/linear_regression.joblib")
joblib.dump(scaler, "models/scaler.joblib")
```

### 6. Visualizations & artifacts
- Save charts to `visuals/` and exported CSVs/Parquet to `data/cleaned/`.
- Export evaluation summaries to `reports/` or notebook cells.

## Metrics & Sample Results
In the notebook you will find trained models and comparative metrics such as:
- RMSE (Root Mean Square Error)
- R² score (coefficient of determination)

Example outcome (your numbers will vary by dataset and preprocessing):
- Linear Regression — RMSE: 0.85, R²: 0.62
- Decision Tree — RMSE: 0.92, R²: 0.58

Include cross-validation and hyperparameter tuning (GridSearchCV) to improve model generalization.

## Project Structure
CropYieldPrediction/
- CropYield.ipynb         # Jupyter notebook with EDA, modeling and outputs
- data/                   # Raw & cleaned datasets (or S3 mount)
- visuals/                # Saved charts and plots
- models/                 # Trained model artifacts (joblib)
- README.md               # This file
- requirements.txt        # Python dependencies

## Future Improvements
- Integrate real-time weather APIs (temperature, precipitation forecasts)
- Add soil analysis and remote sensing (NDVI) features
- Use Spark MLlib or distributed training for large-scale modeling
- Build a web dashboard for farmers (Streamlit/Flask/FastAPI)
- Add geospatial analysis (GIS mapping) for region-aware predictions
- Automate hyperparameter tuning with MLflow & experiment tracking

## Contributing
1. Fork the repo
2. Create a feature branch
3. Add tests / update notebook
4. Open a PR with a clear description of changes

Please follow best practices: add descriptive commit messages, keep large binary files out of the repo, and document data schema changes.

## License
This project is available under the MIT License. See LICENSE for details.

## Acknowledgements
Inspired by practical agricultural data science efforts and open datasets. Thanks to contributors and maintainers of PySpark, scikit-learn, pandas, and visualization libraries.

## Contact
For questions, improvements, or feedback, open an issue or reach out to the project maintainer.

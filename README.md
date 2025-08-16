# College Basketball Transfer Success Predictor

> A machine learning approach to predicting college basketball player transfer outcomes using play-style clustering and advanced analytics.

## Table of Contents
- [Problem Statement](#problem-statement)
- [Dataset](#dataset)
- [Methodology](#methodology)
- [Key Findings](#key-findings)
- [Model Performance](#model-performance)
- [Installation & Usage](#installation--usage)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Limitations & Future Work](#limitations--future-work)

## Problem Statement

The college basketball transfer portal has revolutionized player mobility, with over 1,600+ Division I players entering annually. However, predicting transfer success remains largely intuition-based. This project develops a data-driven approach to:

- **Predict transfer success** using pre-transfer performance and contextual factors
- **Identify player archetypes** through unsupervised learning on play-style metrics  
- **Quantify key factors** that influence transfer outcomes
- **Provide actionable insights** for coaches, athletic directors, and players

## Dataset

### Data Sources
- **Sports Reference (CBB):** Historical player statistics, advanced metrics
- **Transfer Portal Tracking:** Player movement data, timeline information
- **KenPom:** Team efficiency and strength metrics

### Data Scope
- **Players:** 5,000+ Division I transfers (2019-2024)
- **Features:** 50+ statistical and contextual variables
- **Success Metrics:** Based on change in PER currently, I hopt to change to a more advanced Multi-dimensional success definition incorporating performance, playing time, and team success changes in the future

## Methodology

### 1. Data Collection & Engineering
```python
# Advanced feature engineering example
features = [
    'points_per_100_possessions', 'usage_rate', 'true_shooting_pct',
    'team_quality_change', 'conference_strength_diff', 'role_change_indicator'
]
```

### 2. Play-Style Clustering (Unsupervised Learning)
- **Algorithm:** K-Means clustering on normalized per-possession statistics
- **Features:** Usage rate, shooting efficiency, rebounding rates, assist rates
- **Output:** 5 distinct player archetypes:
  - Defensive and Hustling Bench Forward
  - Role Player 
  - High Usage Scoring Guard
  - All Around Wing
  - Low Impact Guard

### 3. Transfer Success Prediction (Supervised Learning)
- **Target Variable:** Change in Player Efficiency Rating (PER)
- **Models Tested:** Logistic Regression, Random Forest
- **Best Model:** Random Forest with 79.7% accuracy

## Key Findings

### Top Predictive Features
1. **Win Share/40 min** (15% feature importance)
2. **Offense Win Shares** (8% feature importance)  
3. **Play Style/Role** (7% feature importance)
4. **Win Share** (5% feature importance)
5. **Strength of Schedule Change** (4% feature importance)

## Model Performance

| Metric | Score |
|--------|-------|
| **Accuracy** | 79.7% |
| **Precision** | 82% |
| **Recall** | 80% |
| **F1-Score** | 79% |
| **ROC-AUC** | 86.2% |

### Cross-Validation Results
- **5-Fold CV Mean:** 79.1%
- **Stable performance** across different data splits

## Installation & Usage

### Prerequisites
```bash
Python 3.8+
Git
```

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/college-basketball-transfer-predictor.git
cd college-basketball-transfer-predictor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Streamlit App
```bash
streamlit run app.py
```

### Training Models
```bash
# Data collection and preprocessing
python src/data/make_dataset.py

# Feature engineering
python src/features/build_features.py

# Model training
python src/models/train_model.py

# Model evaluation
python src/models/predict_model.py
```

## Project Structure

```
college_basketball_transfer_project/
├── data/
│   ├── raw/                    
│   ├── interim/               
│   └── processed/             
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── visualization/
├── models/                   
├── reports/
│   └── figures/              
├── app.py                   
├── requirements.txt          
└── README.md                 
```

## Technologies Used

- **Python:** Core programming language
- **pandas/numpy:** Data manipulation and analysis
- **scikit-learn:** Machine learning algorithms and evaluation
- **XGBoost:** Gradient boosting framework
- **Streamlit:** Web application framework
- **matplotlib/seaborn:** Data visualization
- **BeautifulSoup/requests:** Web scraping
- **Git/GitHub:** Version control

## Limitations & Future Work

### Current Limitations
- **Sample Size:** Limited to D1 transfers since 2019
- **Success Definition:** Subjective composite scoring
- **Data Availability:** Some advanced metrics not available for all players
- **External Factors:** NIL, coaching changes not fully captured

### Future Enhancements
- **Incorporate NIL data** when publicly available
- **Coaching system compatibility** analysis
- **Real-time prediction updates** during transfer windows
- **Expand to other sports** (football, soccer)
- **Player sentiment analysis** from social media

## Contact

**Patrick King**  
patrickking@ufl.edu
[LinkedIn](www.linkedin.com/in/patrickking0)
[GitHub](https://github.com/rickpatking)

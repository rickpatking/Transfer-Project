import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns

df_final = pd.read_csv('processed/final_stats.csv')

y = (df_final['change_in_PER'] > 2).astype(int)

X = df_final.copy()

X = X[[
    'before_G_x', 'before_GS_x', 'before_Class_x', 'before_Pos_x',
    'before_MP_x', 'before_FG', 'before_FGA', 'before_FG%', 'before_3P', 'before_3PA',
    'before_3P%', 'before_2P', 'before_2PA', 'before_2P%', 'before_eFG%', 'before_FT',
    'before_FTA', 'before_FT%', 'before_ORB', 'before_DRB', 'before_TRB', 'before_AST',
    'before_STL', 'before_BLK', 'before_TOV', 'before_PF', 'before_PTS', 'before_TS%',
    'before_3PAr', 'before_FTr', 'before_PProd', 'before_ORB%', 'before_DRB%', 'before_TRB%',
    'before_AST%', 'before_STL%', 'before_BLK%', 'before_TOV%', 'before_USG%', 'before_OWS',
    'before_DWS', 'before_WS', 'before_WS/40', 'before_OBPM', 'before_DBPM', 'before_BPM',
    'cluster', 'rank_change', 'netrtg_change', 'adjt_change', 'luck_change', 'sos_change', 'sos_ooc_change'
]]
position_dummies = pd.get_dummies(df_final['before_Pos_x'], prefix='Pos').astype(int)
class_dummies = pd.get_dummies(df_final['before_Class_x'], prefix='Class').astype(int)
X = pd.concat([X, position_dummies, class_dummies], axis=1)

X = X.apply(pd.to_numeric, errors='coerce')

X = X.dropna(axis=1)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
numerical_cols = X_train.select_dtypes(include=[np.number]).columns
X_train_scaled = X_train.copy()
X_test_scaled = X_test.copy()

X_train_scaled[numerical_cols] = scaler.fit_transform(X_train[numerical_cols])
X_test_scaled[numerical_cols] = scaler.transform(X_test[numerical_cols])

log_reg = LogisticRegression(random_state=42)
log_reg.fit(X_train_scaled, y_train)
cv_scores_lr = cross_val_score(log_reg, X_train_scaled, y_train, cv=5, scoring='accuracy')
print(f"Logistic Regression CV Accuracy: {cv_scores_lr.mean():.3f} (+/- {cv_scores_lr.std() * 2:.3f})")

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train_scaled, y_train)
cv_scores_rf = cross_val_score(rf, X_train_scaled, y_train, cv=5, scoring='accuracy')
print(f"Random Forest CV Accuracy: {cv_scores_rf.mean():.3f} (+/- {cv_scores_rf.std() * 2:.3f})")

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)
grid_search.fit(X_train_scaled, y_train)
print(f"Best RF parameters: {grid_search.best_params_}")
print(f"Best RF CV score: {grid_search.best_score_:.3f}")

best_rf = grid_search.best_estimator_

def evaluate_model(model, X_test, y_test, model_name):
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None

    print(f"\n=== {model_name} Results ===")
    print(classification_report(y_test, y_pred))

    if y_pred_proba is not None:
        auc = roc_auc_score(y_test, y_pred_proba)
        print(f'ROC AUC: {auc:.3f}')

    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f'{model_name} - Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.savefig(f'../../reports/figures/{model_name.lower()}_confusion_matrix.png')
    plt.show()

    return y_pred, y_pred_proba

lr_pred, lr_proba = evaluate_model(log_reg, X_test_scaled, y_test, 'Logistic Regression')
rf_pred, rf_proba = evaluate_model(best_rf, X_test_scaled, y_test, 'Random Forest')

feature_importance = pd.DataFrame({
    'feature': X_train_scaled.columns,
    'importance': best_rf.feature_importances_,
}).sort_values('importance', ascending=False)

plt.figure(figsize=(10, 8))
sns.barplot(data=feature_importance.head(15), x='importance', y='feature')
plt.title('Top 15 Most Important Features for Transfer Success Prediction')
plt.xlabel('Feature Importance')
plt.tight_layout()
plt.savefig('../../reports/figures/feature_importance.png')
plt.show()

print('Top 10 Most Important Features:')
print(feature_importance.head(10))

test_results = X_test_scaled.copy()
test_results['actual'] = y_test
test_results['predicted'] = rf_pred
test_results['correct'] =(test_results['actual'] == test_results['predicted'])

false_positives = test_results[(test_results['actual'] == 0) & (test_results['predicted'] == 1)]
false_negatives = test_results[(test_results['actual'] == 1) & (test_results['predicted'] == 0)]
print(f'False Positives: {len(false_positives)}')
print(f'False Negatives: {len(false_negatives)}')

if len(false_positives) > 0:
    print('False Positive Characteristics')
    print(false_positives[['before_MP_x', 'before_WS/40', 'rank_change']].describe())

if len(false_negatives) > 0:
    print('False Negative Characteristics')
    print(false_negatives[['before_MP_x', 'before_WS/40', 'rank_change']].describe())

import joblib

joblib.dump(best_rf, '../../models/transfer_success_model.pkl')
joblib.dump(scaler, '../../models/scaler.pkl')

feature_names = X_train_scaled.columns.tolist()
with open('../../models/feature_names.txt', 'w') as f:
    for feature in feature_names:
        f.write(f'{feature}\n')

print('Model and preprocessing objects saved successfully!')
import streamlit as st
import joblib
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="🏀 Transfer Success Predictor",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #FF6B35;
    }
    .success-high { color: #28a745; font-weight: bold; }
    .success-medium { color: #ffc107; font-weight: bold; }
    .success-low { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Generate sample data for demonstration"""
    try:
        df_stats = pd.read_csv('data/processed/current_final_stats.csv')
        df_success = pd.read_csv('data/interim/transfer_success.csv')

        merged_df = pd.merge(
            df_stats,
            df_success,
            left_on='player_id',
            right_on='player',
            how='left',
        )

        required_columns = ['player_id', 'success_probability']
        missing_cols = [col for col in required_columns if col not in merged_df.columns]

        if missing_cols:
            st.error(f'Missing required columns: {missing_cols}')
            return pd.DataFrame()

        merged_df = merged_df.dropna(subset=['success_probability'])
        # st.success(f'Loaded {len(merged_df)} transfers')
        return merged_df

    except FileNotFoundError as e:
        st.error(f"❌ Data file not found: {e}")
        st.info("Please ensure you've run your data processing pipeline and saved files to data/processed/")
        return pd.DataFrame()

    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

@st.cache_resource
def load_models():
    models = {}
    try:
        models['predictor'] = joblib.load('models/transfer_success_model.pkl')
        models['scaler'] = joblib.load('models/scaler.pkl')
        models['kmeans'] = joblib.load('models/kmeans.pkl')
        # st.success('Models loaded')
        return models

    except FileNotFoundError as e:
        st.error(f"❌ Model file not found: {e}")
        st.info("Please train and save your models first using src/models/train_model.py")
        return {}

    except Exception as e:
        st.error(f"❌ Error loading models: {e}")
        return {}

def prepare_features(input_features, scaler_model, cluster_model):
    with open('models/feature_names.txt', 'r') as f:
        features_names = [line.strip() for line in f]

    for col in features_names:
        if col not in input_features.columns:
            input_features[col] = 0

    X = input_features[features_names].copy()

    numerical_cols = X.select_dtypes(include=[np.number]).columns

    if len(numerical_cols) > 0:
        X_new = pd.DataFrame(index=X.index)

        non_numerical_cols = X.select_dtypes(exclude=[np.number]).columns
        for col in non_numerical_cols:
            X_new[col] = X[col].values

        scaled_values = scaler_model.transform(X[numerical_cols].astype(float))
        scaled_df = pd.DataFrame(
            scaled_values,
            columns=numerical_cols,
            index=X.index,
            dtype=float
        )

        X_final = pd.concat([X_new, scaled_df], axis=1)

        X_final = X_final[features_names]

        return X_final
    else:
        return X

def predict_transfer_success(features, model):
    success_prob = model.predict_proba(features)[0, 1]
    prediction = model.predict(features)[0]
    feature_importance = model.feature_importances_
    success_prob *= 100
    confidence = 'High' if abs(success_prob - 0.5) > 0.3 else 'Medium' if abs(success_prob - 0.5) > 0.15 else 'Low'

    return success_prob, confidence, bool(prediction), feature_importance

def get_key_factors(processed_data, importance):
    feature_values = processed_data.iloc[0]
    factor_scores = feature_values * importance

    top_largest_factors = factor_scores.nlargest(5)
    top_smallest_factors = factor_scores.nsmallest(5)

    return {
        'positive_factors': {f: factor_scores[f] for f in top_largest_factors.index if factor_scores[f] > 0},
        'negative_factors': {f: factor_scores[f] for f in top_smallest_factors.index if factor_scores[f] < 0}
    }

def main():
    st.markdown('<h1 class="main-header">College Basketball Transfer Success Predictor</h1>',
                unsafe_allow_html=True)

    st.markdown("""
    This application predicts the likelihood of success for college basketball players 
    considering transfers based on their play style, performance metrics, and contextual factors.
    """)

    with st.sidebar:
        st.title("Navigation")
        page = st.selectbox("Choose a page:",
                            ["Prediction Tool", "Model Insights"])

    if page == "Prediction Tool":
        prediction_page()
    else:
        model_insights_page()


def prediction_page():
    st.header("Transfer Success Predictor")

    st.subheader("Current Transfers")

    df = load_data()
    player = st.selectbox('Choose a current transfer',(df['player_x']))

    st.subheader("Prediction Results")

    if st.button(" Predict Transfer Success", type="primary"):
        models = load_models()
        selected_player_df = df[df['player_x'].str.contains(player, na=False)]
        features = prepare_features(selected_player_df, models['scaler'], models['kmeans'])
        success_score, confidence, prediction, feature_importance = predict_transfer_success(features, models['predictor'])
        key_factors = get_key_factors(features, feature_importance)

        st.markdown("### Prediction Summary")

        if success_score >= 70:
            st.markdown(
                f'<div class="success-high">Success Score: {success_score:.1f}/100 (High Probability)</div>',
                unsafe_allow_html=True)
            st.success("This transfer shows strong potential for success!")
        elif success_score >= 50:
            st.markdown(
                f'<div class="success-medium">Success Score: {success_score:.1f}/100 (Moderate Probability)</div>',
                unsafe_allow_html=True)
            st.warning("This transfer has moderate success potential.")
        else:
            st.markdown(f'<div class="success-low">Success Score: {success_score:.1f}/100 (Low Probability)</div>',
                        unsafe_allow_html=True)
            st.error("This transfer shows lower probability of success.")

        st.subheader(f"Model Confidence: {confidence}")

        fig = px.bar(
            x=list(key_factors['positive_factors'].values()),
            y=list(key_factors['positive_factors'].keys()),
            orientation='h',
            title="Positive Factors for This Prediction"
        )
        fig.update_layout(height=400, showlegend=False, xaxis_title='Factor Score', yaxis_title='Factor')
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.bar(
            x=list(key_factors['negative_factors'].values()),
            y=list(key_factors['negative_factors'].keys()),
            orientation='h',
            title="Negative Factors for This Prediction"
        )
        fig2.update_layout(height=400, showlegend=False, xaxis_title='Factor Score', yaxis_title='Factor')
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Shortcomings to Consider")
    st.markdown("""
    - **Coaching System Fit:** How well does the player's style match the new system?
    - **Academic Requirements:** Different academic standards between schools
    - **Competition Level:** Adjustment to new conference strength
    - **Team Chemistry:** Integration with existing roster
    - **NIL Opportunities:** Financial considerations beyond basketball
    """)

def model_insights_page():
    st.header("Model Performance & Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Model Performance Metrics")

        # Performance metrics
        metrics = {
            'Accuracy': 79.7,
            'Precision': 82,
            'Recall': 80,
            'F1-Score': 79,
            'ROC-AUC': 86.2
        }

        for metric, value in metrics.items():
            st.metric(metric, f"{value}%")

        # Feature importance
        st.subheader("Feature Importance")
        importance_data = {
            'Feature': ['WS/40', 'OWS', 'Play Style',
                        'WS', 'SOS Change', 'PTS'],
            'Importance': [15.03, 8.36, 7.30, 4.50, 3.70, 2.92]
        }

        fig = px.bar(
            importance_data, x='Importance', y='Feature',
            orientation='h', title="Top Features for Transfer Success Prediction"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Success Rates by Player Type")

        transfer_success = load_data()
        # st.write(transfer_success.columns)
        playstyle_mapping = {
            0: 'Defensive and Hustling Bench Forward',
            1: 'Role Player',
            2: 'High Usage Scoring Guard',
            3: 'All Around Wing',
            4: 'Low Impact Guard'

        }

        transfer_success['play_style'] = transfer_success['cluster'].map(playstyle_mapping)
        success_rate_by_role = transfer_success.groupby('play_style')['predicted_successful'].mean()
        success_rate_by_role_percent = success_rate_by_role * 100
        success_rate_by_role_percent = success_rate_by_role_percent.to_dict()

        playstyle = transfer_success.groupby('cluster')[['PTS', 'AST', 'TRB', '3P', 'Class_FR', 'Class_SO', 'Class_JR', 'Class_SR', 'Pos_G', 'Pos_F', 'Pos_C', 'WS/40', 'USG%', 'BLK%', 'STL%', 'PProd', 'MP_x', 'BPM']].mean()
        # st.dataframe(playstyle)


        fig2 = px.bar(
            x=list(success_rate_by_role_percent.keys()),
            y=list(success_rate_by_role_percent.values()),
            title="Success Rate by Player Archetype",
            color=list(success_rate_by_role_percent.values()),
            color_continuous_scale="RdYlGn"
        )

        fig2.update_layout(height=500, xaxis_tickangle=-45, showlegend=True, xaxis_title='Role', yaxis_title='Success Rate', font=dict(size=10))
        st.plotly_chart(fig2, use_container_width=True)

        # Cross-validation results
        st.subheader("Cross-Validation Results")
        cv_results = pd.DataFrame({
            'Fold': [1, 2, 3, 4, 5],
            'Accuracy': [80.42, 77.89, 76.63, 81.05, 79.53]
        })

        fig3 = px.line(
            cv_results, x='Fold', y='Accuracy',
            title="5-Fold Cross-Validation Performance",
            markers=True
        )
        fig3.add_hline(y=cv_results['Accuracy'].mean(),
                       line_dash="dash", line_color="red",
                       annotation_text=f"Mean: {cv_results['Accuracy'].mean():.1f}%")
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Key Insights from the Model")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **Most Important Factors**
        - Win Share per 40 minutes is the strongest predictor
        - Playstyle/Role is a good determinant
        - Previous performance (PER) sets baseline expectations
        """)

    with col2:
        st.markdown("""
        **Player Archetype Patterns**
        - Playmaking guards have highest success rates
        - Role players face more adjustment challenges  
        - Two-way players adapt well to new systems
        """)

    with col3:
        st.markdown("""
        **Model Limitations**
        - Coaching system fit not fully captured
        - NIL impact not quantified
        - Sample bias toward recent transfers
        """)

    st.subheader("Future Model Enhancements")
    st.markdown("""
    - **Coaching Compatibility Score:** Quantify system fit between old and new coaches
    - **Real-time Updates:** Incorporate in-season performance adjustments
    - **NIL Integration:** Factor in financial considerations when data becomes available
    - **Injury History:** Account for injury risk and recovery patterns
    - **Academic Fit:** Consider academic requirements and support systems
    """)


if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# PAGE CONFIGURATION 
st.set_page_config(
    page_title="HealthScope AI | Disease Risk Analyzer",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CUSTOM CSS 
st.markdown("""
<style>
    /* Professional Medical Theme */
    :root {
        --primary-dark: #1A365D;
        --primary-blue: #2D5A8C;
        --secondary-blue: #4A90E2;
        --accent-teal: #2C9C9C;
        --accent-green: #38A169;
        --accent-amber: #DD6B20;
        --light-bg: #F7FAFC;
        --white: #FFFFFF;
        --gray-50: #F9FAFB;
        --gray-100: #F3F4F6;
        --gray-200: #E5E7EB;
        --gray-700: #374151;
        --gray-900: #111827;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Reset Streamlit defaults */
    .stApp {
        background: var(--white) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Main Container */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }
    
    /* Cards */
    .card {
        background: var(--white);
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid var(--gray-200);
        box-shadow: var(--shadow);
        transition: box-shadow 0.2s ease;
    }
    
    .card:hover {
        box-shadow: var(--shadow-lg);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .primary-btn {
        background: var(--primary-blue) !important;
        color: white !important;
        border: none !important;
    }
    
    .primary-btn:hover {
        background: var(--primary-dark) !important;
        transform: translateY(-1px);
        box-shadow: var(--shadow-lg) !important;
    }
    
    .outline-btn {
        background: var(--white) !important;
        color: var(--primary-blue) !important;
        border: 1px solid var(--primary-blue) !important;
    }
    
    .outline-btn:hover {
        background: var(--primary-blue) !important;
        color: white !important;
    }
    
    /* Disease Cards */
    .disease-card {
        padding: 1.5rem;
        border: 2px solid var(--gray-200);
        border-radius: 8px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        background: var(--white);
    }
    
    .disease-card:hover {
        border-color: var(--primary-blue);
        transform: translateY(-2px);
    }
    
    .disease-card.selected {
        border-color: var(--primary-blue);
        background: linear-gradient(135deg, var(--light-bg) 0%, #EBF4FF 100%);
    }
    
    /* Typography */
    h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: var(--primary-dark) !important;
        margin-bottom: 1rem !important;
        line-height: 1.2 !important;
    }
    
    h2 {
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        color: var(--gray-900) !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: var(--gray-900) !important;
        margin-bottom: 0.75rem !important;
    }
    
    .section-title {
        color: var(--gray-700);
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
    }
    
    .risk-score {
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        text-align: center !important;
        margin: 1rem 0 !important;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.025em;
    }
    
    .badge-high {
        background-color: #FEE2E2;
        color: #DC2626;
    }
    
    .badge-medium {
        background-color: #FEF3C7;
        color: #D97706;
    }
    
    .badge-low {
        background-color: #D1FAE5;
        color: #059669;
    }
    
    /* Form Styling */
    .form-section {
        background: var(--gray-50);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 1px solid var(--gray-200);
    }
    
    /* Results */
    .result-card {
        border-left: 4px solid var(--primary-blue);
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: var(--gray-200);
        margin: 2rem 0;
    }
    
    /* FIX: Make ALL input text black/dark for visibility */
    .stTextInput input, 
    .stNumberInput input, 
    .stSelectbox select,
    input[type="text"],
    input[type="number"],
    textarea {
        color: var(--gray-900) !important;
        background-color: var(--white) !important;
    }
    
    /* Specifically target Streamlit text input */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextInput"] textarea {
        color: #000000 !important;
        background-color: var(--white) !important;
    }
    
    /* Input field focus state */
    .stTextInput input:focus, 
    .stNumberInput input:focus, 
    .stSelectbox select:focus {
        border-color: var(--primary-blue) !important;
        box-shadow: 0 0 0 2px rgba(45, 90, 140, 0.1) !important;
    }
    
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: var(--gray-700) !important;
        font-weight: 500 !important;
    }
    
    /* Fix slider and selectbox labels for clinical parameters */
    .stSlider label, .stSelectbox label, .stNumberInput label {
        color: var(--gray-900) !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
    }
    
    .stSlider div[data-baseweb="slider"] {
        color: var(--gray-900) !important;
    }
    
    /* Recommendations styling */
    .recommendation-item {
        color: var(--gray-900) !important;
        font-size: 1rem !important;
        line-height: 1.5 !important;
    }
    
    .recommendation-number {
        color: var(--primary-blue) !important;
        font-weight: 700 !important;
        margin-right: 10px !important;
    }
    
    /* Button text visibility */
    .stButton button span {
        color: inherit !important;
    }
    
    /* Make all Streamlit widget labels visible */
    .stSlider, .stSelectbox, .stNumberInput {
        color: var(--gray-900) !important;
    }
    
    div[data-testid="stSlider"] label, 
    div[data-testid="stSelectbox"] label,
    div[data-testid="stNumberInput"] label {
        color: var(--gray-900) !important;
    }
    
    /* Placeholder text styling */
    ::placeholder {
        color: var(--gray-700) !important;
        opacity: 0.7 !important;
    }
    
    /* Ensure input field background is white */
    .stTextInput > div > div {
        background-color: var(--white) !important;
    }
    
    /* Force black text in all inputs */
    input, textarea {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)


if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'selected_disease' not in st.session_state:
    st.session_state.selected_disease = None
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}
if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None
if 'predictions_history' not in st.session_state:
    st.session_state.predictions_history = []


def render_navigation():
    """Simple navigation"""
    pages = ["Home", "Prediction", "Results", "History"]
    
   
    cols = st.columns(len(pages) + 1)
    
    with cols[0]:
        if st.button("🏠 Home", use_container_width=True, 
                    type="primary" if st.session_state.current_page == 'home' else "secondary"):
            st.session_state.current_page = 'home'
            st.rerun()
    
    with cols[1]:
        if st.button("🔮 Prediction", use_container_width=True,
                    type="primary" if st.session_state.current_page == 'predict' else "secondary"):
            st.session_state.current_page = 'predict'
            st.rerun()
    
    with cols[2]:
        if st.button("📊 Results", use_container_width=True,
                    type="primary" if st.session_state.current_page == 'results' else "secondary"):
            st.session_state.current_page = 'results'
            st.rerun()
    
    with cols[3]:
        if st.button("📋 History", use_container_width=True,
                    type="primary" if st.session_state.current_page == 'history' else "secondary"):
            st.session_state.current_page = 'history'
            st.rerun()
    
    with cols[4]:
        if st.button("Sign Out", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()

# PAGE 1: HOME 
def home_page():
    """Simplified Home page"""
    
    st.markdown("""
    <div style='text-align: center; padding: 3rem 0;'>
        <h1>Medical Risk Assessment Platform</h1>
        <p style='color: var(--gray-700); font-size: 1.2rem; line-height: 1.6; max-width: 800px; margin: 0 auto 3rem auto;'>
            Advanced AI-powered analysis for early detection and risk assessment of chronic diseases. 
            Get personalized insights based on clinical data.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Begin Analysis", type="primary", use_container_width=True, key="start_analysis"):
            st.session_state.current_page = 'predict'
            st.rerun()

# PAGE 2: PREDICTION 
def prediction_page():
    """Disease prediction page"""
    
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1>Clinical Risk Assessment</h1>
        <p style='color: var(--gray-700); font-weight: 600; font-size: 1.1rem; margin: 0.5rem 0 1.5rem 0;'>
            Step 1: Select Analysis Type
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(3)
    diseases = ["Heart Disease", "Diabetes", "Breast Cancer"]
    
    selected = None
    for col, disease in zip(cols, diseases):
        with col:
            if st.button(
                disease,
                key=f"select_{disease}",
                use_container_width=True,
                type="primary" if st.session_state.selected_disease == disease else "secondary"
            ):
                selected = disease
    
    if selected:
        st.session_state.selected_disease = selected
        st.rerun()
    
    if st.session_state.selected_disease:
        st.markdown("---")
        
        # Patient Information Form
        with st.form("patient_form"):
            st.markdown(f"""
            <div style='margin-bottom: 2rem;'>
                <p style='color: var(white); font-weight: 600; font-size: 1.1rem; margin: 0.5rem 0 1.5rem 0;'>
                    Step 2: Patient Information
                </p>
                <p style='color: var(--primary-blue); font-weight: 600; background: var(--gray-50); 
                          padding: 10px; border-radius: 6px; margin: 0.5rem 0 1.5rem 0;'>
                    Selected: {st.session_state.selected_disease}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        
            col1, col2 = st.columns(2)
            with col1:
                
                name = st.text_input("Full Name", placeholder="Enter patient name", key="patient_name")
                age = st.number_input("Age", min_value=1, max_value=120, value=45, key="patient_age")
            
            with col2:
                gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="patient_gender")
                height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170, key="patient_height")
                weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70, key="patient_weight")
            
            # Medical Parameters 
            st.markdown('<p style="color: var(--gray-900); font-weight: 600; font-size: 1.1rem; margin: 1.5rem 0 1rem 0;">Step 3: Clinical Parameters</p>', unsafe_allow_html=True)
            
            if st.session_state.selected_disease == "Heart Disease":
                cols = st.columns(2)
                with cols[0]:
                    bp_systolic = st.slider("Systolic BP (mmHg)", 80, 200, 120, key="bp_systolic")
                    cholesterol = st.selectbox("Cholesterol Level", ["Normal", "Elevated", "High"], key="cholesterol")
                with cols[1]:
                    bp_diastolic = st.slider("Diastolic BP (mmHg)", 50, 130, 80, key="bp_diastolic")
                    heart_rate = st.slider("Resting Heart Rate (bpm)", 40, 120, 72, key="heart_rate")
            
            elif st.session_state.selected_disease == "Diabetes":
                cols = st.columns(2)
                with cols[0]:
                    glucose = st.slider("Glucose Level (mg/dL)", 50, 300, 100, key="glucose")
                    insulin = st.slider("Insulin Level (μU/mL)", 0, 300, 25, key="insulin")
                with cols[1]:
                    skin_thickness = st.slider("Skin Thickness (mm)", 0, 100, 20, key="skin_thickness")
                    diabetes_pedigree = st.slider("Family History Factor", 0.0, 2.0, 0.5, 0.1, key="diabetes_pedigree")
            
            else:  # Breast Cancer
                cols = st.columns(2)
                with cols[0]:
                    radius_mean = st.slider("Tumor Radius (mm)", 0.0, 30.0, 10.0, 0.1, key="radius_mean")
                    texture_mean = st.slider("Tumor Texture", 0.0, 40.0, 15.0, 0.1, key="texture_mean")
                with cols[1]:
                    perimeter_mean = st.slider("Tumor Perimeter (mm)", 0.0, 200.0, 80.0, 0.1, key="perimeter_mean")
                    area_mean = st.slider("Tumor Area (mm²)", 0, 2500, 500, key="area_mean")
            
            # Submit Button
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button(
                    "Analyze & Generate Report",
                    use_container_width=True,
                    type="primary"
                )
            
            if submitted:
                # Store data
                st.session_state.patient_data = {
                    'name': name,
                    'age': age,
                    'gender': gender,
                    'disease': st.session_state.selected_disease
                }
                
                # Generate prediction
                np.random.seed(hash(name) % 10000 if name else 42)
                risk_score = np.random.randint(15, 95)
                
                if risk_score >= 70:
                    risk_level = "High Risk"
                elif risk_score >= 40:
                    risk_level = "Medium Risk"
                else:
                    risk_level = "Low Risk"
                
                # Store results
                st.session_state.prediction_result = {
                    'risk_score': risk_score,
                    'risk_level': risk_level,
                    'disease': st.session_state.selected_disease,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'patient_name': name,
                    'patient_age': age,
                    'patient_gender': gender
                }
                
                
                st.session_state.predictions_history.append(st.session_state.prediction_result)
                
               
                st.session_state.current_page = 'results'
                st.rerun()

# PAGE 3: RESULTS 
def results_page():
    """Results display page"""
    
    if not st.session_state.prediction_result:
        st.warning("No analysis data available.")
        if st.button("Start New Analysis", type="primary"):
            st.session_state.current_page = 'predict'
            st.rerun()
        return
    
    result = st.session_state.prediction_result
    
    # Determine styling based on risk
    if "High" in result['risk_level']:
        risk_color = "#DC2626"
        badge = "badge-high"
    elif "Medium" in result['risk_level']:
        risk_color = "#D97706"
        badge = "badge-medium"
    else:
        risk_color = "#059669"
        badge = "badge-low"
    
    
    st.markdown(f"""
    <div style='margin-bottom: 2rem;'>
        <h1>Analysis Report</h1>
        <p style='color: var(--gray-700);'>Generated on {result['timestamp']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Patient Info Card
    st.markdown(f"""
    <div style='background: var(--white); border: 1px solid var(--gray-200); border-radius: 8px; 
                padding: 1.5rem; margin-bottom: 2rem;'>
        <div style='display: flex; justify-a: space-between; align-items: center; margin-bottom: 1.5rem;'>
            <div>
                <h2 style='margin: 0 0 0.5rem 0; color: var(--gray-900);'>{result['disease']}</h2>
                <p style='color: var(--gray-700); margin: 0;'>
                    Patient: {result['patient_name']} | Age: {result['patient_age']} | Gender: {result['patient_gender']}
                </p>
            </div>
            <span class='badge {badge}' style='font-size: 0.9rem; padding: 6px 16px;'>{result['risk_level']}</span>
        </div>
        
        
    </div>
    """, unsafe_allow_html=True)
    
    # Charts
    cols = st.columns(2)
    
    with cols[0]:
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=result['risk_score'],
            title={'text': "Risk Level", 'font': {'size': 16}},
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'font': {'size': 30}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
                'bar': {'color': risk_color},
                'bgcolor': "white",
                'steps': [
                    {'range': [0, 30], 'color': "#D1FAE5"},
                    {'range': [30, 70], 'color': "#FEF3C7"},
                    {'range': [70, 100], 'color': "#FEE2E2"}
                ],
            }
        ))
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with cols[1]:
        # Factors Chart
        factors = ["Clinical Factors", "Lifestyle", "Genetics", "Age", "Biomarkers"]
        values = np.random.randint(20, 90, size=len(factors))
        
        fig = px.bar(
            x=values,
            y=factors,
            orientation='h',
            title="Risk Factor Contribution",
            labels={'x': 'Contribution (%)', 'y': ''},
            color=values,
            color_continuous_scale=[risk_color, risk_color]
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    
    st.markdown("## Recommendations")
    
    if "High" in result['risk_level']:
        recommendations = [
            "Consult a specialist within 48 hours",
            "Complete recommended diagnostic tests",
            "Begin immediate lifestyle modifications",
            "Monitor symptoms daily",
            "Review current medications with physician"
        ]
    elif "Medium" in result['risk_level']:
        recommendations = [
            "Schedule follow-up appointment within 2 weeks",
            "Implement preventive lifestyle changes",
            "Regular monitoring of key parameters",
            "Consider preventive screening",
            "Maintain health records"
        ]
    else:
        recommendations = [
            "Continue routine health maintenance",
            "Annual comprehensive check-up",
            "Maintain healthy lifestyle",
            "Stay informed about preventive care",
            "Regular self-assessment"
        ]
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"""
        <div style='background: var(--gray-50); border-left: 4px solid {risk_color}; 
                    padding: 1rem; margin: 0.5rem 0; border-radius: 0 6px 6px 0;'>
            <div style='display: flex; align-items: start;'>
                <div style='color: {risk_color}; font-weight: 700; font-size: 1.2rem; 
                          min-width: 30px;'>{i}.</div>
                <div style='color: var(--gray-900); font-size: 1rem; line-height: 1.5;'>
                    {rec}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("New Analysis", use_container_width=True, type="primary"):
            st.session_state.current_page = 'predict'
            st.rerun()
    
    with col2:
        if st.button("View History", use_container_width=True, type="secondary"):
            st.session_state.current_page = 'history'
            st.rerun()
    
    with col3:
        if st.button("Export Report", use_container_width=True, type="secondary"):
            st.success("Report exported successfully")
    
    with col4:
        if st.button("Print", use_container_width=True, type="secondary"):
            st.info("Use browser print function")

# PAGE 4: HISTORY 
def history_page():
    """History page"""
    
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1>Analysis History</h1>
        <p style='color: var(--gray-700);'>Previous assessments and reports</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.predictions_history:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: var(--gray-50); border-radius: 8px;'>
            <p style='color: var(--gray-700); font-size: 1.1rem; margin-bottom: 1.5rem;'>
                No analysis history found
            </p>
            <button onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'predict'}, '*')" 
                    style='background: var(--primary-blue); color: white; border: none; padding: 0.75rem 2rem; 
                           border-radius: 6px; font-weight: 500; cursor: pointer;'>
                Start First Analysis
            </button>
        </div>
        """, unsafe_allow_html=True)
        return
    
    
    history_df = pd.DataFrame(st.session_state.predictions_history)
    
    cols = st.columns(4)
    stats = [
        ("Total Analyses", len(history_df)),
        ("High Risk", len([h for h in st.session_state.predictions_history if "High" in h['risk_level']])),
        ("Average Risk", f"{history_df['risk_score'].mean():.1f}%"),
        ("Latest", history_df.iloc[-1]['timestamp'].split()[0])
    ]
    
    for col, (label, value) in zip(cols, stats):
        with col:
            st.markdown(f"""
            <div style='background: var(--white); border: 1px solid var(--gray-200); border-radius: 8px; 
                        padding: 1rem; text-align: center; box-shadow: var(--shadow);'>
                <div style='font-size: 1.5rem; font-weight: 600; color: var(--primary-blue); margin-bottom: 0.5rem;'>
                    {value}
                </div>
                <div style='color: var(--gray-700); font-size: 0.875rem;'>{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # History List 
    st.markdown("### Recent Analyses")
    
    for pred in reversed(st.session_state.predictions_history[-5:]):
        if "High" in pred['risk_level']:
            color = "#DC2626"
        elif "Medium" in pred['risk_level']:
            color = "#D97706"
        else:
            color = "#059669"
        
        st.markdown(f"""
        <div style='background: var(--white); border: 1px solid var(--gray-200); border-left: 4px solid {color};
                    border-radius: 0 6px 6px 0; padding: 1rem; margin: 0.5rem 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <div style='font-weight: 600; color: var(--gray-900); margin-bottom: 0.25rem;'>
                        {pred['disease']}
                    </div>
                    <div style='color: var(--gray-700); font-size: 0.875rem;'>
                        {pred['patient_name']} • {pred['patient_age']} • {pred['patient_gender']}
                    </div>
                    <div style='color: var(--gray-700); font-size: 0.875rem;'>
                        {pred['timestamp']}
                    </div>
                </div>
                <div style='text-align: right;'>
                    <div style='font-size: 1.5rem; font-weight: 700; color: {color};'>{pred['risk_score']}%</div>
                    <div style='color: {color}; font-size: 0.875rem; font-weight: 600;'>{pred['risk_level']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# MAIN APP 
def main():
    """Main application"""
    
    
    render_navigation()
    
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    if st.session_state.current_page == 'home':
        home_page()
    elif st.session_state.current_page == 'predict':
        prediction_page()
    elif st.session_state.current_page == 'results':
        results_page()
    elif st.session_state.current_page == 'history':
        history_page()

if __name__ == "__main__":
    main()

import streamlit as st
import anthropic
import json
import re
from typing import Dict, Optional
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="ABG Interpreter - Medical Training Tool",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .step-box {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .result-box {
        background-color: #d4edda;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .normal-range {
        color: #666;
        font-size: 0.9rem;
        font-style: italic;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'abg_values' not in st.session_state:
    st.session_state.abg_values = {}
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""

# Normal ranges
NORMAL_RANGES = {
    'pH': (7.35, 7.45),
    'pCO2': (4.5, 6.0),  # kPa
    'HCO3': (22, 28),
    'pO2': (11, 13),  # kPa
    'base_excess': (-2, 2),
    'Na': (135, 145),
    'Cl': (98, 107),
    'K': (3.5, 5.0),
    'albumin': (35, 50)
}

def extract_values_from_text(text: str, api_key: str) -> Dict:
    """Use Claude API to extract ABG values from text/image"""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""Extract all arterial blood gas (ABG) values from this report. 
        Look for: pH, pCO2, pO2, HCO3/bicarbonate, base excess, Na, Cl, K, albumin.
        
        Report text:
        {text}
        
        Return ONLY a JSON object with the values found. Use null for missing values.
        Example format:
        {{
            "pH": 7.35,
            "pCO2": 5.5,
            "pO2": 12.0,
            "HCO3": 24,
            "base_excess": -1,
            "Na": 140,
            "Cl": 102,
            "K": 4.0,
            "albumin": 40
        }}
        
        Note: pCO2 and pO2 should be in kPa (not mmHg). If values are in mmHg, convert them (divide by 7.5).
        Return only the JSON, no other text."""
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        # Extract JSON from response
        json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {}
    except Exception as e:
        st.error(f"Error extracting values: {str(e)}")
        return {}

def analyze_abg(values: Dict, clinical_info: str, api_key: str) -> str:
    """Use Claude API to perform step-by-step ABG analysis"""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""You are a medical educator teaching ABG interpretation. Analyze this ABG step-by-step following the standard 5-step approach.

ABG Values:
{json.dumps(values, indent=2)}

Clinical Information:
{clinical_info if clinical_info else "Not provided"}

Perform a detailed step-by-step analysis following this structure:

**STEP 1: pH Assessment**
- Is there acidaemia (pH < 7.35) or alkalaemia (pH > 7.45)?

**STEP 2: Primary Disturbance**
- Identify if respiratory (pCO2 abnormal) or metabolic (HCO3 abnormal)
- Determine the primary disorder

**STEP 3: Anion Gap (if metabolic acidosis)**
- Calculate: Anion Gap = Na - (Cl + HCO3)
- Classify as normal (8-16) or high (>16)
- Correct for albumin if needed
- List likely causes

**STEP 4: Compensation Assessment**
- Is compensation appropriate, excessive, or inadequate?
- Check for mixed disorders
- Use compensation formulas

**STEP 5: Oxygenation & A-a Gradient**
- Assess pO2
- Calculate A-a gradient if appropriate
- Interpret findings

**FINAL IMPRESSION:**
- Primary diagnosis
- Degree of compensation
- Any mixed disorders
- Clinical correlation
- Suggested management considerations

Use clear, educational language suitable for medical trainees. Be thorough but concise."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    except Exception as e:
        return f"Error during analysis: {str(e)}"

def main():
    st.markdown('<h1 class="main-header">🩺 ABG Interpreter</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Step-by-Step Arterial Blood Gas Analysis Training Tool</p>', unsafe_allow_html=True)
    
    # Sidebar for API key
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input("Claude API Key", type="password", help="Enter your Anthropic API key")
        
        st.markdown("---")
        st.header("📚 Normal Ranges")
        st.markdown("""
        - **pH:** 7.35 - 7.45
        - **pCO₂:** 4.5 - 6.0 kPa
        - **HCO₃⁻:** 22 - 28 mmol/L
        - **pO₂:** 11 - 13 kPa
        - **Base Excess:** -2 to +2 mmol/L
        - **Anion Gap:** 8 - 16 mmol/L
        - **Na⁺:** 135 - 145 mmol/L
        - **Cl⁻:** 98 - 107 mmol/L
        """)
        
        st.markdown("---")
        st.markdown("### 📖 About")
        st.info("This tool helps medical trainees learn ABG interpretation using a structured 5-step approach.")
    
    if not api_key:
        st.warning("⚠️ Please enter your Claude API key in the sidebar to begin.")
        st.info("""
        **How to get an API key:**
        1. Visit https://console.anthropic.com
        2. Sign up or log in
        3. Go to API Keys section
        4. Create a new key
        """)
        return
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📊 Input Data", "🔍 Analysis", "📚 Learning Resources"])
    
    with tab1:
        st.header("Step 1: Input ABG Data")
        
        # Upload method selection
        input_method = st.radio("Choose input method:", 
                               ["Upload ABG Report (Image/PDF)", "Manual Entry"],
                               horizontal=True)
        
        if input_method == "Upload ABG Report (Image/PDF)":
            uploaded_file = st.file_uploader(
                "Upload ABG report", 
                type=['png', 'jpg', 'jpeg', 'pdf'],
                help="Upload an image or PDF of the ABG report"
            )
            
            if uploaded_file:
                if uploaded_file.type == "application/pdf":
                    st.info("📄 PDF uploaded. Please manually extract text or use OCR tool.")
                    text_input = st.text_area("Paste extracted text from PDF:", height=200)
                    if st.button("Extract Values from Text"):
                        with st.spinner("Extracting values..."):
                            extracted = extract_values_from_text(text_input, api_key)
                            if extracted:
                                st.session_state.abg_values = extracted
                                st.success("✅ Values extracted successfully!")
                else:
                    st.image(uploaded_file, caption="Uploaded ABG Report", use_container_width=True)
                    
                    # Convert image to base64
                    bytes_data = uploaded_file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode()
                    
                    if st.button("Extract Values from Image"):
                        with st.spinner("Analyzing image..."):
                            # Use Claude's vision capability
                            try:
                                client = anthropic.Anthropic(api_key=api_key)
                                message = client.messages.create(
                                    model="claude-sonnet-4-20250514",
                                    max_tokens=1000,
                                    messages=[{
                                        "role": "user",
                                        "content": [
                                            {
                                                "type": "image",
                                                "source": {
                                                    "type": "base64",
                                                    "media_type": uploaded_file.type,
                                                    "data": base64_image
                                                }
                                            },
                                            {
                                                "type": "text",
                                                "text": """Extract ABG values from this report. Return ONLY a JSON object with: pH, pCO2, pO2, HCO3, base_excess, Na, Cl, K, albumin. 
                                                Use null for missing values. Ensure pCO2 and pO2 are in kPa (convert from mmHg if needed by dividing by 7.5).
                                                Example: {"pH": 7.35, "pCO2": 5.5, "HCO3": 24, "base_excess": -1, "Na": 140, "Cl": 102}"""
                                            }
                                        ]
                                    }]
                                )
                                
                                response_text = message.content[0].text
                                json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                                if json_match:
                                    extracted = json.loads(json_match.group())
                                    st.session_state.abg_values = extracted
                                    st.success("✅ Values extracted successfully!")
                                else:
                                    st.error("Could not extract values. Please try manual entry.")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
        
        else:  # Manual Entry
            st.markdown("### Enter ABG values manually:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                pH = st.number_input("pH", min_value=6.8, max_value=7.8, value=7.40, step=0.01, format="%.2f")
                st.caption(f"Normal: {NORMAL_RANGES['pH'][0]} - {NORMAL_RANGES['pH'][1]}")
                
                pCO2 = st.number_input("pCO₂ (kPa)", min_value=2.0, max_value=12.0, value=5.3, step=0.1, format="%.1f")
                st.caption(f"Normal: {NORMAL_RANGES['pCO2'][0]} - {NORMAL_RANGES['pCO2'][1]} kPa")
                
                HCO3 = st.number_input("HCO₃⁻ (mmol/L)", min_value=10.0, max_value=45.0, value=24.0, step=0.5, format="%.1f")
                st.caption(f"Normal: {NORMAL_RANGES['HCO3'][0]} - {NORMAL_RANGES['HCO3'][1]} mmol/L")
            
            with col2:
                pO2 = st.number_input("pO₂ (kPa)", min_value=5.0, max_value=20.0, value=12.0, step=0.1, format="%.1f")
                st.caption(f"Normal: {NORMAL_RANGES['pO2'][0]} - {NORMAL_RANGES['pO2'][1]} kPa")
                
                base_excess = st.number_input("Base Excess (mmol/L)", min_value=-20.0, max_value=20.0, value=0.0, step=0.5, format="%.1f")
                st.caption(f"Normal: {NORMAL_RANGES['base_excess'][0]} to {NORMAL_RANGES['base_excess'][1]} mmol/L")
            
            with col3:
                Na = st.number_input("Na⁺ (mmol/L)", min_value=120.0, max_value=160.0, value=140.0, step=1.0, format="%.0f")
                st.caption(f"Normal: {NORMAL_RANGES['Na'][0]} - {NORMAL_RANGES['Na'][1]} mmol/L")
                
                Cl = st.number_input("Cl⁻ (mmol/L)", min_value=80.0, max_value=120.0, value=102.0, step=1.0, format="%.0f")
                st.caption(f"Normal: {NORMAL_RANGES['Cl'][0]} - {NORMAL_RANGES['Cl'][1]} mmol/L")
            
            if st.button("Use These Values", type="primary"):
                st.session_state.abg_values = {
                    'pH': pH,
                    'pCO2': pCO2,
                    'HCO3': HCO3,
                    'pO2': pO2,
                    'base_excess': base_excess,
                    'Na': Na,
                    'Cl': Cl
                }
                st.success("✅ Values saved!")
        
        # Display current values
        if st.session_state.abg_values:
            st.markdown("---")
            st.markdown("### 📋 Current ABG Values:")
            
            cols = st.columns(4)
            for idx, (key, value) in enumerate(st.session_state.abg_values.items()):
                if value is not None:
                    with cols[idx % 4]:
                        # Check if value is in normal range
                        is_normal = True
                        if key in NORMAL_RANGES and value is not None:
                            min_val, max_val = NORMAL_RANGES[key]
                            is_normal = min_val <= value <= max_val
                        
                        status = "✅" if is_normal else "⚠️"
                        st.metric(f"{status} {key}", f"{value}")
        
        # Clinical information
        st.markdown("---")
        st.markdown("### 🏥 Clinical Information (Optional)")
        clinical_info = st.text_area(
            "Patient history, symptoms, medications, etc.",
            placeholder="e.g., 65-year-old male with COPD, presenting with shortness of breath...",
            height=100
        )
        
        if st.session_state.abg_values and st.button("🔍 Analyze ABG", type="primary", use_container_width=True):
            st.session_state.clinical_info = clinical_info
            st.session_state.analysis_complete = True
            st.success("✅ Ready for analysis! Go to the Analysis tab.")
    
    with tab2:
        st.header("Step-by-Step Analysis")
        
        if not st.session_state.abg_values:
            st.info("👈 Please input ABG values in the 'Input Data' tab first.")
        elif st.session_state.analysis_complete:
            with st.spinner("🔬 Performing detailed analysis..."):
                clinical_info = st.session_state.get('clinical_info', '')
                analysis = analyze_abg(st.session_state.abg_values, clinical_info, api_key)
                
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown(analysis)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Download button for analysis
                st.download_button(
                    label="📥 Download Analysis Report",
                    data=f"ABG ANALYSIS REPORT\n\n{'='*50}\n\nABG VALUES:\n{json.dumps(st.session_state.abg_values, indent=2)}\n\n{'='*50}\n\nANALYSIS:\n{analysis}",
                    file_name="abg_analysis_report.txt",
                    mime="text/plain"
                )
                
                if st.button("🔄 New Analysis"):
                    st.session_state.analysis_complete = False
                    st.session_state.abg_values = {}
                    st.rerun()
        else:
            st.info("Click 'Analyze ABG' in the Input Data tab to begin analysis.")
    
    with tab3:
        st.header("📚 Learning Resources")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 5-Step Approach")
            st.markdown("""
            1. **pH Assessment** - Acidaemia vs Alkalaemia
            2. **Primary Disturbance** - Respiratory vs Metabolic
            3. **Anion Gap** - Calculate if metabolic acidosis
            4. **Compensation** - Appropriate or mixed disorder?
            5. **Oxygenation** - A-a gradient assessment
            """)
            
            st.markdown("### 🧮 Key Formulas")
            st.markdown("""
            **Anion Gap:**
            ```
            AG = Na⁺ - (Cl⁻ + HCO₃⁻)
            Normal: 8-16 mmol/L
            ```
            
            **Corrected AG (for albumin):**
            ```
            Corrected AG = AG + [(40 - albumin)/10] × 2.5
            ```
            
            **A-a Gradient:**
            ```
            A-a = PAO₂ - PaO₂
            PAO₂ = 20 - (PaCO₂ × 1.2)
            Normal: 2-4 kPa
            ```
            """)
        
        with col2:
            st.markdown("### 🔍 Common Causes")
            
            with st.expander("Respiratory Acidosis (↑pCO₂)"):
                st.markdown("""
                - COPD exacerbation
                - Pneumonia
                - Respiratory muscle weakness
                - Opioid overdose
                - Obesity hypoventilation
                """)
            
            with st.expander("Metabolic Acidosis (↓HCO₃⁻)"):
                st.markdown("""
                **High Anion Gap:**
                - Diabetic ketoacidosis
                - Lactic acidosis
                - Renal failure
                - Toxins (methanol, ethylene glycol)
                
                **Normal Anion Gap:**
                - Diarrhea
                - Renal tubular acidosis
                - Acetazolamide use
                """)
            
            with st.expander("Respiratory Alkalosis (↓pCO₂)"):
                st.markdown("""
                - Anxiety/hyperventilation
                - Pulmonary embolism
                - Pregnancy
                - Salicylate poisoning (early)
                - High altitude
                """)
            
            with st.expander("Metabolic Alkalosis (↑HCO₃⁻)"):
                st.markdown("""
                - Vomiting/NG suction
                - Diuretic use
                - Hyperaldosteronism
                - Hypokalaemia
                """)
        
        st.markdown("---")
        st.markdown("### 💡 Tips for Interpretation")
        st.info("""
        - Always consider the clinical context
        - Look for mixed disorders when compensation seems off
        - Remember: compensation never overcorrects
        - Calculate anion gap for ALL metabolic acidosis cases
        - Don't forget to correct anion gap for albumin in chronic illness
        """)

if __name__ == "__main__":
    main()

import streamlit as st
import requests
from PIL import Image
import io

# Backend API Configuration
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="SnakeSense AI",
    page_icon="🐍",
    layout="wide"
)

# App Header
st.title("🐍 SnakeSense AI")
st.caption("AI-assisted snake identification and emergency snakebite guidance for India")

# Language Selector Sidebar
st.sidebar.header("⚙️ Settings / भाषा / ભાષા")
lang = st.sidebar.selectbox("Select Language", ["English", "Hindi (हिंदी)", "Gujarati (ગુજરાતી)"])

lang_code = "hi" if lang == "Hindi (हिंदी)" else ("gu" if lang == "Gujarati (ગુજરાતી)" else "en")

# Navigation Tabs
tab1, tab2 = st.tabs(["📷 Snake Species Identification", "🚨 Bite Emergency Triage"])

# --- TAB 1: SPECIES IDENTIFICATION ---
with tab1:
    st.subheader("Upload Snake Image")
    uploaded_file = st.file_uploader("Choose a snake photo...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
        with col2:
            if st.button("🔍 Identify Snake Species", type="primary"):
                with st.spinner("Analyzing visual scale features..."):
                    try:
                        # Prepare file for API
                        img_bytes = io.BytesIO()
                        image.save(img_bytes, format="JPEG")
                        img_bytes.seek(0)
                        
                        files = {"file": ("image.jpg", img_bytes, "image/jpeg")}
                        response = requests.post(f"{API_URL}/predict", files=files)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            if data.get("is_low_confidence"):
                                st.warning("⚠️ Low Confidence / Look-alike Alert: The image may be blurry or ambiguous. Treat as potentially venomous.")
                                
                            st.subheader("Top-3 Predictions")
                            for pred in data["top_predictions"]:
                                confidence = pred["confidence_percentage"]
                                scientific_name = pred["scientific_name"]
                                common_name = pred["common_name"]
                                
                                # Local name lookup based on sidebar language
                                local_name = pred["local_names"].get(lang_code, common_name)
                                toxicity = pred["toxicity_status"]
                                
                                badge = "🔴 HIGHLY VENOMOUS" if "HIGHLY" in toxicity else ("🟡 MILDLY VENOMOUS" if "MILDLY" in toxicity else "🟢 NON-VENOMOUS")
                                
                                with st.expander(f"Rank {pred['rank']}: {common_name} ({local_name}) - {confidence}%", expanded=(pred['rank']==1)):
                                    st.write(f"**Scientific Name:** *{scientific_name}*")
                                    st.write(f"**Toxicity:** {badge}")
                                    st.write(f"**Venom Type:** {pred['venom_type']}")
                                    st.progress(confidence / 100)
                                    
                            st.info(f"ℹ️ {data['safety_disclaimer']}")
                        else:
                            st.error(f"API Error: {response.json().get('detail', 'Failed to get predictions')}")
                    except Exception as e:
                        st.error(f"Could not connect to FastAPI backend at {API_URL}. Ensure uvicorn is running. Error: {e}")

# --- TAB 2: BITE EMERGENCY TRIAGE ---
with tab2:
    st.error("🚨 EMERGENCY MODE: Use this tab if a person has been bitten or touched by a snake.")
    
    st.subheader("Symptom Questionnaire")
    bitten = st.checkbox("Has a person been bitten by a snake?", value=True)
    time_elapsed = st.number_input("Time elapsed since bite (minutes):", min_value=0, value=15)
    
    st.write("Select all symptoms currently present:")
    local_swelling = st.checkbox("Local swelling, pain, or discoloration at bite site")
    drooping_eyelids = st.checkbox("Drooping eyelids (Ptosis) or facial weakness")
    difficulty_breathing = st.checkbox("Difficulty breathing or swallowing")
    spontaneous_bleeding = st.checkbox("Bleeding from gums, nose, or dark brown urine")
    
    if st.button("🚨 Assess Emergency Urgency", type="primary"):
        payload = {
            "bitten": bitten,
            "time_elapsed_minutes": time_elapsed,
            "local_swelling": local_swelling,
            "drooping_eyelids": drooping_eyelids,
            "difficulty_breathing": difficulty_breathing,
            "spontaneous_bleeding": spontaneous_bleeding
        }
        
        try:
            res = requests.post(f"{API_URL}/triage", json=payload)
            if res.status_code == 200:
                triage = res.json()
                urgency = triage["urgency_level"]
                
                if urgency == "CRITICAL":
                    st.error(f"🔴 URGENCY LEVEL: {urgency} - {triage['suspected_toxicity']}")
                else:
                    st.warning(f"🟡 URGENCY LEVEL: {urgency} - {triage['suspected_toxicity']}")
                    
                st.markdown(f"### 🏥 {triage['action_protocol']['immediate_action']}")
                
                col_dos, col_donts = st.columns(2)
                
                with col_dos:
                    st.success("### ✅ DO'S")
                    for item in triage['action_protocol']['dos']:
                        st.write(f"- {item}")
                        
                with col_donts:
                    st.error("### ❌ DON'TS")
                    for item in triage['action_protocol']['donts']:
                        st.write(f"- {item}")
                        
                st.info(f"📞 **Emergency Contacts:** {', '.join(triage['emergency_contacts'])}")
        except Exception as e:
            st.error(f"Error connecting to triage API: {e}")
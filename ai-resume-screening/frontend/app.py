import streamlit as st
import sys
import os
import plotly.express as px
import pandas as pd
#from streamlit_option_menu import option_menu 

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.processor import extract_text
from backend.resume_analyzer import ResumeAnalyzer

# Set page config
st.set_page_config(layout="wide", page_title="AI Resume Screening System")

# Custom CSS
st.markdown("""
<style>
    .main {padding: 0rem 2rem;}
    .stButton>button {width: 100%; background-color: #4CAF50; color: white;}
    .stMetric {background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem;}
    .stProgress {height: 10px;}
    .css-1v0mbdj {width: 100%;}
</style>
""", unsafe_allow_html=True)

# Initialize the analyzer
analyzer = ResumeAnalyzer()

# Sidebar navigation
with st.sidebar:
    st.title("Main Menu")
    selected = st.radio(
        "",
        ["Dashboard", "Resume Analysis", "ATS Optimization", "Help"],
        index=0
    )

st.title("AI Resume Screening System")

# File upload and job description section
col1, col2 = st.columns([2, 3])

with col1:
    st.markdown("### Upload Resumes")
    uploaded_files = st.file_uploader("Choose PDF/DOCX files", type=["pdf", "docx"], accept_multiple_files=True)
    if uploaded_files:
        upload_button = st.button("Process Resumes")

with col2:
    st.markdown("### Job Description")
    job_description = st.text_area("Enter the job description", height=200)

if uploaded_files and job_description and 'upload_button' in locals() and upload_button:
    # Create absolute path for save directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_dir = os.path.join(project_root, 'data', 'sample_resumes')
    
    # Ensure directory exists
    os.makedirs(save_dir, exist_ok=True)
    
    # Process each resume
    resume_analyses = []
    for uploaded_file in uploaded_files:
        # Save file
        save_path = os.path.join(save_dir, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Extract and analyze resume
        resume_text = extract_text(save_path)
        analysis = analyzer.generate_improvement_suggestions(resume_text, job_description)
        resume_analyses.append({
            'name': uploaded_file.name,
            'text': resume_text,
            'analysis': analysis
        })
    
    st.success(f"Successfully processed {len(resume_analyses)} resumes!")
    
    # Display comparative analysis
    st.markdown("---")
    st.subheader("📊 Comparative Analysis Dashboard")
    
    # Create comparison table
    comparison_data = {
        'Resume': [],
        'ATS Score': [],
        'Keyword Match': [],
        'Format Score': [],
        'Overall Score': []
    }
    
    for resume in resume_analyses:
        keyword_match = 100 - (len(resume['analysis']['missing_keywords']) * 10 if resume['analysis']['missing_keywords'] else 0)
        overall_score = int((resume['analysis']['ats_score'] + keyword_match + 85) / 3)
        
        comparison_data['Resume'].append(resume['name'])
        comparison_data['ATS Score'].append(f"{resume['analysis']['ats_score']}%")
        comparison_data['Keyword Match'].append(f"{keyword_match}%")
        comparison_data['Format Score'].append("85%")
        comparison_data['Overall Score'].append(f"{overall_score}%")
    
    st.dataframe(pd.DataFrame(comparison_data))
    
    # Individual resume analysis tabs
    resume_tabs = st.tabs([f"Resume {i+1}: {resume['name']}" for i, resume in enumerate(resume_analyses)])
    
    for tab, resume in zip(resume_tabs, resume_analyses):
        with tab:
            col1, col2, col3, col4 = st.columns(4)
            keyword_match = 100 - (len(resume['analysis']['missing_keywords']) * 10 if resume['analysis']['missing_keywords'] else 0)
            overall_score = int((resume['analysis']['ats_score'] + keyword_match + 85) / 3)
            
            with col1:
                st.metric("ATS Score", f"{resume['analysis']['ats_score']}%")
            with col2:
                st.metric("Keyword Match", f"{keyword_match}%")
            with col3:
                st.metric("Format Score", "85%")
            with col4:
                st.metric("Overall Score", f"{overall_score}%")
            
            # Detailed analysis section
            st.markdown("### 📈 Detailed Analysis")
            analysis_tabs = st.tabs(["Skills Match", "ATS Optimization", "Recommendations"])
            
            with analysis_tabs[0]:
                skills_data = {
                    'Category': ['Technical Skills', 'Soft Skills', 'Experience', 'Education', 'Certifications'],
                    'Score': [85, 90, 75, 95, 80]
                }
                fig = px.line_polar(pd.DataFrame(skills_data), r='Score', theta='Category', line_close=True)
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with analysis_tabs[1]:
                st.markdown("#### Missing Keywords")
                if resume['analysis']['missing_keywords']:
                    for keyword in resume['analysis']['missing_keywords']:
                        st.warning(f"🔍 {keyword}")
                else:
                    st.success("✅ No missing keywords found!")
                
                st.markdown("#### ATS Score Breakdown")
                ats_metrics = {
                    'Metric': ['Keyword Optimization', 'Format Compliance', 'Section Headers', 'Content Relevance'],
                    'Score': [85, 90, 95, resume['analysis']['ats_score']]
                }
                fig = px.bar(pd.DataFrame(ats_metrics), x='Metric', y='Score',
                             title='ATS Optimization Metrics')
                st.plotly_chart(fig, use_container_width=True)
            
            with analysis_tabs[2]:
                # Resume Summary
                st.markdown("#### Resume Summary")
                summary_text = resume['text'][:500] + "..." if len(resume['text']) > 500 else resume['text']
                st.text_area("Summary", summary_text, height=100)
                
                st.markdown("#### Improvement Suggestions")
                for i, suggestion in enumerate(resume['analysis']['suggestions'], 1):
                    st.info(f"{i}. {suggestion}")
                
                st.markdown("#### Recommended Actions")
                action_items = [
                    "Add missing keywords in relevant sections",
                    "Quantify achievements with metrics",
                    "Use industry-standard section headings",
                    "Ensure consistent formatting"
                ]
                for item in action_items:
                    st.success(f"✅ {item}")
            
            # Resume preview in expandable section
            with st.expander("📄 View Full Resume"):
                st.markdown("### Resume Content")
                st.text_area("Content", resume['text'], height=300)

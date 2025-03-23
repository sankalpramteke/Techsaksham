import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import os

# Load spaCy model for NLP processing
nlp = spacy.load('en_core_web_sm')

class ResumeAnalyzer:
    def __init__(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        resume_path = os.path.join(project_root, 'data', 'Resume.csv')
        try:
            self.resume_dataset = pd.read_csv(resume_path)
        except FileNotFoundError:
            # Create an empty dataset if file doesn't exist
            self.resume_dataset = pd.DataFrame()
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
    def preprocess_text(self, text):
        """Clean and preprocess text data"""
        doc = nlp(text.lower())
        tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
        return ' '.join(tokens)
    
    def extract_skills(self, text):
        """Extract skills from text using keyword matching and NLP processing"""
        doc = nlp(text.lower())
        # Focus on noun phrases and proper nouns as potential skills
        skills = [chunk.text for chunk in doc.noun_chunks]
        skills.extend([token.text for token in doc if token.pos_ in ['PROPN', 'NOUN']])
        # Clean and normalize skills
        skills = [skill.strip() for skill in skills if len(skill.strip()) > 2]
        return list(set(skills))
    
    def calculate_ats_score(self, resume_text, job_description):
        """Calculate ATS compatibility score"""
        # Preprocess texts
        processed_resume = self.preprocess_text(resume_text)
        processed_jd = self.preprocess_text(job_description)
        
        # Vectorize texts
        text_vectors = self.vectorizer.fit_transform([processed_resume, processed_jd])
        
        # Calculate similarity score
        similarity_score = cosine_similarity(text_vectors[0:1], text_vectors[1:2])[0][0]
        
        return round(similarity_score * 100, 2)
    
    def get_missing_keywords(self, resume_text, job_description):
        """Identify missing keywords from job description"""
        jd_skills = set(self.extract_skills(job_description))
        resume_skills = set(self.extract_skills(resume_text))
        
        return list(jd_skills - resume_skills)
    
    def generate_improvement_suggestions(self, resume_text, job_description):
        """Generate actionable suggestions for resume improvement"""
        missing_keywords = self.get_missing_keywords(resume_text, job_description)
        ats_score = self.calculate_ats_score(resume_text, job_description)
        
        suggestions = {
            'ats_score': ats_score,
            'missing_keywords': missing_keywords,
            'suggestions': [
                'Add missing keywords: ' + ', '.join(missing_keywords),
                'Ensure resume is properly formatted and sections are clearly defined',
                'Use industry-standard section headings',
                'Quantify achievements where possible'
            ]
        }
        
        return suggestions
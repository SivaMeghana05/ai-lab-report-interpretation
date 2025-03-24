import logging
import json
import traceback
import pandas as pd
import numpy as np
import re
from collections import defaultdict

logger = logging.getLogger("HealthLensAI.AdvancedReportAnalyzer")

class AdvancedReportAnalyzer:
    """Enterprise-grade medical data interpretation and analysis with advanced analytics"""
    
    def __init__(self):
        """Initialize with AI service and medical knowledge bases"""
        self._configure_ai()
        self.interpretations_db = self._load_interpretations_db()
        self.recommendations_db = self._load_recommendations_db()
        self.reference_ranges_db = self._load_reference_ranges()
        self.test_relationships = self._load_test_relationships()
        self.condition_patterns = self._load_condition_patterns()
        self.analysis_cache = {}
    
    def _configure_ai(self):
        """Configure the AI API with error handling and advanced options"""
        try:
            # Import here to avoid circular imports
            import google.generativeai as genai
            import streamlit as st
            
            api_key = st.secrets["google"]["api_key"]
            if not api_key:
                raise ValueError("API key not available")
                
            genai.configure(api_key=api_key)
            
            # Configure primary model with enhanced settings
            generation_config = {
                "temperature": 0.2,  # Lower temperature for more factual responses
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
            
            self.primary_model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Configure backup model
            self.backup_model = genai.GenerativeModel("gemini-1.0-pro")
                
            logger.info("AI API configured successfully with enhanced settings")
        except Exception as e:
            logger.error(f"AI API configuration failed: {str(e)}")
            self.primary_model = None
            self.backup_model = None
    
    def _load_interpretations_db(self):
        """Load comprehensive interpretations database"""
        # This would typically load from a database or comprehensive JSON file
        # For now, we'll use an expanded embedded dictionary
        return {
            "Hemoglobin": {
                "High": "Your hemoglobin (oxygen-carrying protein) is higher than normal. This might indicate polycythemia, dehydration, or living at high altitude.",
                "Low": "Your hemoglobin is low, which might make you feel tired or short of breath (anemia). This could be due to iron deficiency, chronic disease, or bleeding."
            },
            "Glucose": {
                "High": "Your blood sugar is higher than normal, which might indicate pre-diabetes or diabetes if persistent. Other causes include stress, medications, or infection.",
                "Low": "Your blood sugar is lower than normal, which might cause weakness, dizziness, confusion or shakiness. This could be due to excessive insulin, missed meals, or intense exercise."
            },
            "Total Cholesterol": {
                "High": "Your cholesterol level is elevated, which may increase your risk of heart disease and stroke. This could be due to diet, genetics, or certain medical conditions.",
                "Low": "Your cholesterol is lower than normal, which might affect hormone production and cell membrane integrity. This could be due to malnutrition, inflammation, or liver disease."
            }
        }
    
    def _load_recommendations_db(self):
        """Load comprehensive recommendations database"""
        return {
            "Hemoglobin": {
                "High": "• Stay well hydrated to reduce blood thickness\n• Consider consulting a hematologist\n• Regular exercise may help regulate blood cell production",
                "Low": "• Include iron-rich foods (lean meats, spinach, beans)\n• Consider iron supplements after consulting with your doctor\n• Pair iron-rich foods with vitamin C sources to enhance absorption"
            },
            "Glucose": {
                "High": "• Limit refined carbohydrates and added sugars\n• Exercise regularly (30 minutes daily)\n• Maintain healthy weight\n• Consider consulting an endocrinologist",
                "Low": "• Eat regular, balanced meals\n• Avoid long periods without eating\n• Keep quick-acting carbohydrate sources available\n• Consider small, frequent meals"
            },
            "Total Cholesterol": {
                "High": "• Reduce saturated and trans fats in your diet\n• Increase soluble fiber intake\n• Exercise regularly\n• Consider heart-healthy Mediterranean or DASH diet",
                "Low": "• Ensure adequate healthy fat intake\n• Consider omega-3 rich foods\n• Consult doctor about hormone health and nutritional status"
            }
        }
    
    def _load_reference_ranges(self):
        """Load comprehensive reference ranges database"""
        return {
            "Hemoglobin": {
                "male": {
                    "adult": (13.5, 17.5),  # g/dL
                    "elderly": (12.5, 17.0)  # g/dL, age 65+
                },
                "female": {
                    "adult": (12.0, 15.5),  # g/dL
                    "elderly": (11.5, 15.0),  # g/dL, age 65+
                    "pregnant": (11.0, 14.0)  # g/dL
                }
            },
            "Glucose": {
                "fasting": (70, 99),  # mg/dL
                "random": (70, 140),  # mg/dL
                "post_meal": (70, 140)  # mg/dL, 2 hours after eating
            },
            "Total Cholesterol": {
                "optimal": (0, 200),  # mg/dL
                "borderline": (200, 239),  # mg/dL
                "high": (240, float('inf'))  # mg/dL
            }
        }
    
    def _load_test_relationships(self):
        """Load database of test relationships for correlation analysis"""
        return {
            "Hemoglobin": ["Hematocrit", "Red Blood Cells", "Iron", "Ferritin"],
            "Glucose": ["Hemoglobin A1C", "Insulin", "C-Peptide"],
            "Total Cholesterol": ["LDL Cholesterol", "HDL Cholesterol", "Triglycerides"]
        }
    
    def _load_condition_patterns(self):
        """Load database of test patterns that suggest specific conditions"""
        return {
            "Metabolic Syndrome": {
                "required": [
                    {"test": "Glucose", "condition": "high"},
                    {"test": "Triglycerides", "condition": "high"}
                ],
                "optional": [
                    {"test": "HDL Cholesterol", "condition": "low"},
                    {"test": "Blood Pressure", "condition": "high"}
                ],
                "min_required": 2,
                "min_optional": 1
            },
            "Iron Deficiency Anemia": {
                "required": [
                    {"test": "Hemoglobin", "condition": "low"},
                    {"test": "Ferritin", "condition": "low"}
                ],
                "optional": [
                    {"test": "Iron", "condition": "low"},
                    {"test": "TIBC", "condition": "high"}
                ],
                "min_required": 2,
                "min_optional": 1
            }
        }
    
    def generate_layman_interpretation(self, test, status, severity):
        """Generate enhanced easy-to-understand interpretation for test results"""
        if test in self.interpretations_db and status in self.interpretations_db[test]:
            return self.interpretations_db[test][status]
        return f"This test is {status.lower()} than the normal range. Consult your healthcare provider for specific advice."
    
    def generate_recommendations(self, test, status):
        """Generate enhanced practical recommendations based on test results"""
        if test in self.recommendations_db and status in self.recommendations_db[test]:
            return self.recommendations_db[test][status]
        return "• Consult your healthcare provider for personalized advice\n• Consider follow-up testing as recommended\n• Monitor symptoms and changes"
    
    def analyze_lab_report(self, report_text):
        """Analyze lab report text and return structured data and interpretation"""
        try:
            if not (self.primary_model or self.backup_model):
                logger.error("No AI models available for analysis")
                return None, None

            interpretation_prompt = self._prepare_interpretation_prompt(report_text)
            extraction_prompt = self._prepare_extraction_prompt(report_text)
            
            interpretation_response = None
            extraction_response = None
            
            # Try primary model first
            if self.primary_model:
                try:
                    interpretation_response = self.primary_model.generate_content(interpretation_prompt)
            extraction_response = self.primary_model.generate_content(extraction_prompt)
                except Exception as e:
                    logger.warning(f"Primary model failed: {str(e)}")
            
            # Fall back to backup model if primary failed or not available
            if not (interpretation_response and extraction_response) and self.backup_model:
                try:
                    interpretation_response = self.backup_model.generate_content(interpretation_prompt)
                    extraction_response = self.backup_model.generate_content(extraction_prompt)
                except Exception as e:
                    logger.error(f"Backup model failed: {str(e)}")
            
            if not (interpretation_response and extraction_response):
                logger.error("Failed to generate responses from both models")
                return None, None
            
            try:
                structured_data = json.loads(extraction_response)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse extraction response: {str(e)}")
                return None, interpretation_response
            
            return structured_data, interpretation_response
            
        except Exception as e:
            logger.error(f"Error analyzing lab report: {str(e)}")
            return None, None
    
    def _generate_fallback_data(self):
        """Generate fallback structured data when AI analysis fails"""
        # Create some basic fallback data
        return [
            {
                "Test": "Hemoglobin",
                "Value": "14.5 g/dL",
                "ReferenceRange": "13.5-17.5 g/dL",
                "Status": "Normal",
                "Category": "Complete Blood Count",
                "Severity": "None"
            },
            {
                "Test": "Glucose",
                "Value": "95 mg/dL",
                "ReferenceRange": "70-99 mg/dL",
                "Status": "Normal",
                "Category": "Metabolic Panel",
                "Severity": "None"
            },
            {
                "Test": "Total Cholesterol",
                "Value": "210 mg/dL",
                "ReferenceRange": "125-200 mg/dL",
                "Status": "High",
                "Category": "Lipid Panel",
                "Severity": "Mild"
            }
        ]
    
    def _generate_fallback_interpretation(self):
        """Generate fallback interpretation when AI analysis fails"""
        return """
        EXECUTIVE SUMMARY
        
        We were unable to perform a complete analysis of your lab report. However, we've provided a basic interpretation based on common lab values.
        
        KEY CONCERNS AND RECOMMENDATIONS
        
        • Please consult with your healthcare provider for a proper interpretation of your lab results
        • Consider scheduling a follow-up appointment to discuss your results in detail
        • Continue with any prescribed medications or treatments
        
        LIFESTYLE AND DIETARY ADVICE
        
        • Maintain a balanced diet rich in fruits, vegetables, and whole grains
        • Stay physically active with at least 150 minutes of moderate exercise per week
        • Stay well-hydrated and get adequate sleep
        • Manage stress through relaxation techniques or mindfulness practices
        
        Note: This is a fallback interpretation generated when our AI analysis system encounters difficulties. It is not based on your specific lab results.
        """
    
    def _prepare_interpretation_prompt(self, text):
        """Generate enhanced interpretation prompt with medical context"""
        return f"""
        Analyze the following lab report and provide a comprehensive medical interpretation. Format the response as follows:

        EXECUTIVE SUMMARY
        - Overall health assessment in 2-3 sentences
        - List of critical findings requiring immediate attention
        - Health score (0-100) with explanation of calculation

        DETAILED ANALYSIS BY CATEGORY
        [For each test category present in the report]
        - Category name and overview
        - Analysis of each abnormal result:
          * Current value vs reference range
          * Severity assessment
          * Clinical significance
        - Potential underlying causes
        - Related health implications

        KEY CONCERNS AND RECOMMENDATIONS
        - Prioritized list of health concerns
        - Specific follow-up tests recommended
        - Suggested specialist consultations if needed
        - Timeline for retesting abnormal values

        LIFESTYLE AND DIETARY ADVICE
        - Specific dietary recommendations based on results
        - Exercise and activity guidelines
        - Lifestyle modifications needed
        - Supplements to consider (if applicable)

        Format with clear headers and bullet points. Prioritize actionable insights.

        Lab Report Text:
        {text}
        """
    
    def _prepare_extraction_prompt(self, text):
        """Generate enhanced extraction prompt with medical context"""
        return f"""
        Extract key lab test parameters from the following lab report as structured data in JSON format.
        For each test include:
        1. "Test": The name of the test
        2. "Value": The numerical value with unit (e.g., "10 g/dL")
        3. "ReferenceRange": The normal reference range
        4. "Status": "High" if above range, "Low" if below range, "Normal" if within range
        5. "Category": Group tests into categories like "Complete Blood Count", "Iron Studies", "Diabetes Profile", etc.
        6. "Severity": Calculate severity as:
           - "Severe" if value is >50% outside range
           - "Moderate" if 25-50% outside range
           - "Mild" if <25% outside range
           - "None" if within range

        Return ONLY valid JSON without explanation, markdown, or text.

        Lab Report Text:
        {text}
        """
    
    def display_test_results(self, df):
        """Display test results with enhanced interactive UI"""
        try:
            import streamlit as st
        st.markdown("### 🔬 Detailed Test Results")
        
            if 'Category' in df.columns and not df['Category'].empty:
        categories = df['Category'].unique().tolist()
        selected_category = st.selectbox("Filter by Category", ["All Categories"] + categories)
        
        filtered_df = df.copy()
        if selected_category != "All Categories":
            filtered_df = filtered_df[filtered_df['Category'] == selected_category]
        
        for category in filtered_df['Category'].unique():
            with st.expander(f"📊 {category} Panel", expanded=True):
                        category_df = filtered_df[filtered_df['Category'] == category]
                for _, row in category_df.iterrows():
                    with st.container():
                                col1, col2 = st.columns([1, 1])
                        with col1:
                            st.markdown(f"### {row['Test']}")
                            value_color = ('🔴' if row['Status'] == 'High' else '🔵' if row['Status'] == 'Low' else '🟢')
                            st.markdown(f"{value_color} **Current Value:** {row['Value']}")
                            st.markdown(f"**Normal Range:** {row['ReferenceRange']}")
                        with col2:
                            if row['Status'] != 'Normal':
                                severity = row.get('Severity', 'Moderate')
                                        st.markdown(f"**Severity:** {severity}")
                                st.markdown("**What this means:**")
                                interpretation = self.generate_layman_interpretation(row['Test'], row['Status'], severity)
                                st.markdown(interpretation)
                                st.markdown("**Recommendations:**")
                                recommendations = self.generate_recommendations(row['Test'], row['Status'])
                                st.markdown(recommendations)
                            else:
                                st.markdown("✅ **Result is within normal range**")
                                st.markdown("Continue maintaining your healthy lifestyle and regular check-ups.")
                                    st.markdown("---")
                                    else:
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            logger.error(f"Error displaying test results: {str(e)}")
            import streamlit as st
            st.warning("Error displaying detailed test results. Showing basic table instead.")
            st.dataframe(df, use_container_width=True)
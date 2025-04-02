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
                return self._generate_fallback_data(), self._generate_fallback_interpretation()

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
                return self._generate_fallback_data(), self._generate_fallback_interpretation()
            
            try:
                # Convert the extraction response to string before parsing JSON
                if hasattr(extraction_response, 'text'):
                    extraction_text = extraction_response.text
                elif hasattr(extraction_response, 'parts'):
                    extraction_text = ''.join([part.text for part in extraction_response.parts])
                else:
                    extraction_text = str(extraction_response)
                
                # Convert the interpretation response to string
                if hasattr(interpretation_response, 'text'):
                    interpretation_text = interpretation_response.text
                elif hasattr(interpretation_response, 'parts'):
                    interpretation_text = ''.join([part.text for part in interpretation_response.parts])
                else:
                    interpretation_text = str(interpretation_response)
                
                # Clean up the extraction text to ensure it's valid JSON
                extraction_text = extraction_text.strip()
                if not extraction_text.startswith('['):
                    # Try to find the JSON array in the text
                    start_idx = extraction_text.find('[')
                    end_idx = extraction_text.rfind(']')
                    if start_idx != -1 and end_idx != -1:
                        extraction_text = extraction_text[start_idx:end_idx + 1]
                    else:
                        logger.error("Could not find valid JSON array in response")
                        return self._generate_fallback_data(), interpretation_text
                
                try:
                    structured_data = json.loads(extraction_text)
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON, trying to fix common issues")
                    # Try to fix common JSON formatting issues
                    extraction_text = re.sub(r'(\w+):', r'"\1":', extraction_text)  # Quote unquoted keys
                    extraction_text = re.sub(r'\'', r'"', extraction_text)  # Replace single quotes with double quotes
                    try:
                        structured_data = json.loads(extraction_text)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse fixed JSON: {str(e)}")
                        return self._generate_fallback_data(), interpretation_text
                
                # Ensure structured_data is a list
                if not isinstance(structured_data, list):
                    structured_data = [structured_data]
                
                # Add required fields if missing
                for test in structured_data:
                    if 'Category' not in test:
                        # Try to determine category from test name
                        test_name = test.get('Test', '').lower()
                        if any(x in test_name for x in ['hemoglobin', 'wbc', 'rbc', 'platelet']):
                            test['Category'] = 'Complete Blood Count'
                        elif any(x in test_name for x in ['glucose', 'sodium', 'potassium', 'chloride']):
                            test['Category'] = 'Metabolic Panel'
                        elif any(x in test_name for x in ['cholesterol', 'triglycerides', 'hdl', 'ldl']):
                            test['Category'] = 'Lipid Panel'
                        else:
                            test['Category'] = 'Other Tests'
                    
                    if 'Severity' not in test:
                        if test.get('Status', '') == 'Normal':
                            test['Severity'] = 'None'
                        else:
                            # Calculate severity based on how far the value is from the reference range
                            try:
                                value = float(test.get('Value', '0').split()[0])
                                ref_range = test.get('ReferenceRange', '')
                                if '-' in ref_range:
                                    low, high = map(float, ref_range.split('-'))
                                    mid = (low + high) / 2
                                    deviation = abs(value - mid) / (high - low)
                                    
                                    if deviation > 0.5:
                                        test['Severity'] = 'Severe'
                                    elif deviation > 0.25:
                                        test['Severity'] = 'Moderate'
                                    else:
                                        test['Severity'] = 'Mild'
                                else:
                                    test['Severity'] = 'Moderate'  # Default if range format is unknown
                            except:
                                test['Severity'] = 'Moderate'  # Default if calculation fails
                    
                    # Ensure Status field exists
                    if 'Status' not in test:
                        test['Status'] = 'Normal'  # Default to Normal if not specified
                
                return structured_data, interpretation_text
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse extraction response: {str(e)}")
                return self._generate_fallback_data(), interpretation_text
            
        except Exception as e:
            logger.error(f"Error analyzing lab report: {str(e)}")
            return self._generate_fallback_data(), self._generate_fallback_interpretation()
   
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
    
    def _get_generic_interpretation(self, test_name):
        """Get generic interpretation for a test"""
        # First try to get from interpretations database
        for test, interpretations in self.interpretations_db.items():
            if test.lower() in test_name.lower():
                # Return a generic version combining both high and low interpretations
                high_interp = interpretations.get('High', '')
                low_interp = interpretations.get('Low', '')
                return f"This test measures {high_interp.split('is higher')[0].strip()}. " + \
                       "Abnormal results may indicate various conditions and should be discussed with your healthcare provider."
        
        # Fallback generic interpretations for common test types
        generic_interpretations = {
            "Glucose": "This test measures your blood sugar levels. Abnormal results may indicate issues with blood sugar regulation.",
            "HbA1c": "This test shows your average blood sugar level over the past 2-3 months.",
            "Cholesterol": "This test measures blood fats that can affect your heart health.",
            "HDL": "This measures 'good' cholesterol that helps remove other forms of cholesterol from your bloodstream.",
            "LDL": "This measures 'bad' cholesterol that can build up in your arteries.",
            "Triglycerides": "This measures a type of fat in your blood that can affect heart health.",
            "Hemoglobin": "This measures the oxygen-carrying protein in your blood.",
            "Iron": "This measures the iron levels in your blood, which is important for producing red blood cells.",
            "Vitamin D": "This measures vitamin D levels, which is important for bone health and immune function.",
            "TSH": "This measures thyroid stimulating hormone, which indicates thyroid function.",
            "Creatinine": "This measures kidney function by checking how well your kidneys filter waste."
        }
        
        # Look for partial matches in test name
        for key, value in generic_interpretations.items():
            if key.lower() in test_name.lower():
                return value
        
        return "This test result should be discussed with your healthcare provider for proper interpretation."

    def _get_specific_recommendations(self, test_name):
        """Get specific recommendations based on test name"""
        # First try to get from recommendations database
        for test, recommendations in self.recommendations_db.items():
            if test.lower() in test_name.lower():
                # Combine both high and low recommendations for a general list
                all_recs = []
                for status_recs in recommendations.values():
                    all_recs.extend(status_recs.split('\n'))
                return list(set(all_recs))  # Remove duplicates
        
        # Fallback generic recommendations for common test types
        generic_recommendations = {
            "Glucose": [
                "Monitor your blood sugar levels as recommended",
                "Follow a balanced diet low in simple sugars",
                "Engage in regular physical activity",
                "Maintain a healthy weight",
                "Take medications as prescribed"
            ],
            "HbA1c": [
                "Work with your healthcare provider on diabetes management",
                "Monitor blood sugar levels regularly",
                "Follow a balanced diet",
                "Exercise regularly",
                "Take medications as prescribed"
            ],
            "Cholesterol": [
                "Follow a heart-healthy diet",
                "Exercise regularly",
                "Maintain a healthy weight",
                "Avoid smoking",
                "Limit alcohol consumption"
            ]
        }
        
        # Look for partial matches in test name
        for key, value in generic_recommendations.items():
            if key.lower() in test_name.lower():
                return value
        
        return ["Discuss these results with your healthcare provider",
                "Follow your provider's recommendations",
                "Report any concerning symptoms",
                "Schedule follow-up appointments as advised"]

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
                                        # Use class's own interpretation method
                                        interpretation = self.generate_layman_interpretation(
                                            row['Test'], 
                                            row['Status'],
                                            severity
                                        )
                                        st.markdown(interpretation)
                                        st.markdown("**Recommendations:**")
                                        # Use class's own recommendations method
                                        recommendations = self.generate_recommendations(
                                            row['Test'],
                                            row['Status']
                                        )
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
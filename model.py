import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

class MedicalChatbot:
    def __init__(self):
        # Load datasets
        self.df_training = pd.read_csv('Training.csv')
        self.df_description = pd.read_csv('symptom_Description.csv')
        self.df_precaution = pd.read_csv('symptom_precaution.csv')
        self.df_severity = pd.read_csv('Symptom_severity.csv')
        
        # Print column names for debugging
        print("Description DataFrame columns:", self.df_description.columns.tolist())
        
        # Get list of all symptoms (excluding 'prognosis' column)
        self.symptoms = list(self.df_training.columns[:-1])
        
        # Create a mapping of normalized symptoms to actual symptoms
        self.symptom_mapping = {}
        for symptom in self.symptoms:
            # Create variations of the symptom name
            normal = symptom.replace('_', ' ').lower()
            self.symptom_mapping[normal] = symptom
            # Also add the original version
            self.symptom_mapping[symptom.lower()] = symptom
        
        # Comprehensive symptom mappings
        self.symptom_phrases = {
            'yellow ooze': 'yellow_crust_ooze',
            'yellow crust': 'yellow_crust_ooze',
            'oozing': 'yellow_crust_ooze',
            'crusty ooze': 'yellow_crust_ooze',
            'red nose': 'red_sore_around_nose',
            'sore nose': 'red_sore_around_nose',
            'nose sore': 'red_sore_around_nose',
            'sore around nose': 'red_sore_around_nose',
            'blister': 'blister',
            'blisters': 'blister',
            'high fever': 'high_fever',
            'fever': 'fever',
            'temperature': 'fever',
            'headache': 'headache',
            'head pain': 'headache',
            'body pain': 'body_pain',
            'muscle pain': 'muscle_pain',
            'joint pain': 'joint_pain',
            'joints hurt': 'joint_pain',
            'stomach pain': 'stomach_pain',
            'belly pain': 'stomach_pain',
            'abdominal pain': 'stomach_pain',
            'cough': 'cough',
            'coughing': 'cough',
            'sore throat': 'sore_throat',
            'throat pain': 'sore_throat',
            'throat hurts': 'sore_throat',
            'runny nose': 'runny_nose',
            'nose running': 'runny_nose',
            'weakness': 'weakness',
            'feeling weak': 'weakness',
            'fatigue': 'fatigue',
            'tired': 'fatigue',
            'exhausted': 'fatigue',
            'chills': 'chills',
            'shivering': 'chills',
            'feeling cold': 'chills',
            'vomiting': 'vomiting',
            'throwing up': 'vomiting',
            'nausea': 'vomiting',
            'dizziness': 'dizziness',
            'feeling dizzy': 'dizziness',
            'dizzy spells': 'dizziness'
        }
        
        # Train the model
        self.train_model()

    def train_model(self):
        # Prepare training data
        X = self.df_training.drop('prognosis', axis=1)
        y = self.df_training['prognosis']
        
        # Encode disease labels
        self.encoder = LabelEncoder()
        y = self.encoder.fit_transform(y)
        
        # Train Random Forest model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)

    def predict_condition(self, symptoms):
        # Create input vector
        input_vector = pd.DataFrame(0, index=[0], columns=self.symptoms)
        for symptom in symptoms:
            if symptom in self.symptoms:
                input_vector[symptom] = 1
        
        # Get prediction probabilities
        prediction_proba = self.model.predict_proba(input_vector)[0]
        prediction = self.model.predict(input_vector)[0]
        
        # Get top 3 predictions with their probabilities
        top_3_indices = prediction_proba.argsort()[-3:][::-1]
        top_3_predictions = []
        
        for idx in top_3_indices:
            condition = self.encoder.inverse_transform([idx])[0]
            confidence = prediction_proba[idx] * 100
            top_3_predictions.append((condition, confidence))
        
        return top_3_predictions

    def get_description(self, condition):
        """Get description for a given condition"""
        try:
            # Print for debugging
            print(f"Looking for condition: {condition}")
            print(f"Available conditions: {self.df_description['disease'].unique()}")
            
            description = self.df_description[
                self.df_description['disease'].str.strip() == condition.strip()
            ]['description'].values[0]
            
            return description if isinstance(description, str) else "Description not available."
        except Exception as e:
            print(f"Error getting description: {str(e)}")
            return "Description not available."

    def get_precautions(self, condition):
        """Get precautions for a given condition"""
        try:
            precautions = []
            row = self.df_precaution[
                self.df_precaution['Disease'].str.strip() == condition.strip()
            ]
            
            for i in range(1, 5):
                precaution = row[f'Precaution_{i}'].values[0]
                if isinstance(precaution, str) and precaution.strip():
                    precautions.append(precaution.strip())
            
            return precautions if precautions else ["No specific precautions available."]
        except Exception as e:
            print(f"Error getting precautions: {str(e)}")
            return ["No specific precautions available."]

    def extract_symptoms_from_text(self, text):
        """Extract symptoms from natural language text"""
        text = text.lower().strip()
        extracted_symptoms = set()

        # Remove common phrases
        common_phrases = [
            'i am', 'i have', 'i\'m', 'suffering from', 'experiencing',
            'feeling', 'with', 'got', 'having', 'there is', 'there are'
        ]
        for phrase in common_phrases:
            text = text.replace(phrase, '')

        # Check for multi-word symptoms first
        for phrase, symptom in self.symptom_phrases.items():
            if phrase in text:
                extracted_symptoms.add(symptom)
                # Remove the matched phrase to avoid double matching
                text = text.replace(phrase, '')

        # Check for partial matches in remaining text
        words = text.split()
        for word in words:
            for phrase, symptom in self.symptom_phrases.items():
                if (word in phrase.split() or phrase in word) and len(word) > 3:
                    extracted_symptoms.add(symptom)

        # If no symptoms found, try fuzzy matching
        if not extracted_symptoms:
            for phrase, symptom in self.symptom_phrases.items():
                if self.fuzzy_match(text, phrase):
                    extracted_symptoms.add(symptom)

        return list(extracted_symptoms)

    def fuzzy_match(self, text1, text2, threshold=0.8):
        """Simple fuzzy matching using ratio comparison"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1, text2).ratio() > threshold

    def find_matching_symptom(self, text):
        """Find matching symptoms from text"""
        text = text.lower().strip()
        matches = []
        
        # Check direct matches in symptom phrases
        if text in self.symptom_phrases:
            return [self.symptom_phrases[text]]
        
        # Check for partial matches
        for phrase, symptom in self.symptom_phrases.items():
            if phrase in text or text in phrase:
                matches.append(symptom)
        
        # Check original symptom list
        for symptom in self.symptoms:
            symptom_normalized = symptom.replace('_', ' ')
            if text in symptom_normalized or symptom_normalized in text:
                matches.append(symptom)
        
        return list(set(matches))  # Remove duplicates

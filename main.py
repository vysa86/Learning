from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from fastapi.middleware.cors import CORSMiddleware
# Load the saved model
model = joblib.load('random_forest_model.joblib')

# Define the known categories for each encoder based on training data
# Replace these lists with the actual categories used during model training
venues = ['MCG', 'Lords', 'Eden Gardens']  # Add all known venues here
match_types = ['ODI', 'T20', 'Test']       # Add all known match types here
teams = ['India', 'Australia', 'England']  # Add all known teams here

# Initialize and fit encoders with known categories
venue_encoder = LabelEncoder()
venue_encoder.fit(venues)

match_type_encoder = LabelEncoder()
match_type_encoder.fit(match_types)

team_batting_encoder = LabelEncoder()
team_batting_encoder.fit(teams)

team_bowling_encoder = LabelEncoder()
team_bowling_encoder.fit(teams)

# Initialize FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust the list to specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Define input data model
class MatchData(BaseModel):
    venue: str
    match_type: str
    team_batting: str
    team_bowling: str
@app.get("/")
async def root():
    return {"message": "Hello World"}
# Prediction endpoint
@app.post("/predict")
def predict_score(data: MatchData):
    # Encode input data
    try:
        venue_encoded = venue_encoder.transform([data.venue])[0]
        match_type_encoded = match_type_encoder.transform([data.match_type])[0]
        team_batting_encoded = team_batting_encoder.transform([data.team_batting])[0]
        team_bowling_encoded = team_bowling_encoder.transform([data.team_bowling])[0]
    except ValueError as e:
        return {"error": f"Encoding error: {str(e)}. Ensure the inputs match known categories."}

    # Prepare input DataFrame
    input_data = pd.DataFrame({
        'Venue': [venue_encoded],
        'Match_Type': [match_type_encoded],
        'Team_Batting': [team_batting_encoded],
        'Team_Bowling': [team_bowling_encoded]
    })

    # Predict and round the result
    predicted_score = model.predict(input_data)
    rounded_predicted_score = round(predicted_score[0])

    # Return the result as a JSON response
    return {"predicted_score": rounded_predicted_score}

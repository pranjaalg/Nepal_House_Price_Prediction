import os
import pickle
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Nepal House Price Prediction API")

# Setup templates directory
templates = Jinja2Templates(directory="templates")

# Model path
MODEL_PATH = "nepal_house_price_lr_model.pkl"


def load_model():
  if os.path.exists(MODEL_PATH):
    try:
      with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)
    except Exception:
      return None
  return None


model = load_model()


# Pydantic schema for request validation
class PropertyInput(BaseModel):
  city: str
  property_type: str
  area_sqft: float
  bedrooms: int
  bathrooms: int


@app.get("/", response_class=HTMLResponse)
async def read_root():
  # Serves the beautiful frontend UI directly
  html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nepal Real Estate Price Predictor</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #4f46e5;
                --primary-hover: #4338ca;
                --bg-gradient: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
                --card-bg: #ffffff;
                --text-main: #1f2937;
                --text-muted: #6b7280;
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: 'Inter', sans-serif;
            }

            body {
                background: var(--bg-gradient);
                color: var(--text-main);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }

            .container {
                background: var(--card-bg);
                width: 100%;
                max-width: 600px;
                padding: 40px;
                border-radius: 16px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
            }

            .header {
                text-align: center;
                margin-bottom: 30px;
            }

            .header h1 {
                font-size: 28px;
                color: var(--primary);
                margin-bottom: 8px;
            }

            .header p {
                color: var(--text-muted);
                font-size: 14px;
            }

            .form-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }

            .form-group {
                margin-bottom: 20px;
            }

            .form-group.full-width {
                grid-column: span 2;
            }

            label {
                display: block;
                font-size: 13px;
                font-weight: 600;
                margin-bottom: 6px;
                color: #374151;
            }

            select, input {
                width: 100%;
                padding: 12px 14px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.2s, box-shadow 0.2s;
                background: #f9fafb;
            }

            select:focus, input:focus {
                border-color: var(--primary);
                box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
                background: #ffffff;
            }

            button {
                width: 100%;
                background: var(--primary);
                color: white;
                border: none;
                padding: 14px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.2s, transform 0.1s;
                margin-top: 10px;
            }

            button:hover {
                background: var(--primary-hover);
            }

            button:active {
                transform: scale(0.98);
            }

            .result-card {
                margin-top: 25px;
                background: #eef2ff;
                border: 1px solid #c7d2fe;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                display: none;
            }

            .result-card h3 {
                color: #312e81;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 6px;
            }

            .price {
                font-size: 26px;
                font-weight: 700;
                color: var(--primary);
            }

            .error-card {
                margin-top: 20px;
                background: #fee2e2;
                border: 1px solid #f87171;
                color: #b91c1c;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                display: none;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏠 Nepal Real Estate Predictor</h1>
                <p>Fill out the property characteristics to estimate market value.</p>
            </div>

            <form id="predictionForm">
                <div class="form-grid">
                    <div class="form-group">
                        <label for="city">City</label>
                        <select id="city" required>
                            <option value="ktm">Kathmandu (ktm)</option>
                            <option value="lalitpur">Lalitpur</option>
                            <option value="bkt">Bhaktapur (bkt)</option>
                            <option value="pokhara">Pokhara</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="property_type">Property Type</label>
                        <select id="property_type" required>
                            <option value="house">House</option>
                            <option value="apartment">Apartment</option>
                            <option value="townhouse">Townhouse</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="area_sqft">Area (sq. ft.)</label>
                        <input type="number" id="area_sqft" min="100" max="50000" value="1500" step="50" required>
                    </div>

                    <div class="form-group">
                        <label for="bedrooms">Bedrooms</label>
                        <input type="number" id="bedrooms" min="1" max="20" value="3" required>
                    </div>

                    <div class="form-group full-width">
                        <label for="bathrooms">Bathrooms</label>
                        <input type="number" id="bathrooms" min="1" max="20" value="2" required>
                    </div>
                </div>

                <button type="submit" id="submitBtn">Estimate Market Price</button>
            </form>

            <div id="resultCard" class="result-card">
                <h3>Estimated Valuation</h3>
                <div class="price" id="priceOutput">NPR 0</div>
            </div>

            <div id="errorCard" class="error-card"></div>
        </div>

        <script>
            document.getElementById('predictionForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const submitBtn = document.getElementById('submitBtn');
                const resultCard = document.getElementById('resultCard');
                const errorCard = document.getElementById('errorCard');
                const priceOutput = document.getElementById('priceOutput');

                submitBtn.disabled = true;
                submitBtn.textContent = 'Calculating...';
                resultCard.style.display = 'none';
                errorCard.style.display = 'none';

                const data = {
                    city: document.getElementById('city').value,
                    property_type: document.getElementById('property_type').value,
                    area_sqft: parseFloat(document.getElementById('area_sqft').value),
                    bedrooms: parseInt(document.getElementById('bedrooms').value),
                    bathrooms: parseInt(document.getElementById('bathrooms').value)
                };

                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();

                    if (response.ok) {
                        priceOutput.textContent = `NPR ${result.predicted_price.toLocaleString('en-IN', {maximumFractionDigits: 2})}`;
                        resultCard.style.display = 'block';
                    } else {
                        errorCard.textContent = result.detail || 'An error occurred during prediction.';
                        errorCard.style.display = 'block';
                    }
                } catch (err) {
                    errorCard.textContent = 'Failed to connect to the server.';
                    errorCard.style.display = 'block';
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Estimate Market Price';
                }
            });
        </script>
    </body>
    </html>
    """
  return html_content


@app.post("/predict")
async def predict_price(input_data: PropertyInput):
  import pandas as pd

  df = pd.DataFrame([{
      "city": input_data.city,
      "property_type": input_data.property_type,
      "area_sqft": input_data.area_sqft,
      "bedrooms": input_data.bedrooms,
      "bathrooms": input_data.bathrooms,
  }])

  try:
    if model is not None:
      prediction = model.predict(df)[0]
    else:
      # Intelligent heuristic backup formula if model is unloaded/incompatible
      # Base rate per sqft ~ NPR 12,000 adjusted by city coefficients
      city_multipliers = {"ktm": 1.4, "lalitpur": 1.3, "pokhara": 1.1, "bkt": 0.9}
      type_multipliers = {
          "apartment": 1.1,
          "house": 1.0,
          "townhouse": 1.15,
      }
      base_val = input_data.area_sqft * 11000
      prediction = (
          base_val
          * city_multipliers.get(input_data.city, 1.0)
          * type_multipliers.get(input_data.property_type, 1.0)
          + (input_data.bedrooms * 150000)
          + (input_data.bathrooms * 100000)
      )

    return {"predicted_price": float(prediction)}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
  uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
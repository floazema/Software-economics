from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Import service modules
from modules.cost_estimation import CostEstimationService
from modules.budget_management import BudgetManagementService

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database Configuration (optional, as we are not using it actively)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/taskbuddy_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize services
cost_service = CostEstimationService()
budget_service = BudgetManagementService()

@app.route('/api')
def index():
    """Root endpoint to welcome users to the API."""
    return jsonify({
        "message": "Welcome to the TaskBuddy Economic Analysis API",
        "version": "1.0.0",
        "modules": ["cost-estimation", "budget-management"]
    })

# --- Cost Estimation Endpoints ---
@app.route('/api/cost-estimation/all', methods=['POST'])
def estimate_all():
    data = request.get_json()
    result = cost_service.compare_all_methods(data)
    return jsonify(result)

# --- Budget Management Endpoints ---
@app.route('/api/budget/financial-metrics', methods=['POST'])
def get_financial_metrics():
    data = request.get_json()
    initial_investment = data.get('initial_investment', 25000)
    cash_flows = data.get('cash_flows', [1000] * 24)
    discount_rate = data.get('discount_rate', 0.1)
    
    result = budget_service.calculate_financial_metrics(initial_investment, cash_flows, discount_rate)
    return jsonify(result)

if __name__ == '__main__':
    # Bind to 0.0.0.0 to make the server accessible from the local network
    app.run(host='0.0.0.0', debug=True, port=5000) 
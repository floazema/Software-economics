import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import math

class CostEstimationService:
    """
    Provides services for estimating project costs using various models.
    """
    def __init__(self):
        """Initializes the service and sets up models."""
        # COCOMO model coefficients
        self.cocomo_coefficients = {
            'organic': {'a': 2.4, 'b': 1.05},
            'semi_detached': {'a': 3.0, 'b': 1.12},
            'embedded': {'a': 3.6, 'b': 1.20}
        }
        
        # Function Point weights (simplified)
        self.fp_weights = {'simple': 3, 'average': 4, 'complex': 6}
        
        # Linear Regression Model
        self._regression_model = self._train_linear_regression_model()

    def _train_linear_regression_model(self):
        """Generates synthetic data and trains a simple regression model."""
        np.random.seed(42)
        n_projects = 50
        data = {
            'loc_thousands': np.random.randint(5, 100, n_projects),
            'complexity_score': np.random.uniform(1, 10, n_projects),
        }
        df = pd.DataFrame(data)
        df['cost_euros'] = (df['loc_thousands'] * 2000 + 
                            df['complexity_score'] * 3000 + 
                            np.random.normal(0, 5000, n_projects))
        
        X = df[['loc_thousands', 'complexity_score']]
        y = df['cost_euros']
        model = LinearRegression()
        model.fit(X, y)
        return model

    def calculate_cocomo(self, loc, project_type='semi_detached'):
        """Calculates cost using a simplified COCOMO model."""
        if loc <= 0:
            return {'error': 'Lines of code must be positive.'}
            
        kloc = loc / 1000
        coeffs = self.cocomo_coefficients.get(project_type, self.cocomo_coefficients['semi_detached'])
        
        effort_pm = coeffs['a'] * (kloc ** coeffs['b'])
        total_cost = effort_pm * 6000  # Assuming €6,000 per person-month
        
        return {
            'method': 'COCOMO',
            'effort_person_months': round(effort_pm, 2),
            'total_cost_euros': round(total_cost, 2)
        }
    
    def calculate_function_points(self, function_points, complexity='average'):
        """Calculates cost using Function Points."""
        if function_points <= 0:
            return {'error': 'Function points must be positive.'}
            
        cost_per_fp = self.fp_weights.get(complexity, 4) * 30 # Simplified cost driver
        total_cost = function_points * cost_per_fp
        
        return {
            'method': 'Function Points',
            'total_cost_euros': round(total_cost, 2)
        }
    
    def calculate_expert_judgment(self, estimates):
        """Calculates cost using expert judgment (PERT-like)."""
        if not isinstance(estimates, list) or len(estimates) < 3:
            return {'error': 'Provide at least three estimates: optimistic, most likely, pessimistic.'}
        
        optimistic, most_likely, pessimistic = estimates[0], estimates[1], estimates[2]
        
        # PERT estimation
        weighted_avg = (optimistic + 4 * most_likely + pessimistic) / 6
        
        return {
            'method': 'Expert Judgment (PERT)',
            'total_cost_euros': round(weighted_avg, 2)
        }
    
    def calculate_linear_regression(self, loc_thousands, complexity_score):
        """Predicts cost using the trained linear regression model."""
        input_data = np.array([[loc_thousands, complexity_score]])
        predicted_cost = self._regression_model.predict(input_data)[0]
        
        return {
            'method': 'Linear Regression',
            'total_cost_euros': round(max(5000, predicted_cost), 2)
        }

    def compare_all_methods(self, project_data):
        """Compares results from all available estimation methods."""
        results = {}
        
        # Unpack data with defaults
        loc = project_data.get('loc', 8000)
        fp = project_data.get('function_points', 350)
        estimates = project_data.get('expert_estimates', [20000, 25000, 40000])
        complexity = project_data.get('complexity_score', 5)

        # Run all models
        results['cocomo'] = self.calculate_cocomo(loc)
        results['function_points'] = self.calculate_function_points(fp)
        results['expert_judgment'] = self.calculate_expert_judgment(estimates)
        results['linear_regression'] = self.calculate_linear_regression(loc / 1000, complexity)
        
        # Calculate a final weighted average
        costs = {k: v['total_cost_euros'] for k, v in results.items() if 'total_cost_euros' in v}
        if costs:
            # Excluding outliers might be a good idea in a real app
            final_estimate = np.mean(list(costs.values()))
            results['final_recommendation'] = round(final_estimate, 2)

        return results 
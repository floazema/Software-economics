import numpy as np
import numpy_financial as npf
import pandas as pd
from scipy.optimize import fsolve
import math

class BudgetManagementService:
    """
    Provides services for financial calculations and budget management.
    """
    def __init__(self):
        self.default_discount_rate = 0.10
        
    def calculate_npv(self, cash_flows, discount_rate):
        """Calculate Net Present Value"""
        npv = 0
        for t, cash_flow in enumerate(cash_flows):
            npv += cash_flow / ((1 + discount_rate) ** t)
        return npv
    
    def calculate_irr(self, cash_flows, max_iterations=1000):
        """Calculate Internal Rate of Return using Newton-Raphson method"""
        def npv_function(rate):
            return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cash_flows))
        
        try:
            # Initial guess
            irr = fsolve(npv_function, 0.1)[0]
            
            # Validate the result
            if abs(npv_function(irr)) < 1e-6 and -0.99 < irr < 10:
                return irr
            else:
                return None
        except:
            return None
    
    def calculate_payback_period(self, initial_investment, cash_flows):
        """Calculate Payback Period"""
        cumulative_cash_flow = -abs(initial_investment)
        
        for month, cash_flow in enumerate(cash_flows[1:], 1):  # Skip initial investment
            cumulative_cash_flow += cash_flow
            if cumulative_cash_flow >= 0:
                # Linear interpolation for exact payback period
                previous_cumulative = cumulative_cash_flow - cash_flow
                fraction = abs(previous_cumulative) / cash_flow
                return month - 1 + fraction
        
        return None  # Payback period not reached
    
    def calculate_roi(self, initial_investment, total_return):
        """Calculate Return on Investment"""
        if initial_investment == 0:
            return None
        return (total_return - initial_investment) / initial_investment * 100
    
    def calculate_financial_metrics(self, initial_investment, cash_flows, discount_rate=None):
        """
        Calculates key financial metrics: NPV, IRR, ROI, and Payback Period.
        """
        if discount_rate is None:
            discount_rate = self.default_discount_rate
        
        # Ensure initial investment is negative for calculations
        if initial_investment > 0:
            initial_investment = -initial_investment
            
        full_cash_flow = [initial_investment] + cash_flows

        # --- Net Present Value (NPV) ---
        npv = npf.npv(discount_rate, full_cash_flow)

        # --- Internal Rate of Return (IRR) ---
        try:
            irr = npf.irr(full_cash_flow)
        except:
            # IRR can fail to converge
            irr = None

        # --- Return on Investment (ROI) ---
        total_return = sum(cash_flows)
        roi = ((total_return + initial_investment) / abs(initial_investment)) * 100 if initial_investment != 0 else 0

        # --- Payback Period ---
        payback_period = None
        cumulative_cash_flow = 0
        for i, cash_flow in enumerate(full_cash_flow):
            cumulative_cash_flow += cash_flow
            if cumulative_cash_flow >= 0:
                # Find the month where it turns positive
                payback_period = i
                break
        
        return {
            'npv': round(npv, 2),
            'irr_percent': round(irr * 100, 2) if irr is not None else None,
            'roi_percent': round(roi, 2),
            'payback_period_months': payback_period
        }
    
    def _get_investment_decision(self, npv, irr, payback_period, profitability_index):
        """Provide investment decision based on financial metrics"""
        recommendations = []
        overall_score = 0
        
        # NPV analysis
        if npv > 0:
            recommendations.append("NPV is positive - project adds value")
            overall_score += 2
        else:
            recommendations.append("NPV is negative - project destroys value")
            overall_score -= 2
        
        # IRR analysis
        if irr is not None:
            if irr > 0.15:  # 15% threshold
                recommendations.append(f"IRR ({irr:.1f}%) exceeds minimum threshold")
                overall_score += 2
            elif irr > 0.10:
                recommendations.append(f"IRR ({irr:.1f}%) is acceptable")
                overall_score += 1
            else:
                recommendations.append(f"IRR ({irr:.1f}%) is below threshold")
                overall_score -= 1
        
        # Payback period analysis
        if payback_period is not None:
            if payback_period <= 12:
                recommendations.append(f"Quick payback period ({payback_period:.1f} months)")
                overall_score += 1
            elif payback_period <= 24:
                recommendations.append(f"Reasonable payback period ({payback_period:.1f} months)")
            else:
                recommendations.append(f"Long payback period ({payback_period:.1f} months)")
                overall_score -= 1
        
        # Profitability Index
        if profitability_index > 1.2:
            recommendations.append("High profitability index - excellent value creation")
            overall_score += 1
        elif profitability_index > 1.0:
            recommendations.append("Positive profitability index - value creation")
        else:
            recommendations.append("Poor profitability index - value destruction")
            overall_score -= 1
        
        # Overall decision
        if overall_score >= 3:
            decision = "HIGHLY RECOMMENDED"
        elif overall_score >= 1:
            decision = "RECOMMENDED"
        elif overall_score >= -1:
            decision = "CONDITIONAL - Requires further analysis"
        else:
            decision = "NOT RECOMMENDED"
        
        return {
            'decision': decision,
            'score': overall_score,
            'recommendations': recommendations,
            'risk_level': 'Low' if overall_score >= 2 else 'Medium' if overall_score >= 0 else 'High'
        }
    
    def track_budget_variance(self, planned_budget, actual_costs):
        """
        Tracks budget variance across different project phases.
        planned_budget and actual_costs are dicts: {'phase': cost}
        """
        variance_analysis = {}
        total_planned = sum(planned_budget.values())
        total_actual = sum(actual_costs.values())

        for phase, planned_cost in planned_budget.items():
            actual_cost = actual_costs.get(phase, 0)
            variance = planned_cost - actual_cost
            variance_percent = (variance / planned_cost * 100) if planned_cost > 0 else 0
            
            status = 'Under Budget'
            if variance < 0:
                status = 'Over Budget'
            elif variance == 0:
                status = 'On Budget'
                
            variance_analysis[phase] = {
                'planned': planned_cost,
                'actual': actual_cost,
                'variance': variance,
                'variance_percent': round(variance_percent, 2),
                'status': status
            }
            
        # Overall project performance
        total_variance = total_planned - total_actual
        total_variance_percent = (total_variance / total_planned * 100) if total_planned > 0 else 0
        
        # Estimate at Completion (EAC) - simple version
        eac = total_actual / (sum(actual_costs.values()) / total_planned) if total_planned > 0 and sum(actual_costs.values()) > 0 else total_planned

        return {
            'phase_analysis': variance_analysis,
            'summary': {
                'total_planned': total_planned,
                'total_actual': total_actual,
                'total_variance': round(total_variance, 2),
                'total_variance_percent': round(total_variance_percent, 2),
                'estimate_at_completion': round(eac, 2)
            }
        }
    
    def forecast_cash_flow(self, initial_revenue, growth_rate, expenses, months):
        """Forecast future cash flows"""
        forecast = []
        current_revenue = initial_revenue
        
        for month in range(1, months + 1):
            # Apply growth rate
            if month > 1:
                current_revenue *= (1 + growth_rate / 12)  # Monthly growth
            
            # Calculate monthly expenses (can be fixed or variable)
            if isinstance(expenses, dict):
                monthly_expenses = sum(expenses.values())
            else:
                monthly_expenses = expenses
            
            net_cash_flow = current_revenue - monthly_expenses
            
            forecast.append({
                'month': month,
                'revenue': round(current_revenue, 2),
                'expenses': round(monthly_expenses, 2),
                'net_cash_flow': round(net_cash_flow, 2),
                'cumulative_cash_flow': round(sum(item['net_cash_flow'] for item in forecast), 2)
            })
        
        return {
            'forecast': forecast,
            'total_revenue': round(sum(item['revenue'] for item in forecast), 2),
            'total_expenses': round(sum(item['expenses'] for item in forecast), 2),
            'total_net_cash_flow': round(sum(item['net_cash_flow'] for item in forecast), 2)
        } 
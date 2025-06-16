-- TaskBuddy Database Schema
-- Database for the economic analysis tool

-- To create the database and user, run as a superuser:
-- CREATE DATABASE taskbuddy_db;
-- CREATE USER taskbuddy_user WITH ENCRYPTED PASSWORD 'your_secure_password';
-- GRANT ALL PRIVILEGES ON DATABASE taskbuddy_db TO taskbuddy_user;

-- Main table for projects
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    budget NUMERIC(15, 2),
    status VARCHAR(50) DEFAULT 'planning', -- e.g., planning, active, completed, cancelled
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for cost estimations from various models
CREATE TABLE IF NOT EXISTS cost_estimations (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    method VARCHAR(50) NOT NULL, -- e.g., cocomo, function_points, expert_judgment
    estimated_cost NUMERIC(15, 2),
    parameters JSONB, -- Store method-specific input parameters
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for budget tracking across project phases
CREATE TABLE IF NOT EXISTS budget_tracking (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    phase VARCHAR(100) NOT NULL,
    planned_cost NUMERIC(15, 2),
    actual_cost NUMERIC(15, 2),
    tracking_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for calculated financial metrics
CREATE TABLE IF NOT EXISTS financial_metrics (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    roi NUMERIC(10, 4),
    npv NUMERIC(15, 2),
    irr NUMERIC(10, 4),
    payback_period_months NUMERIC(6, 2),
    calculation_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing results from risk analyses
CREATE TABLE IF NOT EXISTS risk_analyses (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL, -- e.g., sensitivity, monte_carlo
    results JSONB, -- Store complex results like distributions or sensitivity plots
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for historical project data used for regression models
CREATE TABLE IF NOT EXISTS historical_projects (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(255),
    team_size INTEGER,
    duration_months INTEGER,
    complexity_score NUMERIC(5, 2),
    loc_thousands INTEGER,
    final_cost NUMERIC(15, 2),
    technology_stack VARCHAR(255),
    project_type VARCHAR(100),
    success_rating NUMERIC(3, 2), -- e.g., 0.0 to 1.0
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- --- Indexes for Performance ---
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_cost_estimations_project_id ON cost_estimations(project_id);
CREATE INDEX IF NOT EXISTS idx_budget_tracking_project_id ON budget_tracking(project_id);
CREATE INDEX IF NOT EXISTS idx_financial_metrics_project_id ON financial_metrics(project_id);
CREATE INDEX IF NOT EXISTS idx_risk_analyses_project_id ON risk_analyses(project_id);

-- --- Views for Simplified Queries ---
CREATE OR REPLACE VIEW project_summary AS
SELECT 
    p.id,
    p.name,
    p.budget,
    p.status,
    (SELECT AVG(ce.estimated_cost) FROM cost_estimations ce WHERE ce.project_id = p.id) as avg_estimated_cost,
    (SELECT SUM(bt.actual_cost) FROM budget_tracking bt WHERE bt.project_id = p.id) as total_actual_cost,
    (p.budget - (SELECT SUM(bt.actual_cost) FROM budget_tracking bt WHERE bt.project_id = p.id)) as remaining_budget
FROM projects p;

-- --- Sample Data for Demonstration ---
-- Insert a sample project
INSERT INTO projects (name, description, budget) VALUES
('TaskBuddy Mobile App', 'A mobile app for task management', 25000.00)
ON CONFLICT (name) DO NOTHING;

-- Insert sample historical data for regression analysis
INSERT INTO historical_projects (project_name, team_size, duration_months, complexity_score, loc_thousands, final_cost, project_type, success_rating) VALUES
('E-commerce Platform', 4, 6, 3.5, 12, 35000, 'mobile_app', 0.85),
('CRM Dashboard', 6, 8, 4.2, 25, 68000, 'web_app', 0.92),
('Inventory System', 3, 4, 2.8, 8, 22000, 'mobile_app', 0.88)
ON CONFLICT (project_name) DO NOTHING; 
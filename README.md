# FINESE ONE

== ACCESS LINK: https://huggingface.co/spaces/Jack-ki1/finese_data_1

A comprehensive, modular data analysis platform with AI-powered insights, automated cleaning, modeling, and export capabilities.

## 📊 Overview

FINESE is a powerful data intelligence platform that transforms raw datasets into actionable insights without writing code. Whether you're a data analyst, scientist, or business decision-maker, FINESE provides a seamless workflow for exploring, cleaning, analyzing, and presenting data.

The application features an intuitive interface with multiple tabs for different data analysis tasks, as shown in the screenshots below:

![Data Loading Interface](app_image_1.png)
*Figure 1: Data loading interface with upload options*

![Data Review Dashboard](app_image_2.png)
*Figure 2: Data review dashboard showing dataset statistics and snapshot*

![Data Cleaning Recommendations](app_image_3.png)
*Figure 3: Unified data cleaning and typing recommendations*

## 🔑 Key Features

- **Data Cleaning & Preprocessing**: Handle missing values, detect anomalies, convert data types
- **Interactive Visualizations**: Create charts, pivot tables, and dashboards with drag-and-drop simplicity
- **Data Quality Assessment**: Comprehensive health scoring with AI-powered recommendations
- **Machine Learning Pipeline**: Feature engineering, model training, and evaluation
- **AI-Powered Chatbot**: Natural language interface for data analysis
- **Professional Reporting**: Export to PDF, PowerPoint, and Markdown formats
- **Theme Customization**: Light/dark mode with elegant UI design

## 🚀 Getting Started

1. Upload your dataset (CSV, Excel, JSON, etc.) via the "Browse files" button or by dragging and dropping files
2. Explore your data using the Review tab which shows:
   - Dataset statistics (rows, columns, nulls, duplicates, memory usage)
   - Data snapshot with first and last 10 rows
   - Column summary with data types and missing values
3. Clean and preprocess your data using the Smart Cleanup feature that identifies potential issues like:
   - Numeric characters stored as text
   - Date fields stored as text
4. Create visualizations and pivot tables
5. Use the AI chatbot to ask questions about your data
6. Export your results in various formats

## 🧰 Features & Modules

### 1. Data Review
- Data snapshot (first/last 10 rows)
- Column summary with data types and missing values
- Data health scorecard with comprehensive metrics
- Completeness visualization and missing data heatmap

### 2. Data Cleaning
- Smart cleanup suggestions
- Intelligent data type conversion
- Preview and apply cleaning operations
- Automatic detection of numeric characters stored as text
- Date format recognition and conversion

### 3. Charts & Pivot Tables
- Multiple chart types (bar, line, scatter, histogram, etc.)
- Interactive pivot table builder
- Drag-and-drop interface for data visualization

### 4. AI Chatbot
- Natural language queries about your data
- Option to use external AI providers (OpenAI, Anthropic, Google)
- Built-in rule-based engine for common questions

### 5. Export
- Export filtered data to CSV
- Generate professional reports in PDF and PowerPoint
- Markdown report generation for documentation
- Full executive bundle with all formats

### 6. Pre-Modelling
- Target variable setup
- Advanced exploratory data analysis
- Feature-target relationship analysis
- Data quality and risk assessment

### 7. Model Training & Usage
- Quick model training with various algorithms
- Performance evaluation metrics
- Feature importance analysis
- Model export and code generation

## 🛠️ Technology Stack

- **Frontend**: Streamlit - For building the interactive web interface
- **Data Processing**: pandas, NumPy
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Machine Learning**: scikit-learn, XGBoost, LightGBM, CatBoost
- **Reporting**: ReportLab, python-pptx
- **AI Integration**: OpenAI API, Anthropic API

## 🔧 Configuration

For AI features, set the following environment variables in the Space settings:

- `OPENAI_API_KEY` for OpenAI features
- `ANTHROPIC_API_KEY` for Anthropic features
- `GOOGLE_API_KEY` for Google Gemini features

## 📦 Requirements

All requirements are specified in the [requirements.txt](requirements.txt) file.
"# FINESE_1" 

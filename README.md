# FINESE - Smart Data Explorer Pro

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://finese.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-310/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/Jack-ki1/finese_data_1)

**FINESE** (Fast Intelligent NEural Statistical Engine) is a comprehensive, modular data analysis platform with AI-powered insights, automated cleaning, modeling, and export capabilities. Transform raw datasets into actionable insights without writing code.

## 🎯 Live Demo

Try FINESE online: [https://huggingface.co/spaces/Jack-ki1/finese_data_1](https://huggingface.co/spaces/Jack-ki1/finese_data_1)

## 📊 Overview

FINESE is a powerful data intelligence platform that transforms raw datasets into actionable insights without writing code. Whether you're a data analyst, scientist, or business decision-maker, FINESE provides a seamless workflow for exploring, cleaning, analyzing, and presenting data.

The application features an intuitive interface with multiple tabs for different data analysis tasks:

| Data Loading Interface | Data Review Dashboard |
|------------------------|-----------------------|
| ![Data Loading Interface](app_image_1.png) | ![Data Review Dashboard](app_image_2.png) |
| Upload and manage datasets | Explore data statistics and samples |

| Data Cleaning Recommendations |
|------------------------------|
| ![Data Cleaning Recommendations](app_image_3.png) |
| Intelligent cleaning and type conversion suggestions |

## ✨ Key Features

### 🔍 **Intelligent Data Review**
- Automatic data profiling and quality assessment
- Visual data summaries with key metrics
- Missing value and duplicate detection
- Interactive data exploration
- Comprehensive data health scoring

### 🧹 **Smart Data Cleaning**
- Automated type detection and conversion suggestions
- Bulk apply cleaning transformations
- Side-by-side preview of changes
- Reversible cleaning operations
- Missingness pattern analysis

### 📊 **Interactive Charts & Visualizations**
- Drag-and-drop chart builder
- Multiple visualization types (bar, line, scatter, histograms, heatmaps, pivot tables)
- Dynamic filtering and drill-down capabilities
- Export charts in multiple formats
- Correlation and outlier analysis

### 💬 **AI-Powered Chatbot**
- Natural language queries about your data
- Supports OpenAI, Anthropic, and Google Gemini APIs
- Rule-based engine for offline use
- Automated insight generation

### 🧠 **Machine Learning Studio**
- Automated feature engineering
- Supervised and unsupervised learning
- Model selection and comparison
- Hyperparameter optimization
- Model interpretability and SHAP explanations
- Export models and production-ready code

### 🗣️ **SQL Query Interface**
- Query your data using standard SQL syntax
- Schema explorer for easy column discovery
- Visual query builder
- Download query results in multiple formats
- Powered by DuckDB for fast analytics

### 📤 **Comprehensive Export Options**
- Export cleaned data in multiple formats (CSV, Excel, JSON)
- Professional PDF and PowerPoint reports
- Model export (joblib, pickle)
- Production-ready Python code generation
- Executable report bundles

### 🔄 **Dataset Context Management**
- Seamless handling of large datasets
- Real-time filtering and transformation
- Memory-efficient processing
- Consistent data state across tabs

## 🛠️ Tech Stack

- **Frontend**: Streamlit (1.28+)
- **Data Processing**: Pandas, NumPy, DuckDB
- **Visualization**: Plotly, Matplotlib, Seaborn
- **ML**: Scikit-learn, XGBoost, LightGBM, CatBoost
- **Reports**: ReportLab, Python-PPTX
- **AI**: OpenAI, Anthropic, Google Gemini APIs
- **Architecture**: Modular service-oriented design

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip package manager
- At least 4GB RAM (recommended 8GB+ for large datasets)
- Internet connection (for AI features and initial setup)

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/finese.git
   cd finese
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

### Hugging Face Spaces Setup

To deploy on Hugging Face Spaces:

1. Create a new Space with the following configuration:
   - Framework: Streamlit
   - Hardware: CPU Basic (or higher for larger datasets)
   - Enable "Allow Caching"

2. Add these files to your Space:
   - `app.py` - Main application file
   - `requirements.txt` - Dependencies
   - `README.md` - Documentation
   - All folders: `tabs/`, `services/`, `utils/`, `core/`, `config.py`, `state.py`

3. Hugging Face will automatically install dependencies and launch the app

### Configuration

For AI features, create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key
```

## 📁 Project Structure

```
FINESS/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── config.py             # Global configuration
├── state.py              # Session state defaults
├── logging_config.py     # Logging configuration
├── core/                 # Core data structures
│   ├── __init__.py
│   └── dataset_context.py # Dataset management
├── services/             # Business logic modules
│   ├── __init__.py
│   ├── chart_service.py
│   ├── cleaning_service.py
│   ├── health_service.py
│   ├── llm_service.py
│   ├── ml_service.py
│   ├── profiling_service.py
│   └── sql_service.py
├── tabs/                 # UI components
│   ├── __init__.py
│   ├── charts.py
│   ├── cleaning.py
│   ├── export.py
│   ├── make_a_model.py
│   ├── review.py
│   ├── sql_query.py
│   └── chatbot.py
└── utils/                # Utility functions
    ├── __init__.py
    └── data_utils.py
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure to update tests as appropriate and follow our coding standards.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/your-username/finese/issues) page
2. Search for similar problems
3. Create a new issue if needed, including:
   - Your Python version
   - Operating system
   - Steps to reproduce
   - Error message

## 🙏 Acknowledgments

- DuckDB for fast analytical SQL processing
- Streamlit for the awesome web framework
- Plotly for interactive visualizations
- The open-source community for countless invaluable packages

---

<div align="center">

**Made with ❤️ for the data science community**

⭐ Star this repo if you find it helpful!

</div>
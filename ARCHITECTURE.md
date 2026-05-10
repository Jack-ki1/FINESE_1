# FINESE Architecture Documentation

## Overview

FINESE is built using a modular, service-oriented architecture that separates concerns between UI components, business logic, and utility functions. This design makes the application scalable, maintainable, and easy to extend.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Layer      │    │  Service Layer  │    │   Utils Layer   │
│                 │    │                 │    │                 │
│  tabs/          │◄──►│  services/      │◄──►│  utils/         │
│  app.py         │    │  core/          │    │  config.py     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                       ┌─────────────────┐
                       │  External APIs  │
                       │                 │
                       │  OpenAI         │
                       │  Anthropic      │
                       │  Google Gemini  │
                       │  DuckDB         │
                       └─────────────────┘
```

## Component Breakdown

### 1. UI Layer (`tabs/`)

The UI layer consists of individual tabs that handle different aspects of data analysis:

- **`review.py`**: Data overview and quality assessment
- **`cleaning.py`**: Data cleaning and type conversion
- **`charts.py`**: Visualization and chart creation
- **`chatbot.py`**: AI-powered data querying
- **`make_a_model.py`**: Machine learning model creation
- **`export.py`**: Data export and report generation
- **`sql_query.py`**: SQL-based data querying

Each tab receives a `DatasetContext` object which manages the state of the data being analyzed.

### 2. Service Layer (`services/`)

The service layer contains business logic for specific domains:

- **`chart_service.py`**: Handles chart generation and visualization logic
- **`cleaning_service.py`**: Implements data cleaning algorithms
- **`health_service.py`**: Calculates data quality metrics
- **`llm_service.py`**: Manages interactions with large language models
- **`ml_service.py`**: Handles machine learning workflows
- **`profiling_service.py`**: Performs data profiling
- **`sql_service.py`**: Executes SQL queries against data

### 3. Core Components (`core/`)

- **`dataset_context.py`**: Centralized data management class that maintains the state of the dataset across the application

### 4. Utilities (`utils/`)

- **`data_utils.py`**: Common data manipulation functions
- **`ui_utils.py`**: UI helper functions and components
- **`logging_config.py`**: Centralized logging configuration

### 5. Configuration

- **`config.py`**: Application-wide constants and configuration
- **`state.py`**: Default session state values

## Data Flow

1. **Data Input**: User uploads data via sidebar → stored in `st.session_state.work_df` as a `DatasetContext`
2. **Processing**: Each tab receives the `DatasetContext` and applies transformations
3. **Filtering**: Global filters are applied via `get_filtered_data()` function
4. **Output**: Results are displayed and can be exported via the export tab

## Session State Management

The application uses Streamlit's session state to persist data across reruns:

- `work_df`: Main working dataset (DatasetContext)
- `data_loaded`: Flag indicating if data has been loaded
- `filtered_data`: Cached filtered view of the data
- Various filter settings for date ranges, categorical selections, etc.

## Key Design Principles

1. **Modularity**: Each feature is isolated in its own module
2. **Consistency**: Shared UI components and consistent data handling
3. **Performance**: Caching mechanisms to avoid recomputation
4. **Extensibility**: Easy to add new tabs or services without disrupting existing functionality

## Extending the Application

To add a new feature:

1. Create a new file in the `tabs/` directory with a `render_tab_name()` function
2. Add the tab to the main `app.py` file in the tabs array
3. If needed, create a new service in the `services/` directory
4. Update the UI to maintain consistency with existing components

## Error Handling

The application implements comprehensive error handling at multiple levels:

- UI level: Graceful degradation when optional dependencies aren't available
- Service level: Specific error handling for API calls and data operations
- Global level: Catch-all exception handlers to maintain application stability

## Performance Optimizations

- Lazy loading of tab contents to reduce memory usage
- Caching of expensive computations
- Row limits on large datasets to maintain responsiveness
- Efficient data filtering to avoid copying large DataFrames unnecessarily
# 📊 Attendance Analyzer

A powerful web-based application designed to help teaching faculty analyze students' attendance data efficiently using AI-powered Excel sheet processing.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Gradio](https://img.shields.io/badge/gradio-web_interface-orange.svg)
![UV](https://img.shields.io/badge/uv-package_manager-green.svg)

## ✨ Features

- **🤖 AI-Powered Analysis**: Uses Google's Gemini AI to automatically detect header structure and subject information in Excel files
- **📈 Attendance Tracking**: Analyzes student attendance percentages across multiple subjects
- **🎯 Low Attendance Detection**: Identifies students falling below specified attendance thresholds
- **📊 Overall Percentage Calculation**: Automatically computes overall attendance percentages
- **🌐 Web Interface**: User-friendly Gradio-based web application
- **📋 Flexible Excel Support**: Handles complex Excel sheets with multi-level headers

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv package manager](https://docs.astral.sh/uv/) (recommended) or pip
- Google Gemini API key

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd attendance-analyzer
   ```

2. **Set up environment** (using uv):
   ```bash
   make install
   ```

3. **Set up your Gemini API key**:
   ```bash
   export GEMINI_API_KEY="your-gemini-api-key-here"
   ```
   
   Or create a `.env` file:
   ```
   GEMINI_API_KEY=your-gemini-api-key-here
   ```

4. **Run the application**:
   ```bash
   make run
   ```
   
   The web interface will be available at `http://localhost:7860`

## 📖 Usage

### Web Interface

1. **Upload Excel File**: Click "Upload Excel" and select your attendance spreadsheet (.xlsx or .xls)
2. **Set Minimum Percentage**: Enter the minimum attendance percentage threshold (e.g., 75)
3. **Submit**: Click "Submit" to process the file
4. **View Results**: 
   - See the processed attendance data in the preview table
   - Select subjects from the dropdown to view students with low attendance
   - Review detailed attendance information for each subject

### Excel File Format

The application works with Excel files containing:
- Student names in the first column
- Attendance percentages in columns with "%" in the header
- Subject headers
- Multi-level headers are supported

### Prompts
The prompt currently works for ayurvedic colleges. Prompt can be modified to suit your required category of college.
Modify the function ```get_prompt``` in the file ```helper.py``` accordingly.

**Example Excel Structure**:
```
| Student Name | Subject 1 % | Subject 2 % | Subject 3 % |
|--------------|-------------|-------------|-------------|
| John Doe     | 85.5        | 92.0        | 78.3        |
| Jane Smith   | 70.2        | 88.5        | 95.1        |
```

## 🛠️ Development

### Available Make Commands

```bash
# View all available commands
make help

# Development setup
make install            # Install dependencies

# Running the application
make run               # Start the Gradio web interface

# Code quality
make format            # Format code with ruff
make lint              # Run ruff linter
make check             # Run both format and lint checks

# Maintenance
make clean             # Clean cache and temporary files
make update            # Update all dependencies
make sync              # Sync virtual environment
```

### Project Structure

```
attendance-analyzer/
├── main.py              # Main Gradio application
├── helper.py            # Gemini AI integration helpers
├── helper_analyze.py    # Attendance analysis functions
├── pyproject.toml       # Project configuration and dependencies
├── uv.lock             # Lock file for dependencies
├── Makefile            # Development automation
└── README.md           # This file
```

### Key Components

- **`main.py`**: Contains the Gradio web interface and main application logic
- **`helper.py`**: Handles communication with Google Gemini API for header detection
- **`helper_analyze.py`**: Core attendance analysis functions including:
  - Percentage normalization
  - Overall percentage calculation
  - Low attendance student identification

## 🔧 Configuration

### Environment Variables

- `GEMINI_API_KEY`: Required for AI-powered header detection and analysis

### Dependencies

Main dependencies (see `pyproject.toml` for complete list):
- **gradio**: Web interface framework
- **pandas**: Data manipulation and analysis
- **openpyxl**: Excel file processing
- **rich**: Enhanced console output
- **ruff**: Code formatting and linting
- **requests**: HTTP client for API calls

## 🆘 Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY environment variable not set"**
   - Ensure you have set the `GEMINI_API_KEY` environment variable
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. **"Failed to read file" errors**
   - Ensure the Excel file is not corrupted
   - Check that the file contains the expected structure with student names and percentage columns

3. **"Could not determine header rows" errors**
   - Verify that your Excel file has proper headers
   - Ensure subject names are present

4. **Application won't start**
   - Run `make clean` to clear cache
   - Reinstall dependencies with `make install`
   - Check Python version (requires 3.11+)

### Getting Help

- Check the console output for detailed error messages
- Ensure all dependencies are properly installed
- Verify your Excel file format matches the expected structure

---

**Made with ❤️ for educators to efficiently analyze student attendance data.**

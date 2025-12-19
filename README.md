# 🩺 ABG Interpreter - Medical Training Tool

A comprehensive Streamlit application for step-by-step Arterial Blood Gas (ABG) interpretation using AI-powered analysis with Claude API.

## Features

- 📊 **Multiple Input Methods**: Upload ABG reports (images/PDFs) or enter values manually
- 🤖 **AI-Powered Analysis**: Uses Claude API for intelligent ABG interpretation
- 📚 **Educational Focus**: Step-by-step analysis following the standard 5-step approach
- 🔍 **Automatic Value Extraction**: Extract ABG values from uploaded reports using vision AI
- 📈 **Clinical Correlation**: Include patient history for contextualized analysis
- 📥 **Report Download**: Export analysis reports for reference

## 5-Step ABG Interpretation Approach

1. **pH Assessment** - Identify acidaemia or alkalaemia
2. **Primary Disturbance** - Determine if respiratory or metabolic
3. **Anion Gap Calculation** - For metabolic acidosis cases
4. **Compensation Assessment** - Check for appropriate compensation or mixed disorders
5. **Oxygenation & A-a Gradient** - Evaluate gas exchange

## Installation

### Prerequisites

- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com))

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/abg-interpreter.git
cd abg-interpreter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

## Deployment

### Deploy to Streamlit Cloud (Recommended)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository, branch, and `app.py`
6. Click "Deploy"

### Deploy to Heroku

1. Create `Procfile`:
```
web: sh setup.sh && streamlit run app.py
```

2. Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Deploy to Railway

1. Create `railway.toml`:
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "streamlit run app.py"
```

2. Connect your GitHub repo at [railway.app](https://railway.app)

## Usage

### 1. Enter API Key

- Get your Claude API key from [Anthropic Console](https://console.anthropic.com)
- Enter it in the sidebar

### 2. Input ABG Data

**Option A: Upload Report**
- Upload an image or PDF of the ABG report
- Click "Extract Values" to automatically parse values

**Option B: Manual Entry**
- Enter each ABG parameter manually
- Normal ranges are displayed for reference

### 3. Add Clinical Information (Optional)

- Provide patient history, symptoms, or relevant clinical details
- This helps contextualize the analysis

### 4. Analyze

- Click "Analyze ABG"
- View the comprehensive step-by-step analysis
- Download the report for your records

## Normal Ranges

| Parameter | Normal Range |
|-----------|-------------|
| pH | 7.35 - 7.45 |
| pCO₂ | 4.5 - 6.0 kPa |
| HCO₃⁻ | 22 - 28 mmol/L |
| pO₂ | 11 - 13 kPa |
| Base Excess | -2 to +2 mmol/L |
| Anion Gap | 8 - 16 mmol/L |
| Na⁺ | 135 - 145 mmol/L |
| Cl⁻ | 98 - 107 mmol/L |

## API Information

This application uses the **Claude Sonnet 4** model for analysis. You'll need:

- An Anthropic API account
- Sufficient API credits
- Your API key (keep it secure!)

**Cost Estimate**: Each analysis costs approximately $0.01-0.03 depending on complexity.

## Educational Use

This tool is designed for:
- Medical students learning ABG interpretation
- Junior doctors/residents in training
- Healthcare professionals reviewing acid-base disorders
- Medical educators teaching clinical chemistry

**⚠️ Important**: This tool is for **educational purposes only**. Always verify clinical decisions with qualified healthcare professionals.

## Security Notes

- **Never commit API keys** to version control
- Use environment variables for production deployment
- Consider implementing rate limiting for public deployments
- Add authentication if deploying for institutional use

## Environment Variables (Production)

For production deployment, set these environment variables:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

Or create a `.streamlit/secrets.toml` file:
```toml
ANTHROPIC_API_KEY = "your_api_key_here"
```

## Troubleshooting

**Issue**: "API key not found"
- Ensure you've entered the API key in the sidebar
- Check that your API key is valid

**Issue**: "Failed to extract values"
- Try manual entry instead
- Ensure the uploaded image is clear and readable
- Check that values are in standard units

**Issue**: "Analysis timeout"
- Check your internet connection
- Verify your API key has sufficient credits
- Try again with a simpler query

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on standard ABG interpretation guidelines from BMJ
- Built with Streamlit and Claude AI
- Designed for medical education and training

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

## Disclaimer

This application is intended for educational and training purposes only. It should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for clinical decisions.

---

**Made with ❤️ for medical education**

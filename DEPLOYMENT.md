# Deployment Guide for LUMEN Germany Market Entry Simulator

This guide provides detailed instructions for deploying the LUMEN Germany Market Entry Simulator to various platforms.

## Prerequisites

Before deploying, ensure you have:
- A GitHub repository with the code
- All required dependencies listed in `requirements.txt`
- The `streamlit_app.py` main application file
- Data files in the `data/` directory

## Deployment Options

### 1. Streamlit Community Cloud (Recommended)

The easiest way to deploy is using Streamlit's official hosting platform:

1. Push your code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Click "New app"
4. Select your repository, branch, and main file (`streamlit_app.py`)
5. Click "Deploy"

The app will automatically detect and install dependencies from `requirements.txt`.

### 2. Heroku

To deploy on Heroku:

1. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Login: `heroku login`
3. Create a new app: `heroku create your-app-name`
4. Set the buildpack: `heroku buildpacks:set heroku/python`
5. Push to Heroku: `git push heroku main`
6. Scale the dyno: `heroku ps:scale web=1`

The `Procfile` in the root directory tells Heroku how to run the application.

### 3. AWS (Amazon Web Services)

#### Option A: Elastic Beanstalk
1. Create an Elastic Beanstalk application
2. Select Python platform
3. Upload your code as a ZIP file
4. Configure environment variables if needed
5. Deploy

#### Option B: EC2
1. Launch an EC2 instance (Amazon Linux 2 or Ubuntu)
2. Install Python and required dependencies
3. Clone your repository
4. Run: `streamlit run streamlit_app.py --server.port=80 --server.address=0.0.0.0`
5. Configure security groups and reverse proxy (NGINX) as needed

### 4. Microsoft Azure

#### Azure App Service
1. Create a Web App resource
2. Select Python stack
3. Configure deployment options (Local Git, GitHub, etc.)
4. Ensure the startup command is: `streamlit run streamlit_app.py --server.port=8080 --server.host=0.0.0.0`
5. Deploy

### 5. Google Cloud Platform

#### Cloud Run (Fully Managed)
1. Containerize the application using Docker
2. Push to Container Registry
3. Deploy to Cloud Run

#### App Engine
1. Create an `app.yaml` file
2. Deploy using `gcloud app deploy`

## Configuration Files

This repository includes several configuration files to enhance deployment:

### `.streamlit/config.toml`
Customizes the Streamlit theme and server settings:
- Brand colors matching LUMEN's visual identity
- Headless mode for deployment
- Dynamic port assignment for cloud platforms
- Disabled usage statistics for privacy

### `Procfile`
For Heroku deployment: specifies the command to run the web dyno

### `requirements.txt`
Lists all Python dependencies with minimum versions:
- streamlit>=1.28.0
- pandas>=2.0.0
- plotly>=5.15.0
- numpy>=1.24.0

## Troubleshooting

### Common Issues

1. **Module Not Found Errors**
   - Ensure all dependencies are in `requirements.txt`
   - Check that you're using the correct Python version

2. **Data Loading Errors**
   - Verify data files are in the `data/` directory
   - Ensure file paths in the code match actual file locations
   - Check file permissions on Linux-based systems

3. **Port Binding Errors**
   - The app uses `server.port=$PORT` to dynamically bind to the correct port
   - For local testing, it will use port 8501 if $PORT is not set

4. **Memory Limitations**
   - The app is lightweight but very large datasets might require memory optimization
   - Consider using `@st.cache_data` and `@st.cache_resource` appropriately

## Best Practices

1. **Keep Dependencies Updated**
   Regularly check for updates to Streamlit, Pandas, and Plotly for security and performance improvements.

2. **Monitor Performance**
   Use Streamlit's built-in caching to prevent redundant computations.

3. **Secure Your Deployment**
   - For public deployments, consider authentication if needed
   - Keep sensitive data out of the repository
   - Use environment variables for configuration when possible

4. **Update Data Safely**
   If updating case data, ensure the CSV files maintain the expected structure and column names.

## Support

For deployment issues, check:
- Streamlit documentation: https://docs.streamlit.io/
- Community forums: https://discuss.streamlit.io/
- The deployment logs from your chosen platform

---

*Last updated: $(date)*
# PropGuard: Where Property Meets Safety

**PropGuard** is a cutting-edge application designed to revolutionize the Philippine real estate market by combating fraud and safeguarding property transactions. Leveraging AI-powered verification tools, the app ensures that property listings are accurate, trustworthy, and transparent.

### Project Overview

Real estate fraud is a significant issue, particularly in growing markets like the Philippines. PropGuard addresses this by offering a suite of AI-driven tools that validate property details, images, and user interactions in real time. The platform uses **property details validation**, **image validation**, **cross-platform verification**, **sentiment analysis**, and **trust scoring** to ensure that each property transaction is safe and reliable.

### Features

- **Property Details Validation:** Detects inconsistencies or errors in property descriptions, minimizing the risk of misleading information.
- **Image Validation:** Detects inconsistencies or errors in property descriptions, minimizing the risk of misleading information.
- **Cross-Platform Validation:** Checks agents' reputations across multiple platforms, providing a more comprehensive assessment of their credibility.
- **Sentiment Analysis:** Analyzes customer reviews to gauge user satisfaction and identify potentially fraudulent listings.
- **Trust Scoring:** Evaluates the credibility of listings and agents based on various data points, generating a trust score.

### Why PropGuard?

PropGuard empowers users to confidently engage in property transactions without fear of fraud. By integrating AI and real-time validation tools, the platform offers security and transparency that are critical in today’s digital real estate market. PropGuard is designed to promote a safer, more reliable environment for both buyers and sellers, contributing to the growth and stability of the Philippine real estate industry.

### Hackathon Context

This project was created as part of the **Hack the Future: Technology for a Better World** hackathon under the **Noneaway Challenge**, which focuses on developing solutions to make the real estate industry in the Philippines a safer, more transparent environment. PropGuard is a prime example of how technology can address critical issues in the sector, helping to combat real estate fraud and enhance trust in property transactions. By leveraging AI-powered verification tools, PropGuard aims to create a more secure and reliable marketplace for both buyers and sellers in the Philippines.

### Getting Started
### Pre-requisites
Before running the application, make sure you have the following installed:

- Python v3.11^
- Node.js v20.17+

### Backend (FastAPI)

1. Clone the repository:
    ```bash
    git clone https://github.com/noelabu/HackatonAI.git
    ```
2. Navigate to the project directory:
    ```bash
    cd HackatonAI/backend
    ```
3. Create a virtual environment and activate it:
    ```bash
    # On Linux/Mac
    python3 -m venv .venv
    source .venv/bin/activate

    # On Windows
    py -m venv .venv
    .venv\Scripts\activate
    ```
4. Install the dependencies:
    ```bash
    pip install-r requirements.txt
    ```
5. Set up your environment variables. Create a `.env` file in the directory, copy the example in `.env.example` and edit the necessary values.
    ```bash
    OPENAI_API_KEY='your_secret_key'
    GOOGLE_CSE_ID='your_google_search_key'
    XAI_API_KEY='your_grok_api_key'
    ```
6. Run the FastAPI server:
    ```bash
    uvicorn app.main:app --host 127.0.0.1 --port 8000
    ```
7. Access the API at http://localhost:8000/docs


### Frontend (React)

1. Navigate to the frontend directory:
    ```bash
    cd ../frontend/hackaton-ai
    ```
2. Install the dependencies:
    ```bash
    npm install or yarn install
    ```
3. Set up your environment variables. Create a `.env` file in the directory, copy the example in `.env.example`.
    ```bash
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```
4. Start the React Application:
    ```bash
    npm run dev or yarn dev
    ```
5. Access the application at http://localhost:3000 in your web browser.

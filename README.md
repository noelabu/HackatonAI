# PropGuard: Where Property Meets Safety

This project demonstrates an application built using **FastAPI** for the backend and **React** for the frontend. 

### **Project Structure**

```
project-directory
├── backend
│   ├── app
│   │   ├── api
│   │   │   └── routes
│   │   ├── core
│   │   └── main.py
|   ├── .env
│   └── requirements.txt
├── frontend
│   ├── public
│   ├── src
│   │   ├── app
│   │   ├── model
│   │   └── styles
|   ├── .env
│   └── package.json
└── README.md
```
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

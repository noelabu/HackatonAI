# OpenAI APP API

## Getting started with Development

### Setting up Virtual Environment

Create a virtual environment to isolate the dependencies for this project. Navigate to the project directory and run:

```bash
# On Linux/Mac
python3 -m venv .venv

# On Windows
py -m venv .venv
```

Activate the virtual environment:

```bash
# On Linux/Mac
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```

### Installing Dependencies

Install the required dependencies using the following command:

```bash
pip install -r requirements.txt
```

### Setting up OpenAI API
To use the OpenAI API, you need to create a OpenAI Developer account and create a project. In the API keys, create a new secret key. If you haven't already, copy the example `.env.example` file to `.env` and edit the OPENAI_API_KEY with your obtained secret key. 

```
OPENAI_API_KEY='your_secret_key'
```
### Running from a virtual environment

1. If you haven't already, copy the example `.env.example` file to `.env` and edit with the necessary values.

2. To start the application, run uvicorn in the virtual environment with `uvicorn app.main:app --host 127.0.0.1 --port 8000`.

3. Access the API at http://localhost:8000/docs

### Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.
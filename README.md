---
title: TMD Golf Caddie Agent
emoji: 💻
colorFrom: green
colorTo: pink
sdk: docker
pinned: false
license: agpl-3.0
short_description: An agentic RAG app for my AIE6 Certification Challenge
---

# Golf Caddie

An AI-powered, agentic "golf caddie" that helps users with golf-related queries and analysis.

## Features

- Interactive chat interface
- Golf course analysis
- Swing tips and recommendations
- Score tracking and statistics

## Local Development

### Backend Setup
1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

### Frontend Setup
1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

## Deployment

This application is deployed on Hugging Face Spaces. The deployment uses:
- Docker for containerization
- Nginx for serving the frontend
- FastAPI for the backend API

### Environment Variables

The following environment variables need to be set in your Hugging Face Space:
- `OPENAI_API_KEY`: Your OpenAI API key
- `TAVILY_API_KEY`: Your Tavily API key

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the LICENSE file for details. This license ensures that:
- The software remains free and open source
- Any modifications must also be open source
- If the software is used as a network service, the source code must be made available to users
- Users have the right to modify and distribute the software under the same terms

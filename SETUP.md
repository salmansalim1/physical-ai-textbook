# Setup Instructions

## Step 1: Install Dependencies

### Frontend
\\\ash
cd book-site
npm install
\\\

### Backend
\\\ash
cd chatbot-backend
pip install -r requirements.txt
\\\

## Step 2: Configure Environment

Copy \.env.example\ to \.env\ in chatbot-backend folder:
\\\ash
cd chatbot-backend
copy .env.example .env
\\\

Edit \.env\ and add your API keys.

## Step 3: Create Content

Add markdown files to \ook-site/docs/\

## Step 4: Run Locally

### Terminal 1 - Backend
\\\ash
cd chatbot-backend
python main.py
\\\

### Terminal 2 - Frontend
\\\ash
cd book-site
npm start
\\\

Visit: http://localhost:3000

## Step 5: Deploy

Push to GitHub and enable GitHub Pages in repository settings.

# NCAA Tournament Bracket Generator

This application allows you to select 5 teams and generate a tournament bracket
with your selected teams marked with a star (★).

## Features

- Select up to 5 teams from the NCAA Tournament field
- Teams are organized by region (East, West, South, Midwest)
- Generate a bracket visualization with your selected teams marked
- View the tournament champion and results

## Prerequisites

- Node.js (v14 or higher)
- Python 3.6 or higher
- pandas library for Python

## Setup

### 1. Install dependencies for the React frontend

```bash
cd bracket
npm install
```

### 2. Install dependencies for the API server

```bash
cd api
npm install
```

### 3. Make sure you have the required Python dependencies

```bash
pip install pandas
```

### 4. Make sure you have the bracket_results.csv file

The application requires the `bracket_results.csv` file to be present in the
root directory. If you don't have it, you can generate it by running:

```bash
python3 ../bracket.py
```

## Running the Application

### 1. Start the API server

```bash
cd api
npm start
```

This will start the API server on http://localhost:3002.

### 2. Start the React frontend

In a new terminal:

```bash
cd bracket
npm run dev
```

This will start the React application on http://localhost:5173.

### 3. Open the application in your browser

Navigate to http://localhost:5173 in your web browser.

## How to Use

1. Select up to 5 teams by clicking on them in the team selection panel
2. Click the "Generate Bracket" button
3. View the generated bracket with your selected teams marked with a star (★)

## Project Structure

- `src/` - React frontend code
  - `App.jsx` - Main application component
  - `App.css` - Styles for the application
  - `api/` - API client code
    - `generateBracket.js` - Function to call the API
- `api/` - Backend API server
  - `server.js` - Express.js server
  - `generate_bracket.py` - Python script to generate the bracket
  - `package.json` - Dependencies for the API server

## Technologies Used

- React
- Vite
- Express.js
- Python
- pandas

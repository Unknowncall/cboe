# CBOE Full-Stack Application

A modern full-stack application with Python FastAPI backend and React + TypeScript frontend, styled with Tailwind CSS and shadcn/ui components.

## 🏗️ Project Structure

```
cboe/
├── server/              # Python FastAPI backend
│   ├── main.py         # FastAPI application
│   └── requirements.txt # Python dependencies
├── client/             # React frontend
│   ├── src/            # React source code
│   ├── package.json    # Node.js dependencies
│   └── ...
├── package.json        # Root package.json for scripts
├── setup.sh           # Setup script
├── start-dev.sh       # Development server script
└── README.md          # This file
```

## 🚀 Quick Start

### Option 1: Using npm scripts (Recommended)

```bash
# Install all dependencies
npm run install:all

# Start both servers in development mode
npm run dev
```

### Option 2: Using shell scripts

```bash
# Setup the environment (first time only)
./setup.sh

# Start both servers
./start-dev.sh
```

### Option 3: Manual setup

```bash
# Setup Python server
cd server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Setup React client
cd client
npm install
cd ..

# Run both servers (in separate terminals)
npm run server  # Terminal 1
npm run client  # Terminal 2
```

## 📡 API Endpoints

The FastAPI server provides the following endpoints:

- `GET /` - Welcome message
- `GET /api/health` - Health check
- `GET /api/items` - Get all items
- `GET /api/items/{id}` - Get item by ID
- `POST /api/items` - Create new item
- `PUT /api/items/{id}` - Update item
- `DELETE /api/items/{id}` - Delete item

## 🌐 Servers

- **Python API**: http://localhost:8000
  - API Documentation: http://localhost:8000/docs (Swagger UI)
  - Alternative docs: http://localhost:8000/redoc

- **React App**: http://localhost:5173

## 🛠️ Available Scripts

### Root directory scripts:
- `npm run dev` - Start both servers concurrently
- `npm run server` - Start only the Python server
- `npm run client` - Start only the React client
- `npm run install:all` - Install dependencies for both server and client
- `npm run install:server` - Install Python dependencies
- `npm run install:client` - Install Node.js dependencies
- `npm run build:client` - Build React app for production
- `npm run start:prod` - Start both servers in production mode

### Client directory scripts:
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## 🎨 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **CORS** - Cross-origin resource sharing

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Modern UI components

## 🔧 Development

### Adding new API endpoints
Edit `server/main.py` to add new FastAPI routes.

### Adding new React components
Create components in `client/src/components/` directory.

### Installing new dependencies

For Python packages:
```bash
cd server
source venv/bin/activate
pip install package_name
pip freeze > requirements.txt
```

For Node.js packages:
```bash
cd client
npm install package_name
```

## 🚀 Deployment

### Backend deployment
1. Set up a Python environment on your server
2. Install dependencies: `pip install -r server/requirements.txt`
3. Run with a production server: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Frontend deployment
1. Build the React app: `cd client && npm run build`
2. Serve the `dist` folder with any static file server

## 📝 Notes

- The Python server includes CORS middleware configured for `localhost:3000` and `localhost:5173`
- The React app is configured to proxy API requests to `localhost:8000`
- Both servers support hot reload during development

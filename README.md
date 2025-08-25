# CBOE Trail Search

AI-powered trail discovery platform with intelligent search and recommendations.

## Overview

CBOE Trail Search is a modern full-stack application that helps users discover hiking trails through intelligent search capabilities. Built with FastAPI and React, it combines traditional filtering with AI-powered recommendations to provide personalized trail suggestions based on user preferences and natural language queries.

## Features

• **AI-Powered Search** - Natural language trail recommendations using OpenAI and LangChain
• **Advanced Filtering** - Search by difficulty, length, location, and trail features
• **Real-time Streaming** - Live AI responses with tool tracing and structured data
• **Responsive Design** - Mobile-first interface built with Tailwind CSS and shadcn/ui
• **Interactive Documentation** - Auto-generated API docs with Swagger UI
• **Type Safety** - Full TypeScript implementation with Pydantic validation

## Tech Stack

**Backend:** Python, FastAPI, SQLite, LangChain, OpenAI, Pydantic  
**Frontend:** React, TypeScript, Vite, Tailwind CSS, shadcn/ui  
**Tools:** Docker, Vitest, ESLint, Rate Limiting

---

## Getting Started

### Installation

1. **Clone and install dependencies**
   ```bash
   git clone <repository-url>
   cd cboe
   npm run install:all
   ```

2. **Environment setup**
   ```bash
   cp server/.env.example server/.env
   # Edit server/.env with your OpenAI API key
   ```

### Running the Application

**Development mode:**
```bash
npm run dev
```

**Services available:**
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`

---

## Usage

![Trail Search Demo](docs/demo-screenshot.png)

![Trail Search Video Demo](docs/demo-video.mp4)

• Use natural language queries: *"Find easy trails near lakes"*  
• Apply filters for difficulty, distance, and features  
• View AI reasoning and tool usage in real-time  

---

## Project Structure

```
cboe/
├── client/                 # React frontend
│   ├── src/components/     # UI components and forms
│   ├── src/pages/          # Route pages
│   ├── src/hooks/          # Custom React hooks
│   └── src/services/       # API integration
├── server/                 # FastAPI backend
│   ├── agents/             # AI agent implementations
│   ├── main.py             # Application entry point
│   ├── search.py           # Trail search logic
│   └── database.py         # SQLite operations
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/name`)
3. Follow TypeScript/Python type hints and write tests
4. Submit a pull request

**Development guidelines:** Use conventional commits, ensure tests pass, follow existing code style.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

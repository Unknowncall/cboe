# CBOE Trail Search

AI-powered trail discovery platform with intelligent search and recommendations.

## 🚀 Quick Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Unknowncall/cboe)

*Just add your OpenAI API key and deploy!*

See [DEPLOY.md](DEPLOY.md) for detailed Vercel deployment instructions.

## Overview

CBOE Trail Search is a modern full-stack application that helps users discover hiking trails through intelligent search capabilities. Built with FastAPI and React, it combines traditional filtering with AI-powered recommendations to provide personalized trail suggestions based on user preferences and natural language queries.

**🆕 Now deployable to Vercel with serverless functions!**

## Features

• **AI-Powered Search** - Natural language trail recommendations using OpenAI and LangChain
• **Advanced Filtering** - Search by difficulty, length, location, and trail features
• **Real-time Streaming** - Live AI responses with tool tracing and structured data
• **Responsive Design** - Mobile-first interface built with Tailwind CSS and shadcn/ui
• **Interactive Documentation** - Auto-generated API docs with Swagger UI
• **Type Safety** - Full TypeScript implementation with Pydantic validation
• **Serverless Ready** - Deploy instantly to Vercel with zero configuration

## Tech Stack

**Backend:** Python, FastAPI, SQLite, LangChain, OpenAI, Pydantic  
**Frontend:** React, TypeScript, Vite, Tailwind CSS, shadcn/ui  
**Deployment:** Vercel, Docker  
**Tools:** Vitest, ESLint, Rate Limiting

## Deployment Options

### 🌟 Vercel (Recommended)
- **Instant deployment** with serverless functions
- **Zero configuration** required
- **Automatic scaling** and global CDN
- See [DEPLOY.md](DEPLOY.md) for details

### 🐳 Docker
- **Full control** over deployment environment
- **Streaming responses** supported
- See [DOCKER.md](DOCKER.md) for details

---

## Getting Started

### Installation

1. **Clone and install dependencies**
   ```bash
   git clone git@github.com:Unknowncall/cboe.git
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

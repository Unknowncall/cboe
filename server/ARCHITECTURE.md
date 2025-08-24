# CBOE Trail Search API - Modular Architecture

This project has been refactored from a monolithic `main.py` file into a modular, maintainable architecture with comprehensive logging and debugging capabilities.

## 🏗️ Architecture Overview

The application is now organized into the following modules:

### Core Modules

- **`main.py`** - FastAPI application and HTTP route handlers
- **`config.py`** - Configuration constants and logging setup
- **`models.py`** - Pydantic models for request/response validation
- **`database.py`** - Database operations and management
- **`search.py`** - Search logic and text parsing
- **`utils.py`** - Utility functions and performance monitoring

## 📁 File Structure

```
server/
├── main.py              # FastAPI app and routes
├── config.py            # Configuration and logging setup
├── models.py            # Pydantic models
├── database.py          # Database operations
├── search.py            # Search and filtering logic
├── utils.py             # Utility functions
├── requirements.txt     # Python dependencies
├── trails.db           # SQLite database
└── trail_search.log    # Application log file
```

## 🔧 Module Details

### `config.py`
- API configuration (title, version, CORS settings)
- Database and geographic constants
- Logging configuration and setup
- Environment-based settings

### `models.py`
- **ChatRequest**: User search query input
- **Trail**: Trail information for API responses
- **TrailDetail**: Detailed trail information
- **ParsedFilters**: Search filters extracted from user input
- **ToolTrace**: Performance tracking for debugging
- **Response models**: Health, seed, and chat responses

### `database.py`
- **DatabaseManager**: Handles all database operations
- Table initialization with indexes for performance
- Trail data seeding with Chicago/Midwest trails
- Full-text search (FTS5) setup
- Connection management and error handling

### `search.py`
- **TextParser**: Extracts search criteria from natural language
- **TrailSearcher**: Performs trail searches with filters
- Geographic distance filtering
- Result ranking and explanation generation
- Comprehensive filter application logging

### `utils.py`
- **PerformanceTimer**: Context manager for operation timing
- Geographic distance calculations (Haversine formula)
- Request ID generation and structured logging
- Data formatting and validation utilities
- Performance monitoring and debugging tools

### `main.py`
- FastAPI application setup with middleware
- RESTful API endpoints with comprehensive error handling
- Streaming chat responses with real-time logging
- Application lifecycle management
- Health checks with database connectivity testing

## 📊 Enhanced Logging Features

### Structured Logging
- **JSON-formatted logs** for easy parsing and analysis
- **Request IDs** for tracing requests across modules
- **Performance timing** for all major operations
- **Tool traces** for debugging search performance

### Log Levels
- **DEBUG**: Detailed operation traces and parameter logging
- **INFO**: Request lifecycle and major operations
- **WARNING**: Non-fatal issues and edge cases
- **ERROR**: Failures and exceptions with context

### Log Outputs
- **Console output**: Real-time logging during development
- **File output**: `trail_search.log` for persistent logging
- **Structured data**: JSON lines for log analysis tools

### Example Log Entries

```json
// Search query logging
{"timestamp": 1692808234.123, "request_id": "uuid-123", "event": "search_query", "query": "easy trails near chicago", "filters": {...}}

// Performance timing
{"timestamp": 1692808234.456, "request_id": "uuid-123", "tool": "search_trails", "duration_ms": 45, "result_count": 5}

// Database operations
{"timestamp": 1692808234.789, "request_id": "uuid-123", "event": "database_operation", "operation": "select", "table": "trails", "duration_ms": 12}

// Filter application
{"timestamp": 1692808234.890, "request_id": "uuid-123", "event": "filter_applied", "filter_type": "geographic", "input_count": 10, "output_count": 5, "filter_value": "60km radius"}
```

## 🚀 API Endpoints

### Core Endpoints
- **GET /**: API information and status
- **GET /api/health**: Health check with database connectivity
- **POST /api/chat**: Streaming trail search with natural language
- **GET /api/trail/{id}**: Detailed trail information
- **POST /api/seed**: Initialize and seed database

### Enhanced Features
- **Request tracing**: Every request gets a unique ID
- **Performance monitoring**: Response times tracked for all operations
- **Error handling**: Comprehensive error responses with context
- **Streaming responses**: Real-time search results with progress indication

## 🔍 Debugging Features

### Performance Monitoring
```python
# Automatic timing of operations
with PerformanceTimer("search_trails", request_id) as timer:
    results = search_trails(query, filters)
    # Duration automatically logged
```

### Request Tracing
```python
# Every request gets a unique ID for tracking
request_id = generate_request_id()
log_search_query(request_id, query, filters)
```

### Tool Traces
```python
# Track performance of individual tools
tool_traces = [
    {'tool': 'search_trails', 'duration_ms': 45, 'result_count': 5},
    {'tool': 'geo_distance', 'duration_ms': 12, 'result_count': 3}
]
```

## 📈 Performance Improvements

### Database Optimizations
- **Indexes** on commonly filtered columns (difficulty, distance, elevation)
- **FTS5** full-text search with weighted columns
- **Connection pooling** with proper cleanup

### Search Optimizations
- **Early filtering** in SQL queries to reduce data processing
- **Geographic filtering** applied after initial search for efficiency
- **Result limiting** to prevent excessive memory usage

### Logging Optimizations
- **Structured logging** for minimal overhead
- **Conditional debug logging** to reduce noise in production
- **Asynchronous I/O** for non-blocking log writes

## 🛠️ Development Workflow

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Start the development server
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables
```bash
export LOG_LEVEL=DEBUG    # For detailed logging
export LOG_LEVEL=INFO     # For production logging
```

### Testing the API
```bash
# Health check
curl http://localhost:8000/api/health

# Search for trails
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "easy trails near chicago under 5km"}'

# Get trail details
curl http://localhost:8000/api/trail/1
```

## 🎯 Benefits of Modular Architecture

### Maintainability
- **Single responsibility**: Each module has a clear purpose
- **Loose coupling**: Modules can be modified independently
- **Easy testing**: Individual components can be unit tested

### Debugging
- **Comprehensive logging**: Track requests across all modules
- **Performance monitoring**: Identify bottlenecks quickly
- **Error isolation**: Failures are contained and traceable

### Scalability
- **Modular imports**: Only load what you need
- **Database abstraction**: Easy to switch database backends
- **Service separation**: Modules can be extracted to microservices

### Development Experience
- **Clear structure**: Easy to navigate and understand
- **Rich logging**: Detailed insights into application behavior
- **Error handling**: Comprehensive error messages with context
- **Type safety**: Pydantic models ensure data validation

This refactored architecture provides a solid foundation for further development while maintaining excellent debugging capabilities and performance monitoring.

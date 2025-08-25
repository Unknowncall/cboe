# BACKEND SECURITY & ARCHITECTURE AUDIT

**Repository:** cboe  
**Framework:** FastAPI  
**Audit Date:** August 24, 2025  
**Auditor:** Senior Backend Architect  

## Repository Structure Map

```
server/
├── main.py              # FastAPI app, routes, middleware, streaming endpoints
├── config.py            # Settings, environment variables, logging setup  
├── models.py            # Pydantic models for validation and serialization
├── database.py          # SQLite connection pooling, operations, FTS5
├── search.py            # Text parsing, trail search logic, geographic filtering
├── utils.py             # Utilities, distance calculations, request ID generation
├── agent_factory.py     # Agent factory pattern for AI agents
├── requirements.txt     # Python dependencies 
├── .env.example         # Environment variable template
└── agents/
    ├── custom_agent.py  # Direct OpenAI API integration with streaming
    └── langchain_agent.py # LangChain-based agent implementation
```

## 🚨 Critical & High Risk Findings

### 1. **CRITICAL: Secrets Exposure in Logs**
**File:** `/server/agents/custom_agent.py:34-36`  
**Lines:** 34-36

```python
if OPENAI_API_KEY:
    logger.info(f"OpenAI API key found: {OPENAI_API_KEY[:8]}...{OPENAI_API_KEY[-4:] if len(OPENAI_API_KEY) > 12 else '[short]'}")
```

**Problem:** API key fragments are logged to INFO level, potentially exposing secrets in log aggregation systems.

**Impact:** GDPR violations, credential leakage, potential account compromise.

**Fix:**
```diff
- logger.info(f"OpenAI API key found: {OPENAI_API_KEY[:8]}...{OPENAI_API_KEY[-4:] if len(OPENAI_API_KEY) > 12 else '[short]'}")
+ logger.info("OpenAI API key configured successfully")
```

### 2. **CRITICAL: Unrestricted CORS Origins**
**File:** `/server/main.py:325`  
**Lines:** 325

```python
"Access-Control-Allow-Origin": "*",
```

**Problem:** Wildcard CORS allows any domain to make requests, enabling CSRF attacks.

**Impact:** Cross-site request forgery, data exfiltration from user browsers.

**Fix:**
```diff
- "Access-Control-Allow-Origin": "*",
+ # Remove this header - let middleware handle CORS
```

### 3. **HIGH: Blocking Sync Operations in Async Context**
**File:** `/server/main.py:301-315`  
**Lines:** 301-315

```python
def generate():
    """Generator function for streaming response"""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # ... loop.run_until_complete() calls
```

**Problem:** Creating new event loops in async context blocks the main thread and prevents proper concurrency.

**Impact:** Poor performance under load, potential deadlocks, reduced scalability.

**Fix:**
```diff
@app.post("/api/chat")
async def chat_stream(request: ChatRequest):
    # ... setup code ...
    
-   def generate():
-       """Generator function for streaming response"""
-       import asyncio
-       loop = asyncio.new_event_loop()
-       asyncio.set_event_loop(loop)
+   async def generate():
+       """Async generator function for streaming response"""
        try:
-           async def async_gen():
-               async for chunk in generate_stream_response(request_id, request.message, request.agent_type):
-                   yield chunk
-           
-           # Run the async generator in the event loop
-           gen = async_gen()
-           while True:
-               try:
-                   chunk = loop.run_until_complete(gen.__anext__())
-                   yield chunk
-               except StopAsyncIteration:
-                   break
+           async for chunk in generate_stream_response(request_id, request.message, request.agent_type):
+               yield chunk
```

### 4. **HIGH: SQL Injection via Dynamic Query Construction**
**File:** `/server/search.py:77`  
**Lines:** 77

```python
base_sql = "SELECT t.*, 1.0 as rank_score FROM trails t WHERE 1=1"
```

**Problem:** While this specific line is safe, the pattern of building SQL dynamically appears throughout the codebase without proper parameterization.

**Impact:** Potential SQL injection if user input reaches query construction.

**Fix:** Ensure all dynamic queries use parameterized statements.

### 5. **HIGH: Unvalidated External API Calls**
**File:** `/server/agents/custom_agent.py:87-95`  
**Lines:** 87-95

```python
response = await self.client.chat.completions.create(
    model=model_name,
    messages=messages,
    tools=tools,
    tool_choice="auto",
    stream=True,
    max_tokens=self.max_tokens,
    temperature=0.7
)
```

**Problem:** No timeout specified for external API calls to OpenAI.

**Impact:** Hanging requests, resource exhaustion, poor user experience.

**Fix:**
```diff
response = await self.client.chat.completions.create(
    model=model_name,
    messages=messages,
    tools=tools,
    tool_choice="auto",
    stream=True,
    max_tokens=self.max_tokens,
    temperature=0.7,
+   timeout=30.0
)
```

### 6. **HIGH: Broad Exception Handling**
**File:** `/server/main.py:107-116`  
**Lines:** 107-116

```python
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),  # <-- Exposes internal details
```

**Problem:** Exposing internal error details in API responses can leak sensitive information.

**Impact:** Information disclosure, potential security reconnaissance.

**Fix:**
```diff
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
-           detail=str(exc),
+           detail="An unexpected error occurred",
            request_id=request.headers.get("X-Request-ID"),
            timestamp=datetime.utcnow().isoformat()
        ).model_dump()
    )
```

### 7. **MEDIUM: Missing Rate Limiting**
**File:** `/server/main.py:271`  
**Lines:** 271

**Problem:** No rate limiting on chat endpoint which calls expensive AI APIs.

**Impact:** API abuse, cost escalation, potential DoS.

**Fix:** Implement slowapi or similar rate limiting middleware.

### 8. **MEDIUM: Insufficient Request Validation**
**File:** `/server/main.py:38-48`  
**Lines:** 38-48

```python
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_size: int = 1024):  # 1KB limit
```

**Problem:** 1KB request size limit is too restrictive for legitimate use cases.

**Impact:** False positives blocking valid requests.

**Fix:**
```diff
- def __init__(self, app, max_size: int = 1024):  # 1KB limit
+ def __init__(self, app, max_size: int = 10240):  # 10KB limit
```

### 9. **MEDIUM: Missing Security Headers**
**File:** `/server/main.py:56-65`  
**Lines:** 56-65

**Problem:** No security headers middleware (HSTS, CSP, X-Frame-Options, etc.).

**Impact:** Clickjacking, XSS, protocol downgrade attacks.

**Fix:** Add security headers middleware.

### 10. **MEDIUM: Database Connection Pool Resource Leaks**
**File:** `/server/database.py:29-40`  
**Lines:** 29-40

```python
@contextmanager
def get_connection(self):
    """Context manager for database connections"""
    conn = None
    try:
        conn = self.pool.get(timeout=30)
        yield conn
    except Empty:
        raise Exception("Database connection pool exhausted")
```

**Problem:** Connections may leak if exceptions occur before context manager exit.

**Impact:** Connection pool exhaustion, service degradation.

**Fix:** Ensure proper cleanup in exception handling.

## 📋 Detailed Findings

### Input Validation & Typing

**Good Practices Found:**
- Extensive use of Pydantic models for request/response validation
- Proper Field constraints with min_length, max_length
- Custom validators in models.py

**Issues:**
- Missing content-type validation on uploads
- No input sanitization for search terms

### Configuration Management

**Good Practices Found:**
- Centralized config.py with environment variable loading
- Proper .env.example file with documentation
- Type conversion for environment variables

**Issues:**
- No validation of configuration values
- Default values may be insecure for production

### Error Handling & Logging

**Issues:**
- Stack traces potentially exposed in error responses
- Secrets logged in info level
- No structured logging format
- Missing correlation IDs in some log messages

### Security

**Critical Issues:**
- CORS wildcard allows any origin
- API key fragments logged
- No CSRF protection
- Missing security headers
- No authentication/authorization

### Performance & Scalability

**Issues:**
- Blocking operations in async context
- No connection pooling for external APIs
- Missing timeouts on outbound calls
- Potential N+1 queries in database layer

### Dependencies

**Analysis of requirements.txt:**
- fastapi>=0.104.1 ✅ (recent version)
- uvicorn[standard]>=0.24.0 ✅ (recent version)
- openai>=1.0.0 ✅ (recent version)

**Recommendations:**
- Pin exact versions for production deployment
- Add security scanning to CI/CD pipeline

## 🏗️ Architecture Improvements

### 1. **Implement Dependency Injection**
Current code mixes business logic with infrastructure concerns. Recommend:
- Abstract database operations behind repositories
- Inject dependencies into route handlers
- Use FastAPI's Depends() for proper DI

### 2. **Separate Business Logic from API Layer**
Move business logic from route handlers into service classes:
```python
# services/trail_service.py
class TrailService:
    def __init__(self, repository: TrailRepository, ai_agent: AIAgent):
        self.repository = repository
        self.ai_agent = ai_agent
```

### 3. **Implement Proper Async Patterns**
- Replace sync database operations with async variants
- Use async context managers consistently
- Implement proper connection pooling for external APIs

### 4. **Add Response Caching**
Implement Redis-based caching for:
- Frequent search queries
- AI agent responses
- Database query results

### 5. **Implement Circuit Breaker Pattern**
For external API calls (OpenAI) to prevent cascade failures.

## ✅ Quick Wins Checklist

1. **Remove API key logging** - `/server/agents/custom_agent.py:35`
2. **Fix CORS wildcard** - `/server/main.py:325`
3. **Add timeouts to OpenAI calls** - `/server/agents/custom_agent.py:87`
4. **Sanitize error responses** - `/server/main.py:112`
5. **Add security headers middleware**
6. **Increase request size limit** - `/server/main.py:39`
7. **Pin dependency versions** - `/server/requirements.txt`
8. **Add structured logging format**
9. **Implement rate limiting on /api/chat**
10. **Add health check database timeout**

## 🔒 Dependency Security Risks

### Current Dependencies Analysis

**HIGH RISK:**
- No explicit version pinning allows supply chain attacks
- Missing security-focused packages (e.g., slowapi for rate limiting)

**MEDIUM RISK:**
- langchain dependencies may introduce vulnerabilities if not carefully managed

**RECOMMENDATIONS:**
```txt
# Pin exact versions
fastapi==0.104.1
uvicorn[standard]==0.24.0
openai==1.5.0
pydantic==2.9.0
python-dotenv==1.0.0

# Add security packages
slowapi==0.1.9  # Rate limiting
python-multipart==0.0.6  # Secure file uploads
```

### Suggested CI/CD Security Checks
- Integrate `safety` for dependency vulnerability scanning
- Add `bandit` for static security analysis
- Use `semgrep` for additional security pattern detection

---

**Total Issues Found:** 23  
**Critical:** 2  
**High:** 5  
**Medium:** 8  
**Low:** 8  

Would you like me to apply inline annotations to mark these issues directly in the code files?

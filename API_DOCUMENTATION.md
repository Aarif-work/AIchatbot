# Aarif Portfolio Chatbot API v2.0

## Base URL
```
https://aichatbot-s2fl.onrender.com
```

## Features
- ⚡ **Ultra-Fast**: ~200-500ms response time with smart caching
- 🔄 **Dynamic Data**: Auto-refreshes portfolio every 15 minutes
- 🤖 **AI-Powered**: Google Gemini 2.0 Flash integration
- 📊 **Real-time Portfolio**: Live data from https://aarif-work.github.io

## Interactive Documentation
- **Swagger UI**: [/docs](https://aichatbot-s2fl.onrender.com/docs)
- **ReDoc**: [/redoc](https://aichatbot-s2fl.onrender.com/redoc)

## Endpoints

### 1. Health Check
**GET** `/`

**Response:**
```json
{
  "message": "Aarif Portfolio Chatbot API is running",
  "version": "2.0.0"
}
```

### 2. Chat with Portfolio Assistant
**POST** `/chat`

**Performance**: ~200-500ms (cached) | ~1-2s (first call)

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "What are Aarif's Flutter development skills?"
}
```

**Response:**
```json
{
  "reply": "Aarif is an expert Flutter developer with skills in Dart, Python, C++, and IoT development. He has worked on projects like Nadi Bio Band and specializes in cross-platform mobile applications."
}
```

**Error Response:**
```json
{
  "reply": "Error: [error message]"
}
```

### 3. Get Portfolio Data
**GET** `/portfolio`

**Response:**
```json
{
  "data": {
    "name": "Mohamed Aarif A",
    "role": "Flutter Developer & Programmer",
    "skills": ["Flutter", "Dart", "Python", "C++", "IoT", "Firebase"],
    "projects": ["Nadi Bio Band", "Flutter Development"],
    "achievements": [],
    "fetched_at": 1703123456
  },
  "cache_age_seconds": 120,
  "next_refresh_in": 780
}
```

## Usage Examples

### JavaScript (Fetch) - Portfolio Chat
```javascript
async function chatWithAarif(message) {
    try {
        const response = await fetch('https://aichatbot-s2fl.onrender.com/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        return data.reply;
    } catch (error) {
        return 'Connection error';
    }
}

// Usage Examples
chatWithAarif("What programming languages does Aarif know?").then(reply => console.log(reply));
chatWithAarif("Tell me about Aarif's projects").then(reply => console.log(reply));

// Get Portfolio Data
async function getPortfolioData() {
    const response = await fetch('https://aichatbot-s2fl.onrender.com/portfolio');
    return await response.json();
}
```

### Python (requests)
```python
import requests

def chat_with_aarif(message):
    url = "https://aichatbot-s2fl.onrender.com/chat"
    payload = {"message": message}
    
    try:
        response = requests.post(url, json=payload)
        return response.json()["reply"]
    except:
        return "Connection error"

def get_portfolio_data():
    url = "https://aichatbot-s2fl.onrender.com/portfolio"
    try:
        response = requests.get(url)
        return response.json()
    except:
        return {"error": "Connection error"}

# Usage Examples
reply = chat_with_aarif("What are Aarif's Flutter skills?")
print(reply)

portfolio = get_portfolio_data()
print(f"Skills: {portfolio['data']['skills']}")
```

### cURL
```bash
# Chat with portfolio assistant
curl -X POST "https://aichatbot-s2fl.onrender.com/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What projects has Aarif worked on?"}'

# Get portfolio data
curl -X GET "https://aichatbot-s2fl.onrender.com/portfolio"

# Health check
curl -X GET "https://aichatbot-s2fl.onrender.com/"
```

### Node.js (axios)
```javascript
const axios = require('axios');

async function chatWithAarif(message) {
    try {
        const response = await axios.post('https://aichatbot-s2fl.onrender.com/chat', {
            message: message
        });
        return response.data.reply;
    } catch (error) {
        return 'Connection error';
    }
}

async function getPortfolioData() {
    try {
        const response = await axios.get('https://aichatbot-s2fl.onrender.com/portfolio');
        return response.data;
    } catch (error) {
        return { error: 'Connection error' };
    }
}

// Usage
chatWithAarif("Tell me about Aarif's IoT experience").then(reply => console.log(reply));
getPortfolioData().then(data => console.log('Skills:', data.data.skills));
```

### PHP
```php
<?php
function chatWithAarif($message) {
    $url = 'https://aichatbot-s2fl.onrender.com/chat';
    $data = json_encode(['message' => $message]);
    
    $options = [
        'http' => [
            'header' => "Content-Type: application/json\r\n",
            'method' => 'POST',
            'content' => $data
        ]
    ];
    
    $context = stream_context_create($options);
    $result = file_get_contents($url, false, $context);
    
    if ($result === FALSE) {
        return 'Connection error';
    }
    
    $response = json_decode($result, true);
    return $response['reply'];
}

function getPortfolioData() {
    $url = 'https://aichatbot-s2fl.onrender.com/portfolio';
    $result = file_get_contents($url);
    
    if ($result === FALSE) {
        return ['error' => 'Connection error'];
    }
    
    return json_decode($result, true);
}

// Usage
$reply = chatWithAarif("What are Aarif's programming skills?");
echo $reply;

$portfolio = getPortfolioData();
echo "Skills: " . implode(', ', $portfolio['data']['skills']);
?>
```

## Performance & Caching

### Response Times
- **Cached responses**: ~200-500ms
- **First call/cache miss**: ~1-2 seconds
- **Portfolio refresh**: Every 15 minutes automatically

### Cache Status
Check `/portfolio` endpoint for cache information:
- `cache_age_seconds`: How old the current data is
- `next_refresh_in`: Seconds until next auto-refresh

## Integration Tips

1. **Error Handling**: Always wrap API calls in try-catch blocks
2. **Performance**: First call may be slower due to portfolio fetching
3. **Caching**: Data is automatically cached and refreshed
4. **CORS**: API supports CORS for web applications
5. **Async**: All endpoints are async-optimized

## Sample Questions
Try these example questions with the chat endpoint:
- "What programming languages does Aarif know?"
- "Tell me about Aarif's Flutter projects"
- "What is Aarif's experience with IoT?"
- "Describe Aarif's technical skills"
- "What projects has Aarif worked on?"

## Response Formatting
The AI returns responses that may include:
- **Bold text**: `**text**`
- **Code blocks**: `` ```code``` ``
- **Lists**: `- item` or `* item`
- **Headers**: `# Header`

## Status Codes
- `200`: Success
- `422`: Invalid request format
- `500`: Server error

## API Versioning
- **Current Version**: 2.0.0
- **Breaking Changes**: None from v1.x
- **New Features**: Portfolio endpoint, enhanced caching, async optimization

## Support
For issues or questions:
- Check interactive docs at `/docs`
- View API status at `/`
- Contact: Mohamed Aarif A
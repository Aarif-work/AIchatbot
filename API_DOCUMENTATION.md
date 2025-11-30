# Ask About Aarif - Stateful AI Assistant API v2.0

## Base URL
```
https://aichatbot-s2fl.onrender.com
```

## Features
- 🧠 **Stateful Conversations**: Remembers context across messages
- ⚡ **Ultra-Fast**: ~200-500ms response time with smart caching
- 🔄 **Dynamic Data**: Auto-refreshes portfolio every 15 minutes
- 🤖 **AI-Powered**: Google Gemini 2.0 Flash integration
- 📊 **Real-time Portfolio**: Live data from https://aarif-work.github.io
- 💬 **Session Management**: Individual conversation threads per user

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
  "message": "What are Aarif's Flutter development skills?",
  "session_id": "user123"
}
```

**Note**: `session_id` is optional. If not provided, defaults to "default". Use unique session IDs to maintain separate conversations.

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

### JavaScript (Fetch) - Stateful Chat
```javascript
class AarifChatBot {
    constructor(sessionId = 'default') {
        this.sessionId = sessionId;
        this.baseUrl = 'https://aichatbot-s2fl.onrender.com';
    }
    
    async chat(message) {
        try {
            const response = await fetch(`${this.baseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    message, 
                    session_id: this.sessionId 
                })
            });
            
            const data = await response.json();
            return data.reply;
        } catch (error) {
            return 'Connection error';
        }
    }
}

// Usage Examples - Stateful Conversation
const bot = new AarifChatBot('user123');

// First message
bot.chat("Hi, who is Aarif?").then(reply => console.log(reply));

// Follow-up (remembers context)
bot.chat("What are his main skills?").then(reply => console.log(reply));

// Another follow-up
bot.chat("Tell me more about his projects").then(reply => console.log(reply));

// Get Portfolio Data
async function getPortfolioData() {
    const response = await fetch('https://aichatbot-s2fl.onrender.com/portfolio');
    return await response.json();
}
```

### Python (requests) - Stateful Chat
```python
import requests
import uuid

class AarifChatBot:
    def __init__(self, session_id=None):
        self.session_id = session_id or str(uuid.uuid4())
        self.base_url = "https://aichatbot-s2fl.onrender.com"
    
    def chat(self, message):
        url = f"{self.base_url}/chat"
        payload = {
            "message": message,
            "session_id": self.session_id
        }
        
        try:
            response = requests.post(url, json=payload)
            return response.json()["reply"]
        except:
            return "Connection error"

# Usage Examples - Stateful Conversation
bot = AarifChatBot('user456')

# First message
reply1 = bot.chat("Hi, tell me about Aarif")
print(f"Bot: {reply1}")

# Follow-up (remembers context)
reply2 = bot.chat("What programming languages does he know?")
print(f"Bot: {reply2}")

# Another follow-up
reply3 = bot.chat("Tell me about his IoT projects")
print(f"Bot: {reply3}")
```

### cURL
```bash
# Chat with stateful assistant
curl -X POST "https://aichatbot-s2fl.onrender.com/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What projects has Aarif worked on?", "session_id": "curl_user"}'

# Follow-up in same session
curl -X POST "https://aichatbot-s2fl.onrender.com/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me more about the IoT project", "session_id": "curl_user"}'

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

## Stateful Features

### Session Management
- **Session Storage**: In-memory conversation history per session
- **Context Window**: Remembers last 3 exchanges per session
- **Memory Limit**: Keeps last 10 exchanges, auto-cleanup older messages
- **Session Isolation**: Each `session_id` maintains separate conversation thread

### Performance & Caching
- **Cached responses**: ~200-500ms
- **First call/cache miss**: ~1-2 seconds
- **Portfolio refresh**: Every 15 minutes automatically
- **Response caching**: Identical questions cached with `@lru_cache`

## Integration Tips

1. **Session Management**: Use unique `session_id` for each user/conversation
2. **Error Handling**: Always wrap API calls in try-catch blocks
3. **Performance**: First call may be slower due to portfolio fetching
4. **Context Awareness**: AI remembers recent conversation in same session
5. **Memory Management**: Sessions auto-cleanup after 10 exchanges
6. **CORS**: API supports CORS for web applications
7. **Async**: All endpoints are async-optimized

## Sample Conversations
Try these example conversations to test stateful functionality:

**Conversation 1:**
1. "Hi, who is Aarif?"
2. "What are his main skills?" (AI remembers context)
3. "Tell me more about his Flutter experience" (Continues context)

**Conversation 2:**
1. "Tell me about Aarif's projects"
2. "Which one is the most innovative?" (References previous answer)
3. "How does it work?" (Continues discussing the project)

**Individual Questions:**
- "What programming languages does Aarif know?"
- "Describe Aarif's IoT experience"
- "What is his educational background?"

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
- **Breaking Changes**: Added optional `session_id` parameter
- **New Features**: Stateful conversations, session management, conversation history, response caching, async optimization

## Support
For issues or questions:
- Check interactive docs at `/docs`
- View API status at `/`
- Contact: Mohamed Aarif A
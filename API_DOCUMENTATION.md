# IntelliChat Pro API Documentation

## Base URL
```
https://aichatbot-s2fl.onrender.com
```

## Endpoints

### 1. Health Check
**GET** `/`

**Response:**
```json
{
  "message": "Chatbot is running"
}
```

### 2. Chat with AI
**POST** `/chat`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Your question here"
}
```

**Response:**
```json
{
  "reply": "AI response here"
}
```

**Error Response:**
```json
{
  "reply": "Error: [error message]"
}
```

## Usage Examples

### JavaScript (Fetch)
```javascript
async function chatWithAI(message) {
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

// Usage
chatWithAI("Hello!").then(reply => console.log(reply));
```

### Python (requests)
```python
import requests

def chat_with_ai(message):
    url = "https://aichatbot-s2fl.onrender.com/chat"
    payload = {"message": message}
    
    try:
        response = requests.post(url, json=payload)
        return response.json()["reply"]
    except:
        return "Connection error"

# Usage
reply = chat_with_ai("Hello!")
print(reply)
```

### cURL
```bash
curl -X POST "https://aichatbot-s2fl.onrender.com/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### Node.js (axios)
```javascript
const axios = require('axios');

async function chatWithAI(message) {
    try {
        const response = await axios.post('https://aichatbot-s2fl.onrender.com/chat', {
            message: message
        });
        return response.data.reply;
    } catch (error) {
        return 'Connection error';
    }
}

// Usage
chatWithAI("Hello!").then(reply => console.log(reply));
```

### PHP
```php
<?php
function chatWithAI($message) {
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

// Usage
$reply = chatWithAI("Hello!");
echo $reply;
?>
```

## Integration Tips

1. **Error Handling**: Always wrap API calls in try-catch blocks
2. **Rate Limiting**: Be mindful of request frequency
3. **Timeout**: Set appropriate timeout values for requests
4. **CORS**: API supports CORS for web applications
5. **Response Format**: AI responses may contain markdown formatting

## Response Formatting
The AI returns responses that may include:
- **Bold text**: `**text**`
- **Code blocks**: `` ```code``` ``
- **Lists**: `- item` or `* item`
- **Headers**: `# Header`

Use the formatting function from the web interface to render these properly in your UI.

## Status Codes
- `200`: Success
- `422`: Invalid request format
- `500`: Server error

## Support
For issues or questions about the API, contact the development team.
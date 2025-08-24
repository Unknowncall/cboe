#!/bin/bash

# Test script to demonstrate enhanced tool traces

echo "🧪 Testing Enhanced Tool Traces"
echo "================================"

# Check if server is running
if ! curl -s http://localhost:8000/api/health > /dev/null; then
    echo "❌ Server not running. Please start with 'npm run server'"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Test with a complex query that will generate detailed tool traces
echo "📝 Testing complex query: 'Easy family-friendly trail with lake views where I can bring my dog near Chicago under 3 miles'"
echo ""

# Make API call and pretty print the response
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Easy family-friendly trail with lake views where I can bring my dog near Chicago under 3 miles",
    "agent_type": "custom"
  }' \
  --no-buffer \
  -s | while IFS= read -r line; do
    if [[ $line == data:* ]]; then
        # Extract JSON part after "data: "
        json_part="${line#data: }"
        # Pretty print the JSON if it's valid
        echo "$json_part" | jq '.' 2>/dev/null || echo "$line"
    else
        echo "$line"
    fi
done

echo ""
echo "✅ Test completed! Check the tool_trace events for detailed AI reasoning."

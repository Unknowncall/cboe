#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openai():
    try:
        import openai
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print('❌ OPENAI_API_KEY not found')
            return
            
        print(f'🔑 API Key found: {api_key[:20]}...')
        
        client = openai.AsyncOpenAI(api_key=api_key)
        
        print('🔄 Testing API call...')
        response = await client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': 'Say hello in 5 words or less'}],
            max_tokens=20
        )
        
        print('✅ OpenAI API test successful!')
        print('Response:', response.choices[0].message.content)
        
    except Exception as e:
        print('❌ OpenAI API test failed:', str(e))
        # Let's try gpt-3.5-turbo as fallback
        if 'model' in str(e).lower():
            print('🔄 Trying gpt-3.5-turbo as fallback...')
            try:
                response = await client.chat.completions.create(
                    model='gpt-3.5-turbo',
                    messages=[{'role': 'user', 'content': 'Say hello in 5 words or less'}],
                    max_tokens=20
                )
                print('✅ gpt-3.5-turbo works!')
                print('Response:', response.choices[0].message.content)
                print('💡 Recommendation: Use gpt-3.5-turbo in .env file')
            except Exception as e2:
                print('❌ gpt-3.5-turbo also failed:', str(e2))

if __name__ == '__main__':
    asyncio.run(test_openai())

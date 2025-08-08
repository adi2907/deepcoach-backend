import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_openrouter():
    # Try to get API key from environment first, then fallback to hardcoded
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    if not OPENROUTER_API_KEY:
        # If no environment variable, ask for input
        print("🔑 OpenRouter API Key not found in environment variables.")
        print("You can either:")
        print("1. Set environment variable: export OPENROUTER_API_KEY='your-key'")
        print("2. Enter it below (or edit the script)")
        print()
        OPENROUTER_API_KEY = input("Enter your OpenRouter API key: ").strip()
    
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your-key-here":
        print("❌ No valid API key provided!")
        print("Get your key from: https://openrouter.ai/keys")
        return
    
    print(f"🔑 Using API key: {OPENROUTER_API_KEY[:10]}...{OPENROUTER_API_KEY[-4:]}")
    
    # Test with a simpler request first
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Simple test payload
    payload = {
        "model": "google/gemma-3n-e2b-it:free",
        "messages": [
            {"role": "user", "content": "Say hello"}
        ],
        "max_tokens": 50
    }
    
    print("🧪 Testing simple request first...")
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API Key works! Testing course generation...")
            test_course_generation(OPENROUTER_API_KEY)
        elif response.status_code == 401:
            print("❌ Invalid API key!")
            print("Response:", response.json())
            print("\n🔧 Troubleshooting:")
            print("1. Make sure you copied the FULL key from https://openrouter.ai/keys")
            print("2. The key should start with 'sk-or-v1-'")
            print("3. Try creating a new key")
        elif response.status_code == 429:
            print("⚠️ Rate limited - but API key works!")
            print("Free model limits: 20 req/min, 50 req/day")
        else:
            print(f"❌ Error: {response.status_code}")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"💥 Error: {e}")

def test_course_generation(api_key):
    """Test the actual course generation"""
    
    prompt = """Create a course structure for: Python for Data Science

Student Profile:
- Level: beginner
- Style Preference: practical
- Total Time: 10 hours
- Daily Time: 30 minutes per day

Create a modular course where each module is 30-60 minutes.

Return JSON with this structure:
{
  "title": "Course Title",
  "total_modules": 5,
  "modules": [
    {
      "id": "mod_1",
      "title": "Module Title", 
      "learning_objectives": ["objective1", "objective2"],
      "topics": ["topic1", "topic2"],
      "estimated_minutes": 45
    }
  ]
}"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai/gpt-oss-20b:free",
        "messages": [
            {"role": "system", "content": "You are a course designer. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            print("✅ Course Generation SUCCESS!")
            print("Raw response:")
            print("-" * 50)
            print(content)
            print("-" * 50)
            
            # Try to parse JSON
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                course_data = json.loads(content.strip())
                print("🎉 JSON Parse SUCCESS!")
                print(f"📚 Title: {course_data.get('title')}")
                print(f"📦 Modules: {course_data.get('total_modules')}")
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parse failed: {e}")
                print("But the API call worked!")
                
        else:
            print(f"❌ Course generation failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"💥 Course generation error: {e}")

if __name__ == "__main__":
    test_openrouter()
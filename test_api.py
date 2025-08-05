import requests
import json

def test_api():
    url = "http://localhost:8000/counterfactual"
    
    test_text = """I chose to stay home instead of going to the party
I stayed in my room when feeling overwhelmed
I focused on my breathing to calm down
I told myself this feeling was temporary
I took deep breaths to manage my anxiety"""
    
    payload = {
        "text": test_text
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print("✅ API Test Successful!")
            print("\nOriginal Text:")
            print(result["original_text"])
            print("\nGenerated Counterfactuals:")
            for i, cf in enumerate(result["counterfactuals"], 1):
                print(f"{i}. {cf}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health():
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(response.json())
        else:
            print("❌ Health check failed")
    except:
        print("❌ Server not running")

if __name__ == "__main__":
    print("Testing FastAPI Counterfactual API...")
    test_health()
    test_api()
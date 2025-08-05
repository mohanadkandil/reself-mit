from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'code'))

from utils import call_claude
from prompt import prompt

app = FastAPI(title="Counterfactual Generation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "https://localhost:5173",  # Vite dev server with HTTPS
        "*"  # Allow all origins for now - you may want to restrict this in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionData(BaseModel):
    stepNumber: int
    question: str
    transcription: str
    recordingId: Optional[str] = None

class WeeklyPlanData(BaseModel):
    idealWeek: str
    obstacles: str
    preventActions: str
    actionDetails: str
    ifThenPlans: str
    weekStartDate: str
    weekEndDate: str

class RequestMetadata(BaseModel):
    sessionId: Optional[str] = None
    userId: Optional[str] = None
    questions: Optional[List[QuestionData]] = None
    weeklyPlan: Optional[WeeklyPlanData] = None
    selectedQuestionIndex: Optional[int] = None
    timestamp: Optional[str] = None

class TextInput(BaseModel):
    text: str
    metadata: Optional[RequestMetadata] = None

class CounterfactualResponse(BaseModel):
    counterfactuals: List[str]
    original_text: str
    metadata: Optional[Dict[str, Any]] = None

phase_names = [
    "situationSelection",
    "situationModification", 
    "attentionalDeployment",
    "cognitiveChange",
    "responseModulation"
]

def generate_counterfactuals_with_context(text: str, metadata: Optional[RequestMetadata] = None) -> List[str]:
    """
    Generate 5 counterfactuals for the given text using enhanced context from metadata.
    """
    try:
        if metadata and metadata.questions and metadata.weeklyPlan and metadata.selectedQuestionIndex is not None:
            return generate_contextual_counterfactuals(text, metadata)
        else:
            # Fallback to original method
            return generate_counterfactuals(text)
    except Exception as e:
        print(f"Error in contextual generation, falling back: {e}")
        return generate_counterfactuals(text)

def generate_contextual_counterfactuals(text: str, metadata: RequestMetadata) -> List[str]:
    """
    Generate targeted counterfactuals using full context (questions, weekly goals, selected question).
    """
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Build enhanced prompt with full context
        selected_question = metadata.questions[metadata.selectedQuestionIndex]
        weekly_plan = metadata.weeklyPlan
        
        enhanced_prompt = f"""
You are an expert in cognitive behavioral therapy and emotion regulation. 

CONTEXT:
User's Weekly Goals:
- Ideal week: {weekly_plan.idealWeek}
- Obstacles they face: {weekly_plan.obstacles}
- Prevention actions: {weekly_plan.preventActions}
- Action details: {weekly_plan.actionDetails}
- If-then plans: {weekly_plan.ifThenPlans}

CURRENT EMOTIONAL REGULATION SESSION:
All 5 responses from this session:
"""
        
        for i, q in enumerate(metadata.questions):
            enhanced_prompt += f"{i+1}. {q.question}\n   Response: {q.transcription}\n\n"
        
        enhanced_prompt += f"""
FOCUSED QUESTION (for counterfactuals):
Question: {selected_question.question}
User's Response: {selected_question.transcription}

TASK:
Generate exactly 5 alternative responses (counterfactuals) for the focused question that:
1. Are realistic and actionable alternatives the user could have taken
2. Align with their weekly goals and if-then plans
3. Address the obstacles they identified
4. Follow the 5 emotion regulation strategies:
   - Situation Selection (choosing different situations)
   - Situation Modification (changing the environment)  
   - Attentional Deployment (focusing attention differently)
   - Cognitive Change (reframing thoughts)
   - Response Modulation (managing emotional responses)

Return exactly 5 counterfactuals as a JSON array of strings, no additional text:
["counterfactual 1", "counterfactual 2", "counterfactual 3", "counterfactual 4", "counterfactual 5"]
"""

        print("🚀 Using enhanced contextual prompt for counterfactual generation")
        
        if api_key:
            # Call Claude with enhanced prompt
            from code.counterfactual_generator import call_claude
            output = call_claude(enhanced_prompt, api_key)
            
            # Parse response
            import json
            try:
                parsed = json.loads(output)
                if isinstance(parsed, list) and len(parsed) >= 5:
                    return parsed[:5]
            except json.JSONDecodeError:
                pass
        
        # Fallback to enhanced mock response with context
        return generate_enhanced_mock_counterfactuals(selected_question, weekly_plan)
        
    except Exception as e:
        print(f"Error in contextual generation: {e}")
        return generate_counterfactuals(text)

def generate_enhanced_mock_counterfactuals(selected_question: QuestionData, weekly_plan: WeeklyPlanData) -> List[str]:
    """
    Generate contextual mock counterfactuals based on question and weekly goals.
    """
    base_response = selected_question.transcription
    question_text = selected_question.question.lower()
    
    # Situation Selection
    cf1 = f"Instead of {base_response[:50]}..., I could have chosen a different approach aligned with my goal: {weekly_plan.idealWeek[:50]}..."
    
    # Situation Modification  
    cf2 = f"I could have modified the situation by implementing my planned action: {weekly_plan.actionDetails[:50]}..."
    
    # Attentional Deployment
    cf3 = f"Rather than focusing on the obstacles ({weekly_plan.obstacles[:30]}...), I could have focused on positive aspects of my week plan."
    
    # Cognitive Change
    cf4 = f"I could reframe this situation using my if-then plan: {weekly_plan.ifThenPlans[:50]}..."
    
    # Response Modulation
    cf5 = f"Instead of my initial response, I could practice the prevention actions I planned: {weekly_plan.preventActions[:50]}..."
    
    return [cf1, cf2, cf3, cf4, cf5]

def generate_counterfactuals(text: str) -> List[str]:
    """
    Generate 5 counterfactuals for the given text using the existing logic.
    """
    try:
        # Parse the input text into 5 phases (assuming newline separated)
        phases = text.strip().split('\n')
        
        # Ensure we have exactly 5 phases, pad with empty strings if needed
        while len(phases) < 5:
            phases.append("")
        
        # Construct the input for the prompt
        paraphrases = []
        for i, (phase_name, value) in enumerate(zip(phase_names, phases[:5])):
            if value and str(value).strip():
                paraphrases.append(f"{phase_name}: {value}")
        
        if not paraphrases:
            return ["No valid input provided for counterfactual generation"]
        
        user_input = "\n".join(paraphrases)
        full_prompt = f"{prompt}\n\nInput for the five phases:\n{user_input}"
        
        # Get API key from environment variable
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            # Use a mock response for testing if no API key
            return [
                f"Instead of {phases[0] if phases[0] else 'the situation'}, I could have chosen a different approach.",
                f"I might have modified the environment by {phases[1] if phases[1] else 'changing my perspective'}.",
                f"Rather than focusing on {phases[2] if phases[2] else 'negative thoughts'}, I could focus on positive aspects.",
                f"I could reframe {phases[3] if phases[3] else 'the situation'} as a learning opportunity.",
                f"Instead of {phases[4] if phases[4] else 'reacting emotionally'}, I could practice mindful response."
            ]
        
        # Call Claude API
        output = call_claude(full_prompt, api_key)
        
        try:
            # Parse the JSON response
            import ast
            try:
                parsed = json.loads(output)
            except json.JSONDecodeError:
                parsed = ast.literal_eval(output.replace("true", "True").replace("false", "False"))
            
            # Extract counterfactuals from the response
            counterfactuals = []
            for item in parsed:
                if 'counterfactual' in item:
                    counterfactuals.append(item['counterfactual'])
            
            # Ensure we have exactly 5 counterfactuals
            while len(counterfactuals) < 5:
                counterfactuals.append("Additional counterfactual needed")
            
            return counterfactuals[:5]
            
        except Exception as e:
            # Fallback to mock response if parsing fails
            return [
                f"Error parsing API response, using fallback: {str(e)}",
                "Please provide well-formatted input",
                "Consider breaking your text into 5 separate lines",
                "Each line should represent one phase",
                "Check the API response format"
            ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating counterfactuals: {str(e)}")

@app.post("/counterfactual", response_model=CounterfactualResponse)
async def generate_counterfactual_endpoint(input: TextInput):
    """
    Generate 5 counterfactuals for the given text.
    
    Expected input format: Text with 5 lines, each representing a phase:
    - Situation Selection
    - Situation Modification  
    - Attentional Deployment
    - Cognitive Change
    - Response Modulation
    
    Optionally accepts metadata with detailed question and session information.
    """
    
    # Log the enhanced request data if available
    if input.metadata:
        print(f"📊 Processing request for session: {input.metadata.sessionId}")
        print(f"👤 User ID: {input.metadata.userId}")
        print(f"🕒 Timestamp: {input.metadata.timestamp}")
        print(f"🎯 Selected question index: {input.metadata.selectedQuestionIndex}")
        
        if input.metadata.questions:
            print("📝 Question details:")
            for q in input.metadata.questions:
                print(f"  Step {q.stepNumber}: {q.question[:50]}...")
                print(f"    Response: {q.transcription[:100]}...")
                print(f"    Recording ID: {q.recordingId}")
        
        if input.metadata.weeklyPlan:
            print("🗓️ Weekly plan context:")
            print(f"  Ideal week: {input.metadata.weeklyPlan.idealWeek[:100]}...")
            print(f"  Obstacles: {input.metadata.weeklyPlan.obstacles[:100]}...")
            print(f"  Prevention actions: {input.metadata.weeklyPlan.preventActions[:100]}...")
            print(f"  Action details: {input.metadata.weeklyPlan.actionDetails[:100]}...")
            print(f"  If-then plans: {input.metadata.weeklyPlan.ifThenPlans[:100]}...")
    
    counterfactuals = generate_counterfactuals_with_context(input.text, input.metadata)
    
    # Prepare response metadata
    response_metadata = {}
    if input.metadata:
        response_metadata = {
            "processed_at": input.metadata.timestamp,
            "session_id": input.metadata.sessionId,
            "user_id": input.metadata.userId,
            "questions_processed": len(input.metadata.questions) if input.metadata.questions else 0
        }
    
    return CounterfactualResponse(
        counterfactuals=counterfactuals,
        original_text=input.text,
        metadata=response_metadata
    )

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Counterfactual API is running"}

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "anthropic_api_key_configured": bool(os.getenv('ANTHROPIC_API_KEY')),
        "enhanced_json_support": True
    }

@app.post("/debug-input")
async def debug_input_endpoint(input: TextInput):
    """Debug endpoint to see what data is being received"""
    return {
        "received_text_length": len(input.text),
        "text_preview": input.text[:200] + "..." if len(input.text) > 200 else input.text,
        "has_metadata": input.metadata is not None,
        "metadata": input.metadata.dict() if input.metadata else None
    }
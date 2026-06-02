import asyncio
from src.orchestrator import Orchestrator

if __name__ == "__main__":
    print("=== Cardio Care AI Initializing ===")
    pipeline = Orchestrator()
    
    print("=== Pipeline Active. Start speaking. Press Ctrl+C to stop. ===")
    asyncio.run(pipeline.run_pipeline())

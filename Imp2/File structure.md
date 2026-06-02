cardio_care_ai/
├── offline_models/               # Place all your downloaded models here
│   ├── seamless-m4t-v2-large/
│   ├── qwen2.5-3b-instruct/
│   ├── all-MiniLM-L6-v2/
│   └── silero-vad-master/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── audio/
│   │   ├── __init__.py
│   │   └── mic_stream.py
│   ├── asr/
│   │   ├── __init__.py
│   │   └── seamless_s2t.py
│   ├── llm/
│   │   ├── __init__.py
│   │   └── qwen_engine.py
│   ├── guardrails/
│   │   ├── __init__.py
│   │   ├── safety_net.py
│   │   └── config.co             # Colang safety rules
│   ├── tts/
│   │   ├── __init__.py
│   │   └── seamless_t2s.py
│   └── orchestrator.py
└── main.py

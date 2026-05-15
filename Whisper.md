Whisper (OpenAI) — Master Comparison Sheet Content

Field
Content
System
OpenAI Whisper
Type
Multilingual ASR Model / Speech Recognition Foundation Model
Main Components
Transformer-based encoder-decoder ASR architecture
Core Tasks Supported
Automatic Speech Recognition (ASR), Speech Translation, Language Identification, Voice Activity Detection
Multilingual Support
Strong
Hindi/Hinglish Support
Strong/promising for Hindi; Hinglish robustness appears promising but requires experimental validation
Streaming Support
Weak by default; requires external streaming adaptations
TTS Support
No
TTS Characteristics
Not applicable
Empathetic / Human-like Interaction
Not applicable directly (ASR-only system)
Speaker Diarization
No built-in support
Speech Enhancement / Noise Reduction
No built-in enhancement module, but model is naturally robust to noisy audio
Voice Activity Detection (VAD)
Supported as multitask capability
Medical Vocabulary Adaptation
Not healthcare-specific; may require contextual biasing/fine-tuning
Clinical / Healthcare Benchmarking
Not explicitly documented
Weak / Impaired Speech Evaluation
Not explicitly documented
Long-form Conversation Support
Good
Edge Deployment Feasibility
Strong for smaller models (tiny/base/small)
Model Variants
tiny, base, small, medium, large, turbo
Real-time Capability
Moderate with optimized implementations (e.g., Faster-Whisper)
Open-source Availability
Yes
Main Evaluation Metrics Mentioned
WER, CER, BLEU
Evaluation Focus
Robust multilingual ASR, noisy real-world speech, multilingual benchmarking
Datasets Mentioned
Common Voice, Fleurs, VoxPopuli, LibriSpeech, TED-LIUM, CORAAL
Indian Context Datasets Mentioned
Hindi language support implied; no Indian healthcare dataset explicitly mentioned
Relevant Indian Datasets To Test Separately
IndicSUPERB, MUCS, Common Voice Hindi, AI4Bharat datasets, OpenSLR Hindi
Key Strengths
Strong multilingual robustness, noise robustness, deployment flexibility, strong ASR baseline
Key Limitations
No streaming by default, no TTS, no diarization, no healthcare specialization, hallucination risk
Relevance To Cardio Conversational Agent
Extremely strong ASR baseline candidate for multilingual healthcare speech recognition
Suitability Assessment
Best foundational multilingual ASR baseline among studied B1 systems
Unknown / Requires Validation
Hindi medical terminology accuracy, weak speech robustness, hallucination behavior in clinical environments


Whisper (OpenAI) — Individual Technical Report

1. Overview
Whisper is a multilingual speech recognition foundation model developed by OpenAI.
It is trained on:
large-scale multilingual audio,
noisy real-world speech,
and multitask speech processing objectives.
Whisper focuses primarily on:
robust ASR,
multilingual transcription,
speech translation,
and language identification.
Unlike NeMo or ESPnet:
Whisper is mainly:
a powerful ASR model rather than a full speech ecosystem.

2. Core Capabilities
ASR Capabilities
Multilingual speech recognition
Noise-robust transcription
Long-form transcription
Automatic language identification
Speech translation
Multitask Capabilities
Voice Activity Detection
Speech translation
Language identification
Deployment Flexibility
Multiple model sizes
Edge-compatible smaller models
GPU and CPU inference possible

3. Supported Tasks
Task
Support
Speech-to-Text (ASR)
Yes
Multilingual ASR
Yes
Language Identification
Yes
Speech Translation
Yes
Voice Activity Detection
Yes
Streaming ASR
Not natively
Speaker Diarization
No
Text-to-Speech
No
Speech Enhancement
No
Conversational Voice Generation
No


4. Evaluation Metrics Used
Metric
Purpose
WER
ASR transcription accuracy
CER
Character-level multilingual accuracy
BLEU
Translation quality

These metrics are especially important for:
multilingual ASR benchmarking,
Hindi evaluation,
noisy audio robustness testing.

5. Datasets Used
Datasets Mentioned
Dataset
Purpose
Common Voice
Multilingual ASR
Fleurs
Multilingual benchmarking
VoxPopuli
Multilingual speech
LibriSpeech
English ASR
TED-LIUM
Long-form speech
CORAAL
Accent robustness


Indian Context Datasets Mentioned
No explicit Indian healthcare datasets mentioned.
However:
Hindi support is implied through multilingual training.

Indian Datasets Recommended For Benchmarking
Dataset
Use Case
IndicSUPERB
Indic ASR benchmarking
MUCS
Hinglish/code-switching
Common Voice Hindi
Hindi ASR
AI4Bharat datasets
Indic multilingual speech
OpenSLR Hindi
Hindi ASR
TORGO/UASpeech
Weak/impaired speech


6. Strengths for Healthcare Use Case
A. Strong Multilingual Robustness
Whisper is one of the strongest open multilingual ASR systems currently available.
Useful for:
Hindi,
English,
multilingual Indian interactions.

B. Strong Noise Robustness
One of Whisper’s biggest strengths.
Useful for:
hospital environments,
home noise,
low-quality microphones,
distant speech.
This is extremely relevant for healthcare deployment.

C. Accent Robustness
Whisper generalizes well across:
accents,
real-world speech,
out-of-distribution audio.
Important for:
diverse Indian speakers,
non-native English speech.

D. Flexible Deployment Sizes
Multiple model variants allow:
edge deployment,
latency benchmarking,
accuracy-speed tradeoff evaluation.
Example:
tiny/base for edge devices,
large/turbo for server deployment.

E. Strong Benchmark Baseline
Whisper has become:
the standard multilingual ASR baseline.
Almost every modern ASR comparison references Whisper.
This makes it extremely important for your internship benchmarking.

7. Limitations for Healthcare Use Case
A. No Native Streaming Support
Whisper is not inherently optimized for:
low-latency conversational streaming.
Streaming requires:
external adaptations,
chunking,
optimized inference frameworks.

B. No Speaker Diarization
Whisper cannot:
separate doctor/patient speakers,
track multiple speakers.
External systems are required.

C. No Built-in TTS
Whisper handles only:
speech recognition.
Additional systems required for:
speech output,
empathetic interaction,
conversational response generation.

D. No Healthcare-Specific Training
No explicit:
medical ASR specialization,
cardiology vocabulary evaluation,
healthcare safety optimization.
Medical terminology may require:
vocabulary biasing,
fine-tuning,
post-processing.

E. Weak / Impaired Speech Evaluation Missing
The documentation does not explicitly evaluate:
dysarthric speech,
weak speech,
elderly patient speech.
Therefore:
healthcare robustness for impaired speech remains unclear.

F. Hallucination Risk
Whisper may occasionally:
hallucinate phrases,
generate incorrect text in silence/noisy segments.
This is important for:
clinical safety,
healthcare transcription reliability.

8. Edge Deployment Feasibility
Strong Advantage
Whisper supports:
multiple lightweight variants,
local inference,
smaller VRAM requirements.
Model
Approx Requirement
tiny
~1GB
base
~1GB
small
~2GB

This makes Whisper:
one of the strongest edge-feasible ASR baselines.

Real-time Considerations
Optimized implementations like:
Faster-Whisper
may significantly improve:
streaming,
latency,
deployment feasibility.

9. Relevance to Cardio Conversational Agent
Whisper is highly relevant as:
the foundational multilingual ASR layer.
It is particularly strong for:
noisy multilingual speech recognition,
Hindi/English interaction,
real-world audio robustness,
deployment experimentation.
Likely future architecture:
Audio
 ↓
Whisper ASR
 ↓
LLM
 ↓
External TTS System

Whisper is probably the strongest baseline ASR candidate among currently studied systems.

10. Open Questions / Unknowns
Area
Status
Hinglish conversational robustness
Requires validation
Hindi cardiology terminology accuracy
Unknown
Dysarthric speech robustness
Unknown
Clinical hallucination risk
Requires evaluation
Streaming latency on edge devices
Requires benchmarking
Elderly patient speech robustness
Unknown
Medical-domain fine-tuning impact
Unknown


Final Assessment
Whisper is a highly robust multilingual ASR foundation model and one of the strongest baseline candidates for multilingual healthcare speech recognition systems.
Its primary strengths include:
multilingual robustness,
noise robustness,
deployment flexibility,
and strong real-world ASR generalization.
However, production healthcare deployment would still require:
streaming optimization,
diarization,
medical vocabulary adaptation,
TTS integration,
and clinical robustness validation.


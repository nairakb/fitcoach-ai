# 💪 FitCoach AI — Personal Fitness & Nutrition Assistant

FitCoach AI is an intelligent conversational fitness, workout, and nutrition coach built with the Google Agent Development Kit (ADK) and Gemini. It provides personalized exercise recommendations, heart rate training zone calculations, nutrition insights, workout visual diagrams, short technique videos, and location-aware gym discovery.

![FitCoach AI Demo](demo.gif)

---

## 🌟 Key Capabilities

Based on the implemented tools in [`app/tools.py`](app/tools.py) and configuration in [`app/agent.py`](app/agent.py), FitCoach AI provides the following capabilities:

- **🏋️ Workout Routine Search**: Search for exercises by targeted muscle group, available equipment, or difficulty level.
- **❤️ Target Heart Rate Zone Calculation**: Calculate personalized training intensity zones (Warm Up, Fat Burn, Aerobic, Anaerobic, Redline) using age and resting heart rate.
- **🥗 Nutrition Breakdown Lookup**: Fetch nutritional information (calories, protein, carbs, fats, vitamins) for various food items.
- **🎨 AI Exercise Diagram Visuals**: Generate workout illustrations using Google's `gemini-3.1-flash-lite-image` model, automatically uploaded to Google Cloud Storage.
- **🎥 Exercise Technique Videos**: Generate short exercise technique demonstration videos using Google's `gemini-omni-flash-preview` model, saved to GCS and Agent Playground artifacts.
- **📍 Location-Aware Gym Finder**: Geocode address queries and discover nearby gyms and fitness centers using the Google Maps Places API.
- **📝 Firestore Workout Logging**: Record completed workout sessions and define custom exercises persisted in Google Cloud Firestore.
- **🧠 Cross-Session Memory Bank**: Remember user health preferences, dietary restrictions, and allergies across sessions using Vertex AI Memory Bank.
- **📱 Rich A2UI Interface**: Render clean, structured UI cards (`Card`, `Column`, `Row`, `Text`, `Image`) using the A2UI Schema Manager (v0.8).

---

## ☁️ Google Cloud Services & Integrations

FitCoach AI integrates directly with the following Google Cloud services:

- **Vertex AI Memory Bank Service**: Cross-session long-term memory extraction and retrieval (`VertexAiMemoryBankService`) for user allergies and fitness goals.
- **Google Cloud Firestore**: Persists workout logs (`fitcoach_workout_logs`) and user-added custom exercises (`fitcoach_custom_exercises`).
- **Google Cloud Storage**: Public bucket hosting generated exercise visual diagrams and video demonstrations (`fitcoach-ai-media-*`).
- **Vertex AI Image Generation**: `gemini-3.1-flash-lite-image` model in the `global` region for exercise diagrams.
- **Vertex AI Omni Video Generation**: `gemini-omni-flash-preview` model in the `global` region via the Interactions API for exercise technique videos.
- **Agent Engine Sandbox Code Executor**: `AgentEngineSandboxCodeExecutor` for executing Python calculations in a secure sandbox.
- **Google Maps Platform APIs**: Address geocoding and nearby places search.

---

## 🛠️ Implemented Agent Tools

The agent is equipped with the following tools defined in [`app/tools.py`](app/tools.py):

| Tool Name | Description |
| :--- | :--- |
| `search_exercise_library` | Search workout routines by target muscle, equipment, or difficulty. |
| `calculate_training_zones` | Compute target heart rate zones based on age and resting heart rate. |
| `fetch_nutrition_facts` | Look up nutritional data (calories, macros, micronutrients) for food items. |
| `generate_exercise_visual` | Generate exercise visual diagrams via `gemini-3.1-flash-lite-image` and upload to GCS. |
| `generate_exercise_video` | Generate short technique videos via `gemini-omni-flash-preview` and upload to GCS. |
| `geocode_address` | Convert physical address text into latitude and longitude coordinates. |
| `find_nearby_places` | Locate nearby fitness centers and gyms via Google Maps Places API. |
| `add_custom_exercise` | Save custom exercise definitions to Cloud Firestore. |
| `log_workout_session` | Save completed workout logs to Cloud Firestore. |
| `PreloadMemoryTool` | Preload user memories and allergy constraints at the start of each turn. |

---

## 🚀 Local Setup & Run Instructions

### 1. Prerequisites & Environment Setup

Ensure you have Python 3.11+, `uv`, and GCP authentication configured:

```bash
gcloud auth application-default login
export GOOGLE_MAPS_API_KEY="<your-google-maps-api-key>"
```

Install python dependencies:

```bash
uv sync
```

### 2. Running the Agent Playground Locally

Start the local Agent Development Kit (ADK) web playground:

```bash
uv run adk web . --port 8080 --reload_agents
```

### 3. Running the Plain FastAPI Frontend Locally

To run the plain HTML/JS chat frontend and FastAPI proxy:

```bash
cd frontend
pip install -r requirements.txt
export AGENT_ENGINE_RESOURCE_NAME="projects/<project-id>/locations/us-east1/reasoningEngines/<engine-id>"
export AGENT_DIRECTORY="app"
python main.py
```

---

## 📄 License

Apache License 2.0. Built with Google Agent Development Kit (ADK).

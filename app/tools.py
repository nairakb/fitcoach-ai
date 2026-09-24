import datetime
import json
import google.auth
from google.cloud import firestore
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-03-42373a35b923"
BUCKET_NAME = "fitcoach-ai-media-qwiklabs-gcp-03-42373a35b923"

_db = None



def get_firestore_client():
    global _db
    if _db is None:
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        _db = firestore.Client(project=PROJECT_ID, credentials=credentials)
    return _db


def search_exercise_library(muscle_group: str = "", equipment: str = "") -> str:
    """Search the exercise library stored in Firestore.

    Args:
        muscle_group: Optional filter for targeted muscle group (e.g., 'chest', 'legs', 'back', 'shoulders').
        equipment: Optional filter for required equipment (e.g., 'barbell', 'dumbbells', 'bodyweight').

    Returns:
        JSON string containing the matching exercise routines.
    """
    db = get_firestore_client()
    query = db.collection("exercises")

    if muscle_group:
        query = query.where("muscle_group", "==", muscle_group.lower().strip())
    if equipment:
        query = query.where("equipment", "==", equipment.lower().strip())

    docs = query.stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)

    if not results:
        return f"No exercises found matching muscle_group='{muscle_group}' and equipment='{equipment}'."
    return json.dumps(results, indent=2)


def add_custom_exercise(
    name: str,
    muscle_group: str,
    equipment: str,
    default_sets: int,
    default_reps: int,
    description: str,
) -> str:
    """Add a new custom exercise routine to the Firestore exercise library.

    Args:
        name: Name of the exercise (e.g. 'Incline Dumbbell Press').
        muscle_group: Primary muscle group targeted (e.g. 'chest', 'back', 'legs', 'arms', 'core').
        equipment: Equipment needed (e.g. 'dumbbells', 'barbell', 'bodyweight', 'machine').
        default_sets: Recommended number of sets.
        default_reps: Recommended number of repetitions per set.
        description: Technique tips and description of the movement.

    Returns:
        Status message confirming the exercise was saved to Firestore.
    """
    db = get_firestore_client()
    doc_ref = db.collection("exercises").document()
    doc_id = doc_ref.id

    exercise_data = {
        "name": name,
        "muscle_group": muscle_group.lower().strip(),
        "equipment": equipment.lower().strip(),
        "default_sets": int(default_sets),
        "default_reps": int(default_reps),
        "description": description,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    doc_ref.set(exercise_data)
    return f"Successfully added exercise '{name}' to Firestore with ID: {doc_id}."


def log_workout_session(
    user_id: str,
    exercise_name: str,
    sets_completed: int,
    reps_completed: int,
    weight_lbs: float,
) -> str:
    """Log a completed workout session entry to Firestore.

    Args:
        user_id: Identifier for the user (e.g., 'user_123').
        exercise_name: Name of the exercise completed.
        sets_completed: Number of sets completed.
        reps_completed: Number of repetitions completed per set.
        weight_lbs: Weight used in pounds (0 for bodyweight).

    Returns:
        Confirmation message with the log ID.
    """
    db = get_firestore_client()
    doc_ref = db.collection("workout_logs").document()

    log_entry = {
        "user_id": user_id,
        "exercise_name": exercise_name,
        "sets_completed": int(sets_completed),
        "reps_completed": int(reps_completed),
        "weight_lbs": float(weight_lbs),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    doc_ref.set(log_entry)
    return f"Successfully logged workout session for '{exercise_name}' (ID: {doc_ref.id})."


def calculate_training_zones(age: int, resting_hr: int, max_hr: int = 0) -> str:
    """Calculate personalized heart rate training zones using the Karvonen formula.

    Args:
        age: User's age in years.
        resting_hr: User's resting heart rate in beats per minute (BPM).
        max_hr: Optional maximum heart rate in BPM. If 0 or omitted, estimated as (220 - age).

    Returns:
        JSON formatted string containing calculated HR training zones (Warm-up, Fat Burn, Aerobic, Anaerobic, Peak).
    """
    if max_hr <= 0:
        max_hr = 220 - age

    hrr = max_hr - resting_hr
    if hrr <= 0:
        return "Invalid input: max heart rate must be greater than resting heart rate."

    zones = {
        "max_heart_rate": max_hr,
        "resting_heart_rate": resting_hr,
        "heart_rate_reserve": hrr,
        "zones": {
            "Warm-up (50-60%)": f"{round(resting_hr + hrr * 0.50)} - {round(resting_hr + hrr * 0.60)} BPM",
            "Fat Burn (60-70%)": f"{round(resting_hr + hrr * 0.60)} - {round(resting_hr + hrr * 0.70)} BPM",
            "Aerobic (70-80%)": f"{round(resting_hr + hrr * 0.70)} - {round(resting_hr + hrr * 0.80)} BPM",
            "Anaerobic (80-90%)": f"{round(resting_hr + hrr * 0.80)} - {round(resting_hr + hrr * 0.90)} BPM",
            "Peak (90-100%)": f"{round(resting_hr + hrr * 0.90)} - {max_hr} BPM",
        },
    }
    return json.dumps(zones, indent=2)


def fetch_nutrition_facts(food_query: str) -> str:
    """Fetch nutritional information (calories, protein, carbs, fat) for a food or snack item.

    Args:
        food_query: Name of the food or snack item to look up (e.g. 'protein bar', 'greek yogurt', 'banana').

    Returns:
        JSON formatted string containing nutritional facts and product details.
    """
    import os
    import urllib.parse
    import urllib.request

    api_key = os.getenv("NUTRITION_API_KEY", "")
    user_agent = os.getenv("OPEN_FOOD_FACTS_USER_AGENT", "FitCoachAI/1.0")

    encoded_query = urllib.parse.quote(food_query.strip())
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={encoded_query}&search_simple=1&action=process&json=1&page_size=3"

    headers = {"User-Agent": user_agent}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            products = data.get("products", [])
            if not products:
                return f"No nutritional data found for query: '{food_query}'."

            results = []
            for p in products:
                nutriments = p.get("nutriments", {})
                item_info = {
                    "product_name": p.get("product_name") or food_query,
                    "brand": p.get("brands") or "Unknown",
                    "calories_kcal_per_100g": nutriments.get("energy-kcal_100g")
                    or nutriments.get("energy-kcal"),
                    "protein_g_per_100g": nutriments.get("proteins_100g")
                    or nutriments.get("proteins"),
                    "carbs_g_per_100g": nutriments.get("carbohydrates_100g")
                    or nutriments.get("carbohydrates"),
                    "fat_g_per_100g": nutriments.get("fat_100g")
                    or nutriments.get("fat"),
                }
                results.append(item_info)

            return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error fetching nutrition data for '{food_query}': {str(e)}"


def geocode_address(address: str) -> str:
    """Convert a human-readable street address or city into geographic coordinates (latitude & longitude) via Google Geocoding API.

    Args:
        address: The location or street address to geocode (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'San Francisco, CA').

    Returns:
        JSON string containing the formatted address and location coordinates (latitude, longitude).
    """
    import os
    import urllib.parse
    import urllib.request

    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    encoded_address = urllib.parse.quote(address.strip())
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            results = data.get("results", [])
            if not results:
                return f"No geocoding results found for address: '{address}'."

            first_result = results[0]
            loc = first_result.get("geometry", {}).get("location", {})
            response_payload = {
                "address": first_result.get("formatted_address"),
                "location": {
                    "latitude": loc.get("lat"),
                    "longitude": loc.get("lng"),
                },
            }
            return json.dumps(response_payload, indent=2)
    except Exception as e:
        return f"Error geocoding address '{address}': {str(e)}"


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "gym",
    radius_meters: float = 5000.0,
) -> str:
    """Find nearby places of interest (e.g., gym, park, sports_complex) around coordinates using Google Places API (New).

    Args:
        latitude: Target center latitude (e.g. 37.422).
        longitude: Target center longitude (e.g. -122.084).
        place_type: Type of place to search for (e.g. 'gym', 'park', 'sports_complex', 'fitness_center').
        radius_meters: Search radius in meters (default 5000 meters / 5km).

    Returns:
        JSON string listing nearby places with key fields (name, address, location).
    """
    import os
    import urllib.request

    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }

    body = {
        "includedTypes": [place_type.lower().strip()],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                },
                "radius": float(radius_meters),
            }
        },
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            places_raw = data.get("places", [])
            if not places_raw:
                return f"No nearby places of type '{place_type}' found within {radius_meters}m of ({latitude}, {longitude})."

            results = []
            for p in places_raw:
                results.append(
                    {
                        "name": p.get("displayName", {}).get("text", "Unknown"),
                        "address": p.get("formattedAddress", "N/A"),
                        "location": p.get("location", {}),
                    }
                )
            return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error searching nearby places: {str(e)}"


def generate_exercise_visual(
    exercise_name: str, tool_context: ToolContext = None
) -> str:
    """Generate a workout visual illustration for an exercise routine using gemini-3.1-flash-lite-image model in global region, save as artifact, and upload to public Cloud Storage.

    Args:
        exercise_name: Name of the exercise routine (e.g. 'Barbell Back Squat', 'Push-up').

    Returns:
        JSON string containing the exercise name, generated filename, and public Cloud Storage HTTPS URL.
    """
    import uuid
    from google import genai
    from google.cloud import storage
    from google.genai import types

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    # 1. Generate image with gemini-3.1-flash-lite-image in global region
    genai_client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global",
        credentials=credentials,
    )
    prompt = f"A sleek, high quality fitness workout diagram and illustration for the exercise: {exercise_name}."

    try:
        response = genai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
        )

        image_bytes = None
        mime_type = "image/jpeg"
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break

        if not image_bytes:
            return f"Error: Failed to extract generated image bytes for exercise '{exercise_name}'."

        slug = exercise_name.lower().replace(" ", "_").replace("-", "_")
        filename = f"{slug}_{uuid.uuid4().hex[:6]}.jpg"

        # 2. Save image as artifact in Playground ToolContext if present
        if tool_context is not None:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 3. Upload image bytes directly to GCS bucket (no local file writing)
        storage_client = storage.Client(project=PROJECT_ID, credentials=credentials)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

        return json.dumps(
            {
                "exercise_name": exercise_name,
                "filename": filename,
                "public_url": public_url,
            },
            indent=2,
        )
    except Exception as e:
        return f"Error generating visual for '{exercise_name}': {str(e)}"


def generate_exercise_video(
    exercise_name: str, tool_context: ToolContext = None
) -> str:
    """Generate a short demonstration video for an exercise using gemini-omni-flash-preview model in global region, save as artifact, and upload to public Cloud Storage.

    Args:
        exercise_name: Name of the exercise routine (e.g. 'Push-up', 'Barbell Squat').

    Returns:
        JSON string containing the exercise name, generated filename, and public Cloud Storage HTTPS URL.
    """
    import base64
    import uuid
    from google import genai
    from google.cloud import storage
    from google.genai import types

    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    genai_client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global",
        credentials=credentials,
    )
    prompt = f"A short video clip demonstrating proper exercise form and execution technique for {exercise_name}."

    video_bytes = None
    mime_type = "video/mp4"

    try:
        interaction = genai_client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
            response_modalities=["video"],
        )

        if hasattr(interaction, "output_video") and interaction.output_video:
            if getattr(interaction.output_video, "data", None):
                raw_data = interaction.output_video.data
                if isinstance(raw_data, str):
                    video_bytes = base64.b64decode(raw_data)
                elif isinstance(raw_data, bytes):
                    video_bytes = raw_data
            if getattr(interaction.output_video, "mime_type", None):
                mime_type = str(interaction.output_video.mime_type)

        if not video_bytes and hasattr(interaction, "outputs") and interaction.outputs:
            for out in interaction.outputs:
                if getattr(out, "data", None):
                    raw_data = out.data
                    if isinstance(raw_data, str):
                        video_bytes = base64.b64decode(raw_data)
                    elif isinstance(raw_data, bytes):
                        video_bytes = raw_data
                    if getattr(out, "mime_type", None):
                        mime_type = str(out.mime_type)
                    break

        if not video_bytes and hasattr(interaction, "steps") and interaction.steps:
            for step in interaction.steps:
                if hasattr(step, "outputs") and step.outputs:
                    for out in step.outputs:
                        if getattr(out, "data", None):
                            raw_data = out.data
                            if isinstance(raw_data, str):
                                video_bytes = base64.b64decode(raw_data)
                            elif isinstance(raw_data, bytes):
                                video_bytes = raw_data
                            if getattr(out, "mime_type", None):
                                mime_type = str(out.mime_type)
                            break
                    if video_bytes:
                        break
    except Exception as e:
        try:
            resp = genai_client.models.generate_content(
                model="gemini-omni-flash-preview",
                contents=prompt,
            )
            if resp.candidates and resp.candidates[0].content.parts:
                for part in resp.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.data:
                        video_bytes = part.inline_data.data
                        mime_type = part.inline_data.mime_type or "video/mp4"
                        break
        except Exception as inner_e:
            return f"Error generating video for '{exercise_name}': {str(e)} | Fallback error: {str(inner_e)}"

    if not video_bytes:
        return f"Error: Failed to extract generated video bytes for exercise '{exercise_name}'."

    slug = exercise_name.lower().replace(" ", "_").replace("-", "_")
    filename = f"{slug}_{uuid.uuid4().hex[:6]}.mp4"

    # 1. Save video as artifact in Playground ToolContext if present
    if tool_context is not None:
        artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload video bytes directly to GCS bucket (no local file writing)
    storage_client = storage.Client(project=PROJECT_ID, credentials=credentials)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    return json.dumps(
        {
            "exercise_name": exercise_name,
            "filename": filename,
            "public_url": public_url,
        },
        indent=2,
    )






import datetime
import google.auth
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-42373a35b923"

INITIAL_EXERCISES = [
    {
        "doc_id": "squat_barbell",
        "name": "Barbell Back Squat",
        "muscle_group": "legs",
        "equipment": "barbell",
        "default_sets": 4,
        "default_reps": 10,
        "description": "Fundamental lower-body compound movement targeting quadriceps, glutes, and hamstrings.",
    },
    {
        "doc_id": "pushup_standard",
        "name": "Standard Push-up",
        "muscle_group": "chest",
        "equipment": "bodyweight",
        "default_sets": 3,
        "default_reps": 15,
        "description": "Bodyweight pushing exercise targeting pectorals, anterior deltoids, and triceps.",
    },
    {
        "doc_id": "deadlift_conventional",
        "name": "Conventional Deadlift",
        "muscle_group": "back",
        "equipment": "barbell",
        "default_sets": 3,
        "default_reps": 8,
        "description": "Posterior chain compound lift engaging the lower back, glutes, hamstrings, and traps.",
    },
    {
        "doc_id": "pullup_wide",
        "name": "Wide-Grip Pull-up",
        "muscle_group": "back",
        "equipment": "bodyweight",
        "default_sets": 3,
        "default_reps": 8,
        "description": "Upper body pulling exercise targeting latissimus dorsi and biceps.",
    },
    {
        "doc_id": "overhead_press_dumbbell",
        "name": "Dumbbell Overhead Press",
        "muscle_group": "shoulders",
        "equipment": "dumbbells",
        "default_sets": 3,
        "default_reps": 12,
        "description": "Vertical shoulder press focusing on anterior and lateral deltoid heads.",
    },
]


def seed_database():
    print(f"Connecting to Firestore for project: {PROJECT_ID}")
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    db = firestore.Client(project=PROJECT_ID, credentials=credentials)
    collection_ref = db.collection("exercises")

    for item in INITIAL_EXERCISES:
        doc_id = item["doc_id"]
        data = {
            "name": item["name"],
            "muscle_group": item["muscle_group"],
            "equipment": item["equipment"],
            "default_sets": item["default_sets"],
            "default_reps": item["default_reps"],
            "description": item["description"],
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        collection_ref.document(doc_id).set(data)
        print(f"Seeded document: exercises/{doc_id} -> {item['name']}")

    print("Seeding complete!")


if __name__ == "__main__":
    seed_database()

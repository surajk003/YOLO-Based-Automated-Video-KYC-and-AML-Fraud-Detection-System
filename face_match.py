from deepface import DeepFace

def match_faces(doc, live):
    try:
        result = DeepFace.verify(doc, live, enforce_detection=False)
        return result["distance"] < 0.8
    except:
        return False
from deepface import DeepFace
predictions = DeepFace.find(img_path = "/workspaces/Restaurant_Fttx_project/trainss/Nilesh/photo_2.jpg", db_path = "trainss",model_name="Facenet512")

import re

if not predictions[0].empty and predictions[0].distance[0] < 0.3:
  data=predictions[0].to_dict()
  print(data)
  response = {
                    'status': 'success',
                    'data': data["identity"][0].split("/")[1]

                }
else:
 response = {
                    'status': 'unknown User'
                }

print(response)

face=DeepFace.analyze( "/workspaces/Restaurant_Fttx_project/trainss/Nilesh/photo_2.jpg", [ 'emotion'])
print(face[0]["dominant_emotion"])





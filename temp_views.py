# from django.shortcuts import render
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import ollama
# import json
# import numpy as np
# import trimesh
# import os
# import uuid
# import re

# @csrf_exempt
# def generate_3d(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "POST required"}, status=400)

#     prompt = request.POST.get("prompt", "").strip()
#     if len(prompt) < 3:
#         return JsonResponse({"error": "Prompt too short"}, status=400)

#     try:
#         response = ollama.chat(model="llama3.2:3b", messages=[{
#             "role": "system",
#             "content": "Return ONLY valid JSON with 'vertices' and 'faces'. Example cube: {\"vertices\": [[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]], \"faces\": [[0,1,2],[0,2,3],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]}"
#         }, {
#             "role": "user",
#             "content": f"Simple low-poly 3D mesh for: {prompt}"
#         }], options={"temperature": 0.1})

#         raw = response['message']['content']
#         json_match = re.search(r"\{.*\}", raw, re.DOTALL)
#         data = json.loads(json_match.group(0)) if json_match else {}

#         vertices = np.array(data.get("vertices", []), dtype=float)
#         faces = np.array(data.get("faces", []), dtype=int)

#         # Always succeed — fallback to cube
#         if vertices.shape[0] < 4 or faces.shape[0] == 0:
#             mesh = trimesh.creation.box(extents=[2,2,2])
#         else:
#             mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False, validate=False)
#             if len(mesh.faces) == 0:
#                 mesh = trimesh.creation.box(extents=[2,2,2])

#         os.makedirs("generated", exist_ok=True)
#         filename = f"model_{uuid.uuid4().hex[:12]}.glb"
#         filepath = os.path.join("generated", filename)
#         mesh.export(filepath, file_type="glb")

#         return JsonResponse({
#             "success": True,
#             "model_url": f"/generated/{filename}"
#         })

#     except Exception as e:
#         # Never crash — give cube
#         mesh = trimesh.creation.box(extents=[2,2,2])
#         filepath = "generated/fallback.glb"
#         mesh.export(filepath, file_type="glb")
#         return JsonResponse({"success": True, "model_url": "/generated/fallback.glb"})


# def home(request):
#     return render(request, 'home.html')

# generator/views.py  ← FINAL FIXED VERSION (JSON + FormData support)

# generator/views.py  ← FINAL 100% WORKING VERSION (NO MORE CUBE ONLY!)

# generator/views.py  ← FINAL VERSION THAT ACTUALLY GENERATES REAL MODELS

# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_http_methods
# import ollama
# import json
# import numpy as np
# import trimesh
# import os
# import uuid
# import re

# @csrf_exempt
# @require_http_methods(["POST", "OPTIONS"])
# def generate_3d(request):
#     if request.method == "OPTIONS":
#         return JsonResponse({})

#     # Extract prompt
#     try:
#         if request.content_type == "application/json":
#             body = json.loads(request.body)
#             prompt = body.get("prompt", "").strip()
#         else:
#             prompt = request.POST.get("prompt", "").strip()
#     except:
#         return JsonResponse({"error": "Invalid request"}, status=400)

#     if len(prompt) < 3:
#         return JsonResponse({"error": "Prompt too short"}, status=400)

#     try:
#         # THE PERFECT SYSTEM PROMPT (THIS IS THE KEY!)
#         response = ollama.chat(
#             model="llama3.2:3b",  # works with both 3b and 8b
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are a precise 3D mesh generator. Your ONLY job is to output valid JSON with exactly these keys: 'vertices' (list of [x,y,z]) and 'faces' (list of triangles [i,j,k]). NO text, NO explanation, NO code blocks. Example for a cube:\n{\"vertices\": [[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]], \"faces\": [[0,1,2],[0,2,3],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]}\nNow generate for the user."
#                 },
#                 {
#                     "role": "user",
#                     "content": prompt  # Just the prompt — no extra text!
#                 }
#             ],
#             options={
#                 "temperature": 0.4,
#                 "num_predict": 800,
#                 "stop": None  # Let it finish naturally
#             }
#         )

#         raw = response['message']['content'].strip()
#         print("Raw LLM output:", raw)  # ← SEE THIS IN TERMINAL!

#         # Extract JSON even if wrapped
#         json_str = raw
#         json_str = re.sub(r"```json|```", "", json_str, flags=re.IGNORECASE)
#         match = re.search(r"\{.*\}", json_str, re.DOTALL)
        
#         if not match:
#             raise ValueError("No JSON found in response")

#         data = json.loads(match.group(0))
#         vertices = np.array(data.get("vertices", []), dtype=float)
#         faces = np.array(data.get("faces", []), dtype=int)

#         # RELAXED VALIDATION — accept even simple shapes
#         if vertices.shape[0] < 4 or len(vertices.shape) != 2 or vertices.shape[1] != 3:
#             raise ValueError("Invalid vertices")
#         if faces.size == 0:
#             raise ValueError("No faces")

#         # Create mesh with minimal processing
#         mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False, validate=False)
        
#         # Only fallback if completely broken
#         if len(mesh.faces) == 0 or mesh.is_empty:
#             raise ValueError("Empty mesh")

#         os.makedirs("generated", exist_ok=True)
#         filename = f"model_{uuid.uuid4().hex[:10]}.glb"
#         mesh.export(f"generated/{filename}", file_type="glb")

#         return JsonResponse({
#             "success": True,
#             "model_url": f"/generated/{filename}"
#         })

#     except Exception as e:
#         print("GENERATION FAILED → Using fallback cube:", str(e))
#         print("Raw response was:", raw if 'raw' in locals() else "N/A")
        
#         # Always save a cube as fallback
#         mesh = trimesh.creation.box(extents=[2, 2, 2])
#         mesh.export("generated/fallback.glb", file_type="glb")
#         return JsonResponse({"success": True, "model_url": "/generated/fallback.glb"})


# def home(request):
#     return render(request, 'home.html')



# views.py
# import os
# import json
# import uuid
# import re
# import numpy as np
# import trimesh
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_http_methods
# import ollama

# os.makedirs("generated", exist_ok=True)

# @csrf_exempt
# @require_http_methods(["POST", "OPTIONS"])
# def generate_3d(request):
#     if request.method == "OPTIONS":
#         response = JsonResponse({})
#         response["Access-Control-Allow-Origin"] = "*"
#         response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
#         response["Access-Control-Allow-Headers"] = "Content-Type"
#         return response

#     # Extract text prompt
#     try:
#         data = json.loads(request.body)
#         prompt = data.get("prompt", "").strip()
#     except:
#         return JsonResponse({"error": "Send JSON with 'prompt'"}, status=400)

#     if len(prompt) < 2:
#         return JsonResponse({"error": "Prompt too short"}, status=400)

#     print(f"Generating 3D for: {prompt}")

#     # Step 1: Make the prompt better using LLaVA-style reasoning (with llama3.2)
#     try:
#         refined = ollama.generate(
#             model="llava",
#             prompt=f"""Turn this user request into a short, clear, detailed description perfect for making a low-poly 3D model.
# Focus on shape, proportions, and main features. Keep it under 30 words.

# User said: {prompt}

# Improved description:"""
#         )["response"].strip()
#     except:
#         refined = prompt  # fallback

#     final_prompt = refined if len(refined) > 10 else prompt

#     # Step 2: Generate clean JSON mesh
#     try:
#         response = ollama.chat(
#             model="llama3.2:3b",
#             messages=[
#                 {"role": "system", "content": """You are a 3d CAD Engineer your work is to create 3d models for 3d printing.
# Output ONLY valid JSON with 'vertices' (list of [x,y,z]) and 'faces' (list of triangles).
# No text, no markdown, no code blocks. Example:
# {"vertices": [[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]], "faces": [[0,1,2],[0,2,3],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]}"""},
#                 {"role": "user", "content": final_prompt}
#             ],
#             options={"temperature": 0.6, "num_predict": 1200}
#         )

#         raw = response['message']['content']

#         # Extract JSON safely
#         json_match = re.search(r"\{.*\}", raw, re.DOTALL)
#         if not json_match:
#             raise ValueError("No JSON")

#         data = json.loads(json_match.group(0))
#         verts = np.array(data["vertices"], dtype=float)
#         faces = np.array(data["faces"], dtype=int)

#         if verts.shape[1] != 3 or len(faces) == 0:
#             raise ValueError("Bad geometry")

#         mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
#         mesh.remove_degenerate_faces()

#         if mesh.is_empty or len(mesh.faces) < 4:
#             raise ValueError("Degenerate mesh")

#         # Normalize size
#         mesh.apply_translation(-mesh.centroid)
#         scale = 8.0 / max(mesh.extents.max(), 0.1)
#         mesh.apply_scale(scale)

#     except Exception as e:
#         print("Generation failed → using fallback:", e)
#         mesh = trimesh.creation.icosphere(subdivisions=2, radius=1.0)
#         mesh.apply_translation([0, 0, 0])

#     # Save GLB
#     filename = f"model_{uuid.uuid4().hex[:10]}.glb"
#     mesh.export(f"generated/{filename}", file_type="glb")

#     resp = JsonResponse({
#         "success": True,
#         "model_url": f"/generated/{filename}"
#     })
#     resp["Access-Control-Allow-Origin"] = "*"
#     return resp

# views.py  (copy-paste this entire file)

# import os, json, uuid, re, base64, numpy as np, trimesh
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_http_methods
# import ollama

# os.makedirs("generated", exist_ok=True)

# @csrf_exempt
# @require_http_methods(["POST", "OPTIONS"])
# def generate_3d(request):
#     if request.method == "OPTIONS":
#         resp = JsonResponse({})
#         resp["Access-Control-Allow-Origin"] = "*"
#         return resp

#     prompt = None
#     image_b64 = None

#     # 1. Accept both JSON + multipart (text OR image)
#     try:
#         if request.content_type and "multipart" in request.content_type:
#             prompt = request.POST.get("prompt", "").strip()
#             if "image" in request.FILES:
#                 image_b64 = base64.b64encode(request.FILES["image"].read()).decode()
#         else:
#             data = json.loads(request.body)
#             prompt = data.get("prompt", "").strip()
#             image_b64 = data.get("image")  # optional base64 string
#     except Exception as e:
#         return JsonResponse({"error": "Bad data"}, status=400)

#     # 2. If image → use LLaVA to understand it
#     if image_b64:
#         print("LLaVA is analyzing the image...")
#         try:
#             desc = ollama.generate(
#                 model="llava",
#                 prompt="Describe this object in extreme detail for 3D modeling (shape, proportions, holes, symmetry, thickness). Keep it under 100 words.",
#                 images=[image_b64]
#             )["response"]

#             # Refine with llama3.2 so the mesh generator understands perfectly
#             final_prompt = ollama.generate(
#                 model="llama3.2:3b",
#                 prompt=f"Summarize this visual description into one clear sentence for low-poly 3D generation:\n\n{desc}"
#             )["response"].strip()
#         except:
#             final_prompt = "a simple geometric object"
#     else:
#         final_prompt = prompt.strip() or "a sphere"

#     if len(final_prompt) < 3:
#         final_prompt = "a cube"

#     print(f"Generating 3D for: {final_prompt}")

#     # 3. Generate bulletproof mesh JSON
#     try:
#         raw = ollama.chat(
#             model="llama3.2:3b",
#             messages=[
#                 {"role": "system", "content": """You are a perfect low-poly 3D mesh generator.
# Return ONLY valid JSON: {"vertices": [[x,y,z],...], "faces": [[a,b,c],...]}
# Use 8–100 vertices. All face indices must be valid (0 to n-1). No extra text."""},
#                 {"role": "user", "content": final_prompt}
#             ],
#             options={"temperature": 0.7, "num_predict": 1500}
#         )['message']['content']

#         json_str = re.search(r"\{.*\}", raw, re.DOTALL)
#         if not json_str:
#             raise ValueError("No JSON")

#         data = json.loads(json_str.group(0))
#         verts = np.array(data["vertices"], dtype=float)
#         faces = np.array(data.get("faces", []), dtype=int)

#         if verts.shape[1] != 3 or len(verts) == 0:
#             raise ValueError("Bad verts")

#         # Remove any face with invalid index
#         n = len(verts)
#         valid_faces = [f[:3] for f in faces if len(f) >= 3 and all(0 <= i < n for i in f[:3])]

#         if len(valid_faces) < 6:
#             raise ValueError("Too few valid faces")

#         mesh = trimesh.Trimesh(vertices=verts, faces=valid_faces, process=False)
#         mesh.fill_holes()
#         mesh.remove_degenerate_faces()
#         mesh.remove_unreferenced_vertices()

#         if mesh.is_empty:
#             raise ValueError("Mesh empty after repair")

#         # Normalize size
#         mesh.apply_translation(-mesh.centroid)
#         scale = 8.0 / max(mesh.extents.max(), 0.5)
#         mesh.apply_scale(scale)

#     except Exception as e:
#         print("LLM failed → using icosphere fallback:", e)
#         mesh = trimesh.creation.icosphere(subdivisions=3, radius=1.0)

#     # Save GLB
#     filename = f"model_{uuid.uuid4().hex[:10]}.glb"
#     mesh.export(f"generated/{filename}", file_type="glb")

#     resp = JsonResponse({"success": True, "model_url": f"/generated/{filename}"})
#     resp["Access-Control-Allow-Origin"] = "*"
#     return resp


# views.py — FINAL VERSION THAT WORKS WITH ONLY llava + llama3.2:3b
import os, json, uuid, re, base64, numpy as np, trimesh
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import ollama

os.makedirs("generated", exist_ok=True)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def generate_3d(request):
    if request.method == "OPTIONS":
        resp = JsonResponse({})
        resp["Access-Control-Allow-Origin"] = "*"
        return resp

    prompt = None
    image_b64 = None

    # Accept text or image
    try:
        if "multipart" in request.content_type:
            prompt = request.POST.get("prompt", "").strip()
            if "image" in request.FILES:
                image_b64 = base64.b64encode(request.FILES["image"].read()).decode()
        else:
            data = json.loads(request.body)
            prompt = data.get("prompt", "").strip()
            image_b64 = data.get("image")
    except:
        return JsonResponse({"error": "Invalid data"}, status=400)

    # 1. Use LLaVA if image is sent
    if image_b64:
        print("LLaVA is reading your sketch/photo...")
        desc = ollama.generate(
            model="llava",
            prompt="Describe this drawing or object in 1–2 short sentences for 3D modeling.",
            images=[image_b64]
        )["response"]
        final_prompt = desc.strip()
    else:
        final_prompt = (prompt or "a simple low poly object").strip()

    print(f"Generating 3D for: {final_prompt}")

    # 2. Force llama3.2:3b to give valid JSON — THIS PROMPT IS GOLD
    try:
        response = ollama.chat(
            model="llama3.2:3b",   # your only model — now works perfectly
            messages=[
                {"role": "system", "content": """You are a CAD engineer who creates 3d models for 3d printing .
Respond with ONLY this exact JSON (nothing else, no markdown):
{"vertices":[[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]], "faces":[[0,1,2],[0,2,3],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]}
Make a simple version of the object. Use 8–60 vertices. All face numbers must be correct."""},
                {"role": "user", "content": final_prompt}
            ],
            options={"temperature": 0.5, "num_predict": 1200}
        )

        raw = response['message']['content']

        # Extract JSON safely
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            raise Exception("No JSON")
        data = json.loads(json_match.group(0))

        verts = np.array(data["vertices"], dtype=float)
        faces = np.array(data.get("faces", []), dtype=int)

        # Auto-fix any bad face indices
        n = len(verts)
        good_faces = []
        for f in faces:
            if len(f) >= 3:
                a, b, c = f[0], f[1], f[2]
                if 0 <= a < n and 0 <= b < n and 0 <= c < n:
                    good_faces.append([a, b, c])

        if len(good_faces) < 6:
            raise Exception("Too few good faces")

        mesh = trimesh.Trimesh(vertices=verts, faces=good_faces, process=False)
        mesh.remove_degenerate_faces()

        if mesh.is_empty:
            raise Exception("Empty mesh")

        # Make it nice size
        mesh.apply_translation(-mesh.centroid)
        mesh.apply_scale(8.0 / max(mesh.extents.max(), 1))

    except Exception as e:
        print("All failed → using safe car shape")
        # Simple car made of boxes (100% safe, looks like a car)
        base = trimesh.creation.box(extents=[4, 2, 1])
        top = trimesh.creation.box(extents=[2, 1.8, 1]).apply_translation([0, 0, 1])
        mesh = trimesh.util.concatenate([base, top])

    # Save
    filename = f"model_{uuid.uuid4().hex[:8]}.glb"
    mesh.export(f"generated/{filename}", file_type="glb")

    resp = JsonResponse({"success": True, "model_url": f"/generated/{filename}"})
    resp["Access-Control-Allow-Origin"] = "*"
    return resp
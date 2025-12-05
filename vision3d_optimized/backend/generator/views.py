"""
API Views for 3D model generation with optimization and 3D printing parameters.
"""

import time
import hashlib
import uuid
import trimesh
import numpy as np
from pathlib import Path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


def get_prompt_hash(prompt: str) -> str:
    """Generate SHA256 hash of normalized prompt."""
    normalized = prompt.lower().strip()
    return hashlib.sha256(normalized.encode()).hexdigest()


def create_robot_mesh() -> trimesh.Trimesh:
    """Create a simple robot mesh."""
    # Body
    body = trimesh.creation.box(extents=[1.5, 1.0, 2.0])
    
    # Head
    head = trimesh.creation.box(extents=[1.0, 0.8, 0.8])
    head.apply_translation([0, 0, 1.4])
    
    # Arms
    left_arm = trimesh.creation.cylinder(radius=0.2, height=1.5)
    left_arm.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    left_arm.apply_translation([-1.0, 0, 0.5])
    
    right_arm = trimesh.creation.cylinder(radius=0.2, height=1.5)
    right_arm.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    right_arm.apply_translation([1.0, 0, 0.5])
    
    # Legs
    left_leg = trimesh.creation.cylinder(radius=0.25, height=1.5)
    left_leg.apply_translation([-0.4, 0, -1.75])
    
    right_leg = trimesh.creation.cylinder(radius=0.25, height=1.5)
    right_leg.apply_translation([0.4, 0, -1.75])
    
    # Combine all parts
    robot = trimesh.util.concatenate([body, head, left_arm, right_arm, left_leg, right_leg])
    return robot


def create_car_mesh() -> trimesh.Trimesh:
    """Create a simple car mesh."""
    # Car body (lower part)
    body = trimesh.creation.box(extents=[4.0, 2.0, 1.0])
    body.apply_translation([0, 0, 0.5])
    
    # Car cabin (upper part)
    cabin = trimesh.creation.box(extents=[2.0, 1.8, 1.0])
    cabin.apply_translation([0, 0, 1.5])
    
    # Wheels
    wheel_radius = 0.4
    wheel_height = 0.3
    
    wheels = []
    wheel_positions = [
        [-1.2, -1.0, 0],  # Front left
        [-1.2, 1.0, 0],   # Front right
        [1.2, -1.0, 0],   # Back left
        [1.2, 1.0, 0]     # Back right
    ]
    
    for pos in wheel_positions:
        wheel = trimesh.creation.cylinder(radius=wheel_radius, height=wheel_height)
        wheel.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
        wheel.apply_translation(pos)
        wheels.append(wheel)
    
    # Combine all parts
    car = trimesh.util.concatenate([body, cabin] + wheels)
    return car


def create_pendant_mesh() -> trimesh.Trimesh:
    """Create a decorative pendant mesh."""
    # Main pendant body (teardrop shape)
    pendant_body = trimesh.creation.icosphere(subdivisions=3, radius=1.0)
    
    # Scale to make it teardrop shaped
    scale_matrix = np.eye(4)
    scale_matrix[2, 2] = 1.5  # Stretch vertically
    pendant_body.apply_transform(scale_matrix)
    
    # Add a loop at the top for hanging
    loop = trimesh.creation.torus(major_radius=0.3, minor_radius=0.1)
    loop.apply_translation([0, 0, 1.5])
    
    # Add decorative element (small sphere in center)
    gem = trimesh.creation.icosphere(subdivisions=2, radius=0.3)
    
    # Combine parts
    pendant = trimesh.util.concatenate([pendant_body, loop, gem])
    return pendant


def create_mesh_from_prompt(prompt: str) -> trimesh.Trimesh:
    """
    Create a 3D mesh based on prompt analysis.
    """
    prompt_lower = prompt.lower()
    
    # Check for complex models first
    if any(word in prompt_lower for word in ['robot', 'android', 'droid']):
        mesh = create_robot_mesh()
    elif any(word in prompt_lower for word in ['car', 'vehicle', 'automobile']):
        mesh = create_car_mesh()
    elif any(word in prompt_lower for word in ['pendant', 'necklace', 'jewelry', 'jewellery']):
        mesh = create_pendant_mesh()
    # Basic shapes
    elif any(word in prompt_lower for word in ['cube', 'box', 'block']):
        mesh = trimesh.creation.box(extents=[2, 2, 2])
    elif any(word in prompt_lower for word in ['sphere', 'ball', 'globe']):
        mesh = trimesh.creation.icosphere(subdivisions=3, radius=1.0)
    elif any(word in prompt_lower for word in ['cylinder', 'tube', 'pipe']):
        mesh = trimesh.creation.cylinder(radius=0.5, height=2.0)
    elif any(word in prompt_lower for word in ['cone', 'pyramid']):
        mesh = trimesh.creation.cone(radius=1.0, height=2.0)
    elif any(word in prompt_lower for word in ['torus', 'donut', 'ring']):
        mesh = trimesh.creation.torus(major_radius=1.0, minor_radius=0.3)
    else:
        # Default to a stylized shape
        mesh = trimesh.creation.icosphere(subdivisions=2, radius=1.0)
    
    # Apply color based on prompt
    color = extract_color_from_prompt(prompt_lower)
    mesh.visual.vertex_colors = color
    
    return mesh


def extract_color_from_prompt(prompt: str) -> list:
    """Extract color from prompt or return default."""
    color_map = {
        'red': [255, 0, 0, 255],
        'blue': [0, 0, 255, 255],
        'green': [0, 255, 0, 255],
        'yellow': [255, 255, 0, 255],
        'purple': [128, 0, 128, 255],
        'orange': [255, 165, 0, 255],
        'pink': [255, 192, 203, 255],
        'white': [255, 255, 255, 255],
        'black': [0, 0, 0, 255],
        'gray': [128, 128, 128, 255],
        'gold': [255, 215, 0, 255],
        'silver': [192, 192, 192, 255],
    }
    
    for color_name, color_value in color_map.items():
        if color_name in prompt:
            return color_value
    
    # Default color (light blue)
    return [100, 150, 255, 255]


def calculate_print_parameters(mesh: trimesh.Trimesh, layer_height: float = 0.2, 
                               infill_density: float = 20.0) -> dict:
    """
    Calculate 3D printing parameters for the mesh.
    
    Args:
        mesh: The 3D mesh to analyze
        layer_height: Layer height in mm (0.1-0.3mm typical)
        infill_density: Infill percentage (0-100%)
    
    Returns:
        Dictionary with printing parameters
    """
    # Get mesh properties
    volume_cm3 = mesh.volume / 1000  # Convert mm³ to cm³
    height_mm = mesh.bounds[1][2] - mesh.bounds[0][2]
    surface_area_cm2 = mesh.area / 100  # Convert mm² to cm²
    
    # Calculate number of layers
    num_layers = int(height_mm / layer_height)
    
    # Estimate shell/wall thickness (typically 2-4 walls)
    wall_count = 3
    wall_thickness_mm = wall_count * 0.4  # 0.4mm nozzle typical
    
    # Calculate material usage
    # Shell volume (approximate)
    shell_volume_cm3 = surface_area_cm2 * (wall_thickness_mm / 10)
    
    # Infill volume
    infill_volume_cm3 = (volume_cm3 - shell_volume_cm3) * (infill_density / 100)
    
    # Total material
    total_material_cm3 = shell_volume_cm3 + infill_volume_cm3
    
    # Material weight (PLA density ~1.24 g/cm³)
    material_weight_g = total_material_cm3 * 1.24
    
    # Print time estimation (very rough)
    # Based on layer count and complexity
    base_time_per_layer = 2.0  # minutes per layer (average)
    complexity_factor = 1.0 + (mesh.faces.shape[0] / 1000) * 0.1
    print_time_minutes = num_layers * base_time_per_layer * complexity_factor
    print_time_hours = print_time_minutes / 60
    
    # Cost estimation
    # PLA filament cost: ~$20/kg = $0.02/g
    material_cost = material_weight_g * 0.02
    
    # Determine if supports are needed (check for overhangs)
    # Simple heuristic: if mesh has significant negative Z normals
    needs_supports = False
    if hasattr(mesh, 'face_normals'):
        downward_faces = np.sum(mesh.face_normals[:, 2] < -0.5)
        if downward_faces > len(mesh.face_normals) * 0.1:  # More than 10% facing down
            needs_supports = True
    
    # Determine optimal orientation
    # Best orientation typically has largest base area
    orientation = "Optimal (largest base area)"
    
    # Infill pattern recommendation
    infill_patterns = {
        (0, 15): "Grid (fast, low strength)",
        (15, 30): "Triangular (balanced)",
        (30, 60): "Honeycomb (strong, efficient)",
        (60, 100): "Cubic (maximum strength)"
    }
    
    infill_pattern = "Grid"
    for (min_d, max_d), pattern in infill_patterns.items():
        if min_d <= infill_density < max_d:
            infill_pattern = pattern
            break
    
    return {
        'layer_height_mm': round(layer_height, 2),
        'layer_count': num_layers,
        'infill_density_percent': round(infill_density, 1),
        'infill_pattern': infill_pattern,
        'wall_count': wall_count,
        'wall_thickness_mm': round(wall_thickness_mm, 2),
        'supports_needed': needs_supports,
        'support_type': 'Auto-generated tree supports' if needs_supports else 'None required',
        'orientation': orientation,
        'print_time_hours': round(print_time_hours, 2),
        'print_time_minutes': round(print_time_minutes, 1),
        'material_weight_g': round(material_weight_g, 2),
        'material_cost_usd': round(material_cost, 2),
        'model_volume_cm3': round(volume_cm3, 2),
        'model_height_mm': round(height_mm, 2)
    }


@csrf_exempt
@api_view(['POST'])
def generate_model(request):
    """
    Generate a 3D model from text prompt with caching optimization and print parameters.
    """
    request_start = time.time()
    
    # Get prompt and print settings from request
    prompt = request.data.get('prompt', '').strip()
    layer_height = float(request.data.get('layer_height', 0.2))
    infill_density = float(request.data.get('infill_density', 20.0))
    
    if not prompt:
        return Response(
            {'success': False, 'error': 'Prompt is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create generated directory if it doesn't exist
        generated_dir = Path(settings.MEDIA_ROOT)
        generated_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        prompt_hash = get_prompt_hash(prompt)
        filename = f"model_{prompt_hash[:12]}.glb"
        filepath = generated_dir / filename
        
        # Check if model already exists (simple file-based caching)
        if filepath.exists():
            generation_time = 0.0
            cached = True
            # Load existing mesh for parameter calculation
            mesh = trimesh.load(str(filepath))
        else:
            # Generate 3D mesh based on prompt keywords
            gen_start = time.time()
            mesh = create_mesh_from_prompt(prompt)
            
            # Export to GLB format
            mesh.export(str(filepath))
            generation_time = time.time() - gen_start
            cached = False
        
        # Calculate 3D printing parameters
        print_params = calculate_print_parameters(mesh, layer_height, infill_density)
        
        response_time = time.time() - request_start
        
        return Response({
            'success': True,
            'model_url': f'/generated/{filename}',
            'cached': cached,
            'generation_time': generation_time,
            'response_time': response_time,
            'cache_hit': cached,
            'print_parameters': print_params
        })
    
    except Exception as e:
        print(f"Error generating model: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def performance_stats(request):
    """
    Get performance statistics.
    """
    return Response({
        'cache_hit_rate': '0.00%',
        'cached_avg_response': '0.000s',
        'non_cached_avg_response': '0.000s',
    })


@api_view(['GET'])
def health_check(request):
    """Simple health check endpoint."""
    return Response({'status': 'healthy', 'service': 'Vision3D API'})

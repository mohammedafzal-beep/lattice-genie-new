import numpy as np
from skimage import measure
from stl import mesh
import os
from concurrent.futures import ThreadPoolExecutor

def Inverse_Ortho_FCC(a, b, c, face_atom_radius=0.4, r=0.47, resolution=200, folder='all_files'):

    def Lattice_atom_positions(a, b, c, alpha, beta, gamma):
        alpha_rad = np.deg2rad(alpha)
        beta_rad = np.deg2rad(beta)
        gamma_rad = np.deg2rad(gamma)

        T = np.array([
            [1, 0, 0],
            [np.cos(gamma_rad), np.sin(gamma_rad), 0],
            [np.cos(beta_rad), (np.cos(alpha_rad) - np.cos(beta_rad) * np.cos(gamma_rad)) / np.sin(gamma_rad),
             np.sqrt(1 - np.cos(beta_rad) ** 2 - ((np.cos(alpha_rad) - np.cos(beta_rad) * np.cos(gamma_rad)) / np.sin(gamma_rad)) ** 2)]
        ])
        positions = [
            [0, 0, 0], [a, 0, 0], [0, b, 0], [0, 0, c],
            [a, b, 0], [a, 0, c], [0, b, c], [a, b, c],
            [0.5 * a, 0.5 * b, 0],
            [0.5 * a, 0, 0.5 * c],
            [0, 0.5 * b, 0.5 * c],
            [0.5 * a, 0.5 * b, 1 * c],
            [0.5 * a, 1 * b, 0.5 * c],
            [1 * a, 0.5 * b, 0.5 * c],
        ]
        return [np.dot(pos, T) for pos in positions], T

    #def bravais_function(pos, radius):
        #return (x - pos[0])**2 + (y - pos[1])**2 + (z - pos[2])**2 - radius**2

    def plane_from_points(p1, p2, p3):
        v1 = p3 - p2
        v2 = p1 - p2
        normal_vector = np.cross(v2, v1)
        D = -np.dot(normal_vector, p2)
        return normal_vector, D

    def generate_solid_volume():
        u = np.linspace(0, 1, resolution)
        v = np.linspace(0, 1, resolution)
        w = np.linspace(0, 1, resolution)
        uu, vv, ww = np.meshgrid(u, v, w, indexing='ij')

        grid = uu[..., None] * v1 + vv[..., None] * v2 + ww[..., None] * v3
        global x, y, z
        x, y, z = grid[..., 0], grid[..., 1], grid[..., 2]

        # Start as solid, then subtract spheres
        mask = np.ones_like(x, dtype=bool)
        for pos in atom_positions:
            dx, dy, dz = x - pos[0], y - pos[1], z - pos[2]
            inside_sphere = (dx**2 + dy**2 + dz**2) <= r**2
            mask &= ~inside_sphere  # subtract sphere

        # Convert binary mask to float field for marching cubes
        values = np.where(mask, 1.0, 0.0)

        # Clip faces
        values[0, :, :] = 0
        values[-1, :, :] = 0
        values[:, 0, :] = 0
        values[:, -1, :] = 0
        values[:, :, 0] = 0
        values[:, :, -1] = 0

        verts_idx, faces, _, _ = measure.marching_cubes(values, level=0.5)
        transform_matrix = np.stack([v1, v2, v3], axis=1)
        verts = verts_idx @ (transform_matrix / (resolution - 1))
        return verts, faces


    def create_stl_from_mesh(verts, faces, folder, filename):
        os.makedirs(folder, exist_ok=True)
        full_path = os.path.join(folder, filename)
        tpms_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))

        for i, f in enumerate(faces):
            tri = verts[f]
            normal = np.cross(tri[1] - tri[0], tri[2] - tri[0])
            if np.linalg.norm(normal) == 0:
                normal = np.array([0.0, 0.0, 1.0])
            else:
                normal = normal / np.linalg.norm(normal)
            tpms_mesh.vectors[i] = tri
            tpms_mesh.normals[i] = normal

        tpms_mesh.save(full_path)
        print(f"STL file saved: {full_path}")



    alpha, beta, gamma = 90.0, 90.0, 90.0
    atom_positions, T = Lattice_atom_positions(a, b, c, alpha, beta, gamma)
    positions = np.array(atom_positions)
    v1, v2, v3 = positions[1], positions[2], positions[3]

    faces = {
        'bottom': (positions[0], positions[1], positions[4]),
        'top': (positions[7], positions[5], positions[3]),
        'front': (positions[1], positions[5], positions[7]),
        'back': (positions[6], positions[3], positions[0]),
        'right': (positions[1], positions[0], positions[3]),
        'left': (positions[7], positions[6], positions[2]),
    }
    plane_equation = {name: plane_from_points(*verts) for name, verts in faces.items()}

    filename = f"20Inverse_ortho_FCC_{a:.1f}_{b:.1f}_{c:.1f}_{r:.2f}_{face_atom_radius:.2f}_{resolution}.stl"
    cached_file = os.path.join(folder, filename) 

    verts, faces = generate_solid_volume()
    create_stl_from_mesh(verts, faces, folder, filename) 
    return f'{folder}\\{filename}'

import numpy as np
import pyvista as pv


def visualize_overhang(mesh: pv.PolyData, threshold_angle: float = 45.0):
    """
    In this function, I calculate the angle between the normal and reference direction to get the overhanging angle.
    The input is the mesh and threshold overhanging angle.
    The output is ratio of number of overhanging to all the mesh.
    """

    # calculate the normal of mesh by PyVista
    # The normal direction must be determined in the mesh. In my lattice, the normal calculated by Pyvista toward inwards.
    mesh.compute_normals(
        cell_normals=True,
        point_normals=False,
        consistent_normals=True,
        auto_orient_normals=True
    )
    k = np.array([0, 0, -1])  # This is the direction of reference. For the overhanging angle, we need to calculate the angle between the normal and this direction.


    # we need to exclude the bottom of lattice. Because these will be considered as overhanging.
    # ----------------- exclude the bottom of mesh -----------------
    face_centers = mesh.cell_centers().points

    # get the minimum value (z position value) of all point as the bottom surface.
    z_min = face_centers[:, 2].min()

    """
    Only the mesh points that are above the threshold will be considered for the overhanging calculation
    # I think the threshold (0.5 in my lattice) need to be modified based on your lattice. Maybe it can be decreased to a small number. 
    # You can use the following visualizing function to get feedback and change this threshold to an appropriate value.
    """

    valid_mask = face_centers[:, 2] > z_min+0.5  # 非底层面
    normals = mesh.face_normals

    # Calculate the angle between the normal and this direction.
    norms = np.linalg.norm(normals, axis=1)
    dot_product = normals @ k
    cos_theta = np.clip(dot_product / norms, -1.0, 1.0)
    face_angles = np.degrees(np.arccos(cos_theta))

    # My normal calculated by Pyvista toward inwards. So the overhanging angle are set to be more than 90 plus overhanging set (45)
    """
    After test, your direction is opposite to mine, so I changed the degree to accord to your version
    """
    overhang_faces = (face_angles < threshold_angle) & valid_mask

    # count the ratio of overhanging
    ratio = np.sum(overhang_faces) / len(face_angles)
    # print(ratio)

    # This is a visualizing function to validate the calculation overhanging. It will draw the picture of lattice structure. The red part of picture are overhanging parts.
    face_colors = np.zeros((mesh.n_cells, 3), dtype=np.uint8)
    face_colors[overhang_faces] = [255, 0, 0]  # 红色悬垂
    face_colors[~overhang_faces] = [0, 255, 0]  # 绿色安全

    # 赋值给 cell_data
    mesh.cell_data["face_colors"] = face_colors



    #visualing
    plotter = pv.Plotter()
    plotter.add_mesh(mesh, scalars="face_colors", rgb=True, show_edges=True)
    plotter.add_legend([("Safe", "green"), ("Overhang > Threshold", "red")])

    """
    I find the direction of lattices from STL do not have the normal and even the same xyz direction and origin. 
    The z direction will determine the overhanging situation because the overhanging calculation is based on -z direction.
    I think the direction should be normalized when generating the lattice structure. Change the direction will be complex in the overhanging part.
    
    The direction of xyz axis is visualized accompanying with overhanging situation.
    The following part draws the origin and arrow which can display the lattice's direction (x,y,z) in STL file
    """

    origin = np.array([0, 0, 0])
    mesh_size = max(mesh.bounds[1] - mesh.bounds[0],
                    mesh.bounds[3] - mesh.bounds[2],
                    mesh.bounds[5] - mesh.bounds[4])
    arrow_length = mesh_size * 0.25  # 箭头总长度
    tip_ratio = 0.1  # 箭头头部占总长度比例

    directions = {"X": ([1, 0, 0], "red"),
                  "Y": ([0, 1, 0], "green"),
                  "Z": ([0, 0, 1], "blue")}

    for label, (dir_vec, color) in directions.items():
        vec = np.array(dir_vec) * arrow_length
        # 先画杆
        line = pv.Line(origin, origin + vec * (1 - tip_ratio))
        plotter.add_mesh(line, color=color, line_width=5)
        # 再画箭头头部
        arrow = pv.Arrow(start=origin + vec * (1 - tip_ratio), direction=vec * tip_ratio,
                         tip_length=tip_ratio * arrow_length,
                         tip_radius=0.05 * arrow_length,
                         shaft_radius=0.02 * arrow_length)
        plotter.add_mesh(arrow, color=color)
        # 标签
        plotter.add_point_labels([origin + vec], [label], font_size=20, point_color=color)

    plotter.show()

    return ratio, mesh

def surface_area_to_volume_ratio(file_path):
    """
    Read input STL file
    Calculate overhanging and surface ratio.
    Output surface ratio value
    """

    # calculate overhanging
    mesh = pv.read(file_path)
    ratio, labeled_mesh = visualize_overhang(mesh, threshold_angle=45.0)

    if mesh.volume == 0:
        return np.inf  # avoid 0

    ratio = mesh.area / mesh.volume

    return ratio

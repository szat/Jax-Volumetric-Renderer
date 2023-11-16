import open3d as o3d
import numpy as np

def visualize_3d_points(points):
    """
    Visualizes a set of 3D points.

    Args:
    points (np.ndarray): NumPy array of shape (n, 3) representing 3D points.
    """
    # Ensure the input is a NumPy array
    if not isinstance(points, np.ndarray):
        raise ValueError("The input points must be a NumPy array.")

    # Ensure the shape of the array is correct
    if points.shape[1] != 3:
        raise ValueError("The input array must have a shape of (n, 3).")

    # Create a point cloud object
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    # Visualize the point cloud
    o3d.visualization.draw_geometries([pcd])

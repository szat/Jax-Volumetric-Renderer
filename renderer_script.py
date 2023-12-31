import copy
import os
import sys
sys.path.append('.')
import cv2
import numpy as np
from jax_helpers import *
import open3d as o3d
from jax_mipmap import *
from o3d_helpers import *

model_name = "lego"
path_to_weigths = f"/home/adrian/Documents/Nerf/256_to_512_fasttv/{model_name}/ckpt.npz"
img_size = 800
batch_size = 1024*4
nb_samples = 512
nb_sh_channels = 3
size_model = 128
device = "cuda"

# Try to render now only with one channel???
data = np.load(path_to_weigths, allow_pickle=True)
# Access data arrays using keys
npy_radius = data['radius']
npy_center = np.float16(data['center'])
npy_links = data['links']
npy_density_data = np.float16(data['density_data'])
npy_sh_data = np.float16(data['sh_data'])
npy_basis_type = data['basis_type']

mask_sphere = filter_over_sphere(npy_links, np.ones(3)*(512/2), 512/2-10)
npy_links[~mask_sphere] = 0

# kill one voxel for simplicity and indexing
npy_density_data[0] = -999
npy_sh_data[0] = -999
npy_links[npy_links < 0] = 0

# Here we take only one channel npy_sh_data[:,:,:,:9]
npy_density_data = npy_density_data[npy_links[::4, ::4, ::4]]
npy_sh_data = npy_sh_data[npy_links[::4, ::4, ::4]]
npy_sh_data_c1 = npy_sh_data[:,:,:,:9]
npy_sh_data_c2 = npy_sh_data[:,:,:,9:18]
npy_sh_data_c3 = npy_sh_data[:,:,:,18:]

origin = np.array([size_model + 20., size_model + 20., size_model + 20.])
orientation = np.array([-1., -1., -1.])
orientation = orientation / np.linalg.norm(orientation)
camera = Camera(origin=origin, orientation=orientation, dist_plane=2, length_x=1, length_y=1,
                pixels_x=img_size, pixels_y=img_size)
rays_cam = get_camera_rays(camera)
rays_origins = np.tile(origin, (img_size*img_size, 1)).astype(np.float32)
rays_dirs = rays_cam.reshape((img_size*img_size, 3)).astype(np.float32)
box_min = np.zeros(rays_origins.shape)
box_max = np.ones(rays_origins.shape)*(size_model - 2)
ray_inv_dirs = 1. / rays_dirs
tmin, tmax = intersect_ray_aabb(rays_origins, ray_inv_dirs, box_min, box_max)
sh_mine = eval_sh_bases_mine(rays_dirs)

mask = np.ones([800, 800])
mask = mask == 1
mask = mask.flatten()

mask = tmin < tmax
valid_rays_origins = rays_origins[mask]
valid_rays_dirs = rays_dirs[mask]
valid_tmin = tmin[mask]
valid_tmin = valid_tmin[:, None]
valid_tmax = tmax[mask]
valid_tmax = valid_tmax[:, None]
valid_sh = sh_mine[mask]

x = np.concatenate((valid_rays_origins, valid_rays_dirs, valid_tmin, valid_tmax, valid_sh), axis=1)
x = np.float16(x)

colors = np.zeros([800*800, 3])
max_dt = np.max(tmax - tmin)
nb = 100
step_size = 0.5
delta_scale = 1/128

tics = np.float16(np.arange(0.05, 0.95, step=1/nb_samples))
tics = jnp.array(tics)

nb_samples = 2 * npy_density_data.shape[0]
tics = jnp.float16(jnp.arange(0.05, 0.95, step=1 / nb_samples))

# could be done once on a inbetween grid
def mean3d_to_vmap_no_links(vecs, data):
    xyz = vecs
    xyz_floor = jnp.floor(xyz)
    x0, y0, z0 = xyz_floor.astype(int)

    v000 = data[x0, y0, z0]
    v100 = data[x0+1, y0, z0]
    v010 = data[x0, y0+1, z0]
    v001 = data[x0, y0, z0+1]
    v110 = data[x0+1, y0+1, z0]
    v011 = data[x0, y0+1, z0+1]
    v101 = data[x0+1, y0, z0+1]
    v111 = data[x0+1, y0+1, z0+1]

    tmp = jnp.array([v000, v100, v010, v001, v110, v011, v101, v111])
    return jnp.mean(tmp)

mean3d_no_links = jit(vmap(mean3d_to_vmap_no_links, in_axes=(0, None)))

def silhouette(x, npy_density_data):
    ori = x[:3]
    dir = x[3:6]
    tmin = x[6:7]
    tmax = x[7:8]
    samples = (tmax - tmin) * tics + tmin
    tmp = jnp.matmul(samples[:, None], dir[None, :])
    tmp = jnp.add(tmp, ori[None, :])
    sample_points_in = tmp

    out = mean3d_no_links(sample_points_in, npy_density_data)
    sample_point_idx = jnp.argmax(out > -999)
    out = sample_points_in[sample_point_idx]
    return out

silhouete = jit(vmap(silhouette, in_axes=(0, None)))

front = silhouete(x, npy_density_data)
front = np.array(front)

visualize_3d_points(front)

mask_box = is_inside_box(front, 10*np.ones(3), (size_model-10)*np.ones(3))
front = front[mask_box]

visualize_3d_points(front)

x = x[mask_box]

line_end = front + x[:, 3:6] * 5
line_start = front + x[:, 3:6] * (-1)

line_end = line_end[::43]
line_start = line_start[::43]

# Define multiple points for the lines
line_points =  np.vstack([line_start, line_end])
lines = []
for i in range(len(line_end)):
    lines.append([i, i+len(line_end)])

# # Create a LineSet object
line_set = o3d.geometry.LineSet()
line_set.points = o3d.utility.Vector3dVector(line_points)
line_set.lines = o3d.utility.Vector2iVector(lines)
line_set.paint_uniform_color([0, 1, 0])  # Red color for the line

pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(front)

o3d.visualization.draw_geometries([pcd, line_set])

tics = jnp.float16(jnp.arange(0, 1, step=1 / 50))
xx = x
xx[:, :3] = front
def render_slim_c1(xxx, npy_data_in):
    f = xxx[:3]
    ray_start = f + xxx[3:6] * 0
    dir = xxx[3:6]
    my_sh_in = xxx[8:]

    samples = tics * 50
    tmp = jnp.matmul(samples[:, None], dir[None, :])
    tmp = jnp.add(tmp, ray_start[None, :])

    sample_points_in = tmp
    interp = jit_trilinear_interp_no_links(sample_points_in, npy_data_in)
    interp = np.squeeze(interp)
    interp_sh_coeffs = interp[:, 1:][None, :, :]
    interp_opacities = interp[:, :1][None, :, :]
    interp_opacities = jnp.clip(interp_opacities, a_min=0.0, a_max=100000)
    deltas = (samples[1:] - samples[:-1])

    interp_sh_coeffs = interp_sh_coeffs.reshape(1, tics.shape[0], 1, 9)
    interp_opacities = interp_opacities.reshape(1, tics.shape[0], 1)
    interp_harmonics = interp_sh_coeffs * my_sh_in[None, None, None, :]

    interp_opacities = jnp.squeeze(interp_opacities)

    deltas_times_sigmas = - deltas * interp_opacities[:-1]

    cum_weighted_deltas = jnp.cumsum(deltas_times_sigmas)
    cum_weighted_deltas = jnp.concatenate([jnp.zeros(1, dtype='float16'), cum_weighted_deltas[:-1]])

    samples_colors = jnp.clip(jnp.sum(interp_harmonics, axis=3) + 0.5, a_min=0.0, a_max=100000)
    samples_colors = samples_colors[0]  # here this needs changing
    deltas_times_sigmas = jnp.squeeze(deltas_times_sigmas)
    tmp1 = jnp.exp(cum_weighted_deltas)
    tmp2 = 1 - jnp.exp(deltas_times_sigmas)
    rays_color = jnp.sum(tmp1[:, None] * tmp2[:, None] * samples_colors[:-1], axis=0)
    out = rays_color
    return out

render_slim_jit_c1 = jit(vmap(render_slim_c1, in_axes=(0, None)))

def render_wrapper(x, npy_density_data, npy_sh_data):
    npy_data = np.concatenate((npy_density_data, npy_sh_data), axis=3)

    batch_size = 50000
    batch_nb = jnp.ceil(len(x) / batch_size)

    tmp_rgb_slim = []
    for i in range(int(batch_nb - 1)):
        res = render_slim_jit_c1(x[i * batch_size: (i + 1) * batch_size], npy_data)
        res.block_until_ready()
        tmp_rgb_slim.append(res)

    res = render_slim_jit_c1(x[int((batch_nb - 1) * batch_size):], npy_data)
    tmp_rgb_slim.append(res)
    colors_c1_slim = np.concatenate(tmp_rgb_slim)

    complete_colors_slim = np.zeros((rays_origins.shape[0], 1))

    tmp_mask = np.zeros_like(mask)
    tmp_mask[mask] = 1
    tmp_mask[tmp_mask == 1] = mask_box
    complete_colors_slim[tmp_mask] = colors_c1_slim
    complete_colors_slim[complete_colors_slim > 1] = 1
    complete_colors_slim[complete_colors_slim < 0] = 0

    img_slim = complete_colors_slim.reshape([800,800,1])
    return img_slim

img_c1 = render_wrapper(xx, npy_density_data, npy_sh_data_c1)
img_c2 = render_wrapper(xx, npy_density_data, npy_sh_data_c2)
img_c3 = render_wrapper(xx, npy_density_data, npy_sh_data_c3)

import cv2
img = np.concatenate([img_c1, img_c2, img_c3], axis=2)
img = (img * 255).astype(np.uint8)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


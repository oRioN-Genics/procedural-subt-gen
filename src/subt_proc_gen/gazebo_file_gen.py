# This file defines functions to create a gazebo world file from a set of meshes
import subt_proc_gen.mesh_generation as mg
import subt_proc_gen.param_classes as mgp
import subt_proc_gen.tunnel as tn
from subt_proc_gen.gazebo_base_sdf_text import *
import open3d as o3d
import os
import shutil


def format_model_sdf_text(name, x, y, z, r, p, yw, uri, material_text):
    return MODEL_BASE_SDF.format(name, x, y, z, r, p, yw, uri, uri, material_text)

def format_model_config_text(name):
    return MODEL_CONFIGURATION.format(name)

def write_model_config(path_to_model_folder, name):
    cfg = format_model_config_text(name)
    
    with open(os.path.join(path_to_model_folder, "model.config"), "w") as f:
        f.write(cfg)

def mesh_generator_to_gazebo_model(
    mesh_generator: mg.TunnelNetworkMeshGenerator, path_to_model_folder, name
):
    mesh = mesh_generator.mesh
    os.makedirs(path_to_model_folder, exist_ok=True)
    meshes_dir = os.path.join(path_to_model_folder, "meshes")
    os.makedirs(meshes_dir, exist_ok=True)
    path_to_mesh = os.path.join(meshes_dir, "mesh.obj")

    # Mesh cleaning and manifold checks
    print("Before cleaning:")
    print("  Edge manifold:", mesh.is_edge_manifold())
    print("  Vertex manifold:", mesh.is_vertex_manifold())
    print("  Self intersecting:", mesh.is_self_intersecting())
    print("  Watertight:", mesh.is_watertight())

    mesh.remove_duplicated_vertices()
    mesh.remove_duplicated_triangles()
    mesh.remove_degenerate_triangles()
    mesh.remove_non_manifold_edges()

    print("After cleaning:")
    print("  Edge manifold:", mesh.is_edge_manifold())
    print("  Vertex manifold:", mesh.is_vertex_manifold())
    print("  Self intersecting:", mesh.is_self_intersecting())
    print("  Watertight:", mesh.is_watertight())

    tensor_mesh = o3d.t.geometry.TriangleMesh.from_legacy(mesh)
    tensor_mesh.compute_uvatlas()
    o3d.t.io.write_triangle_mesh(path_to_mesh, tensor_mesh)
    sdf_text = format_model_sdf_text(
        name, 0, 0, 0, 0, 0, 0, path_to_mesh, MATERIAL_TEXT
    )
    path_to_sdf = os.path.join(path_to_model_folder, "model.sdf")
    with open(path_to_sdf, "w") as f:
        f.write(sdf_text)
    write_model_config(path_to_model_folder, name)
    return path_to_sdf


def mesh_generator_to_gazebo_world(
    mesh_generator: mg.TunnelNetworkMeshGenerator, path_to_folder, number_of_rocks=0
):
    os.makedirs(path_to_folder, exist_ok=True)
    path_to_cave_model_folder = os.path.join(path_to_folder, "cave_model")
    path_to_cave_model_sdf = mesh_generator_to_gazebo_model(
        mesh_generator,
    )

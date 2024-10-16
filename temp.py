import math
import numpy as np

cu1_ort = [-0.248, -10.288, -2.811]
p1_ort = [1.185, 12.254, 3.311]
cu2_ort = [8.663285, 3.501868, 10.253111]
p2_ort = [8.263336, 5.698820, 9.894364]

cell_params = [20.13800, 13.59500, 26.54900, 90.00000, 95.31600, 90.00000]

def dist(v1, v2):
    return np.sqrt((v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)

def unit_cell_vectors(cell_parameters):
    # Convert angles to radians
    alpha, beta, gamma = np.radians(cell_parameters[3:])
    # Calculate cell volume
    a, b, c = cell_parameters[:3]
    volume = a * b * c * np.sqrt(1 - np.cos(alpha)**2 - np.cos(beta)**2 - np.cos(gamma)**2 + 2*np.cos(alpha)*np.cos(beta)*np.cos(gamma))
    # Calculate vectors
    a_vector = np.array([a, 0, 0])
    b_vector = np.array([b * np.cos(gamma), b * np.sin(gamma), 0])
    c_vector = np.array([c * np.cos(beta),
                         (c * (np.cos(alpha) - np.cos(beta) * np.cos(gamma))) / np.sin(gamma),
                         volume / (a * b * np.sin(gamma))])
    return a_vector, b_vector, c_vector

def ort2frac(xyz_coords, A):
    return (list(np.matmul(xyz_coords, np.linalg.inv(A))))

def frac2ort(frac_coords, A):
    return (list(np.matmul(frac_coords, A)))

cell_vec_a, cell_vec_b, cell_vec_c = unit_cell_vectors(cell_params)
A = np.array([cell_vec_a, cell_vec_b, cell_vec_c])


vec1 = np.add(p1_ort, cu1_ort)
nomr_vec1 = vec1 / dist(cu1_ort, p1_ort)
new_cu1 = np.add(cu1_ort, nomr_vec1*0.3)

vec2 = np.subtract(p2_ort, cu2_ort)
nomr_vec2 = vec2 / dist(cu2_ort, p2_ort)
new_cu2 = np.add(cu2_ort, nomr_vec2*0.3)


print (f'{ort2frac(new_cu1, A)[0]:.6f} {ort2frac(new_cu1, A)[1]:.6f} {ort2frac(new_cu1, A)[2]:.6f}')
print (f'{ort2frac(new_cu2, A)[0]:.6f} {ort2frac(new_cu2, A)[1]:.6f} {ort2frac(new_cu2, A)[2]:.6f}')

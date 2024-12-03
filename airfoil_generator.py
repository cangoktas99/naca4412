import numpy as np
import math

# Formula for 4-digit NACA Airfoil (NACA XYTT) [For 1 unit chord]
# m = X/100 [maximum camber]; p = Y/10 [location of maximum camber]; thickness = TT/100 [maximum thickness]
# y_c = m/p^2 (2px-x^2) for 0 <= x <= p
# y_c = m/(1-p^2) ((1-2p) + 2px - x^2) for p <= x <= 1
# x_upper = x - y_t sin\theta, x_lower = x + y_t sin\theta
# y_upper = y_c + y_t cos\theta, y_lower = y_c - y_t cos\theta
# y_t = 5*thickness (0.2969\sqrt(x) - 0.1260x - 0.3516x^2 + 0.2843x^3 - 0.1015x^4)
# and \theta = atan(dy_c/dx), where
# dy_c/dx = 2m/p^2 (p-x) for 0 <= x <= p
# dy_c/dx = 2m/(1-p^2) (p-x) for p <= x <= 1


def define_camber_parameters(a, b):
    m = a/100
    p = b/10
    return m, p


def define_thickness_parameter(thickness):
    max_thickness = thickness / 100
    return max_thickness


def thickness_function(x, thickness):
    return 5*thickness * (0.2969*np.sqrt(x) - 0.1260*x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)


def camber_function(x, mm, pp):
    if x <= pp:
        return mm/pp**2 * (2*pp*x - x**2)
    else:
        return mm/(1-pp)**2 * (1 - 2*pp + 2*pp*x - x**2)


def derivative_of_camber_function(x, mm, pp):
    if x <= pp:
        return 2*mm/pp**2 * (pp - x)
    else:
        return 2*mm/(1-pp)**2 * (pp - x)


def set_x_coordinates(n, cosine_spacing=True):
    if n % 2 == 1:
        n = n - 1
    one_side_points = int(n/2) + 1
    if cosine_spacing:
        beta = list(np.linspace(0, math.pi, one_side_points, True))
        x_c = []
        for b in beta:
            x_c.append((1 - math.cos(b)) / 2)
    else:
        x_c = list(np.linspace(0, 1, one_side_points, True))
    return x_c[1:]


def multiply_list_with_constant(a: list, b: float):
    a_ = []
    for e in a:
        a_.append(e*b)
    return a_


def calculate_airfoil(a, b, tt, n, scale=1):
    # NACA abtt for n points (total) in space
    if scale is None:
        scale = [False, 1]
    m, p = define_camber_parameters(a, b)
    t = define_thickness_parameter(tt)
    x_c = set_x_coordinates(n)
    x_upper, x_lower, y_upper, y_lower = [], [], [], []
    vec_y_c = []
    for x in x_c:
        y_c = camber_function(x, m, p)
        vec_y_c.append(y_c)
        dyc_dx = derivative_of_camber_function(x, m, p)
        theta  = math.atan(dyc_dx)
        y_t    = thickness_function(x, t)
        x_upper.append(x - y_t * math.sin(theta))
        x_lower.append(x + y_t * math.sin(theta))
        y_upper.append(y_c + y_t * math.cos(theta))
        y_lower.append(y_c - y_t * math.cos(theta))
    vec_x = []
    vec_y = []
    for i in range(len(x_upper)-1, -1, -1):
        vec_x.append(x_upper[i])
        vec_y.append(y_upper[i])
    vec_x.append(0.)
    vec_y.append(0.)
    for i in range(len(x_lower)):
        vec_x.append(x_lower[i])
        vec_y.append(y_lower[i])
    if not scale == 1:
        vec_x = multiply_list_with_constant(vec_x, scale)
        vec_y = multiply_list_with_constant(vec_y, scale)
    return vec_x, vec_y
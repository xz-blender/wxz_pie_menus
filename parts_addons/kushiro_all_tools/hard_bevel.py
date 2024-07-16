# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Created by Kushiro

import math
from operator import indexOf

import bpy
import bmesh
import bmesh.utils

from mathutils import Matrix, Vector, Quaternion, Euler

import mathutils


import math
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    FloatVectorProperty,
    StringProperty
)

from pprint import pprint

import itertools
import numpy as np
from mathutils.geometry import intersect_line_line




class Vert:
    def __init__(self) -> None:
        self.co = None


class Loop:
    def __init__(self) -> None:
        self.vert = Vert()
        self.link_loop_next = None
        self.link_loop_prev = None
        self.deg = None
        self.next = None
        self.realvert = None


mat = None

def link_loops(ps):
    for i , p1 in enumerate(ps):
        p2 = ps[(i + 1) % len(ps)]
        p1.link_loop_next = p2
        p2.link_loop_prev = p1



def create_ps(f1, mat):
    ps = []
    for p1 in f1.loops:
        p2 = Loop()
        p2.index = p1.vert.index
        p2.vert.co = mat @ p1.vert.co
        p2.realvert = p1.vert
        ps.append(p2)
    link_loops(ps)        
    return ps
    

def intersect2d(p1, p2, p3, p4):
    res = mathutils.geometry.intersect_line_line_2d(p1.xy, p2.xy, p3.xy, p4.xy)
    if res != None:
        return Vector((res[0], res[1], 0))
    return None


def get_matrix_face(f1):
    p1 = f1.loops[0]
    m1 = Vector()
    for p2 in f1.loops:
        p3 = p2.link_loop_next
        m1 = p3.vert.co - p2.vert.co
        if m1.length > 0:
            break
    if m1.length == 0:
        return None
    m2 = f1.normal.cross(m1)
    mat = get_matrix(m1, m2, f1.normal, p1.vert.co)
    return mat.inverted()



def get_matrix(m1, m2, m3, cen):
    if m1.length == 0 or m2.length == 0 or m3.length == 0:
        return Matrix.Identity(4)            
    m = Matrix.Identity(4)        
    m[0][0:3] = m1.normalized()
    m[1][0:3] = m2.normalized()
    m[2][0:3] = m3.normalized()
    m[3][0:3] = cen.copy()
    m = m.transposed()
    return m    



def get_mid(m1, m2, sn):
   c1 = m1.cross(sn) * -1
   c2 = m2.cross(sn)
   c3 = c1.normalized() + c2.normalized()
   return c3.normalized() 


def get_ps_mid(p1, sn):
    p2 = p1.link_loop_next
    p3 = p1.link_loop_prev
    m1 = p2.vert.co - p1.vert.co
    m2 = p3.vert.co - p1.vert.co
    return get_mid(m1, m2, sn)

def angle(p1):
    p2 = p1.link_loop_next
    p3 = p1.link_loop_prev
    m1 = p2.vert.co - p1.vert.co
    m2 = p3.vert.co - p1.vert.co
    if m1.length == 0 or m2.length == 0:
        return 0
    return m1.angle(m2)



def is_concave(p1, sn):
    p2 = p1.link_loop_next
    p3 = p1.link_loop_prev
    m1 = p2.vert.co - p1.vert.co
    m2 = p3.vert.co - p1.vert.co
    c1 = m1.cross(m2)
    if c1.dot(sn) < 0:
        return True
    return False

def make_mid_loop(ps, sn, mlen):
    ps2 = []
    for p1 in ps:
        # if is_concave(p1, sn):
        #     p2 = Loop()
        #     p2.vert.co = p1.vert.co.copy()
        # else:
        mid = get_ps_mid(p1, sn)
        p2 = Loop()
        d1 = angle(p1)
        p1.deg = math.sin(d1 / 2)
        if p1.deg == 0:
            p2.vert.co = p1.vert.co.copy()
        else:
            d2 = mlen / p1.deg
            p2.vert.co = p1.vert.co + mid * d2
        p1.next = p2
        
        ps2.append(p2)
    link_loops(ps2)
    return ps2



def filter_same(ps):
    psk = list(ps)
    while True:
        ps2 = []
        changed = False
        for i in range(len(psk)):
            i2 = (i + 1) % len(psk)
            v1 = psk[i]
            v2 = psk[i2]
            if v1 == v2:
                changed = True
                continue
            ps2.append(v1)
        psk = ps2
        if not changed:
            break
    return psk


def get_links(v1, v2):
    if v1 == v2:
        return []
    vk = v1
    vs = []
    while True:
        vk = vk.link_loop_next        
        if vk == None:
            return []
        if vk == v2:
            return vs
        if vk == v1:
            return None
        vs.append(vk)


def edge_dist(A, B, P):
    C = B - A
    if C.length == 0:
        return (P - A).length
    diff = P - A
    t = diff.dot(C) / C.dot(C)
    t = min(max(t, 0), 1)
    K = A + C * t
    d1 = (K - P).length    
    return d1



def min_value(d1, d2):
    if d1 == None and d2 == None:
        return None
    if d1 == None:
        return d2
    elif d2 == None:
        return d1
    return min(d1, d2)



def distance_point_to_segment(p, a, b):
    v = b - a
    w = p - a
    t = w.dot(v) / v.dot(v)
    if t < 0.0:
        return (p - a).length
    elif t > 1.0:
        return (p - b).length
    else:
        projection = a + t * v
        return (p - projection).length
    





def get_ps_center(ps):
    cen = Vector((0, 0, 0))
    for p1 in ps:
        cen += p1.vert.co
    cen /= len(ps)
    return cen




def get_intersect_edge(i, ps, sn):
    mid = get_ps_mid(ps[i], sn)
    ms = []
    for k in range(len(ps)):
        k2 = (k + 1) % len(ps)
        if k == i or k2 == i:
            continue
        p1 = ps[k].vert.co
        p2 = ps[k2].vert.co
        pin = intersect2d(ps[i].vert.co, ps[i].vert.co + mid * 1000, 
                        p1, p2)
        if pin == None:
            continue
        d1 = (pin - ps[i].vert.co).length    
        ms.append((d1, k))
    if len(ms) == 0:
        return None, None
    d1, k = min(ms, key=lambda x: x[0])
    return d1, k




def check_line_hit(p1, mid1, p2, mid2, deg1, deg2):
    xA = p1.vert.co.x
    yA = p1.vert.co.y
    xB = mid1.x
    yB = mid1.y
    xC = p2.vert.co.x
    yC = p2.vert.co.y
    xD = mid2.x
    yD = mid2.y
    if xB - xD == 0:
        return None
    if yB - yD == 0:
        return None
    t1 = -(deg1*deg2*xA - deg1*deg2*xC)/(deg2*xB - deg1*xD)
    t2 = -(deg1*deg2*yA - deg1*deg2*yC)/(deg2*yB - deg1*yD)
    if t1 != t2:
        return None
    if t1 < 0 or t2 < 0:
        return None
    return t1


def get_max_bound(ps):
    vs = [p1.vert.co for p1 in ps]
    x_max = max([v1.x for v1 in vs])
    x_min = min([v1.x for v1 in vs])
    y_max = max([v1.y for v1 in vs])
    y_min = min([v1.y for v1 in vs])
    width = x_max - x_min
    height = y_max - y_min
    return max(width, height)

def sqrt(x):
    return math.sqrt(abs(x))


def get_ds(p1, p2, pv, mid1, mid2):
    xA = p1.vert.co.x
    yA = p1.vert.co.y
    xB = p2.vert.co.x
    yB = p2.vert.co.y
    x_mid1 = mid1.x
    y_mid1 = mid1.y
    x_mid2 = mid2.x
    y_mid2 = mid2.y
    xK = pv.x
    yK = pv.y
    seg1 = p1.deg
    seg2 = p2.deg
    div = x_mid2*y_mid1 - x_mid1*y_mid2
    if div == 0:
        return None
    t = -1/2*(seg1*x_mid2*yA - seg2*x_mid1*yB + (seg2*x_mid1 - seg1*x_mid2)*yK + (seg2*xB - seg2*xK)*y_mid1 - (seg1*xA - seg1*xK)*y_mid2 - sqrt(seg1**2*x_mid2**2*yA**2 - 2*seg1*seg2*x_mid1*x_mid2*yA*yB + seg2**2*x_mid1**2*yB**2 + (seg2**2*x_mid1**2 - 2*seg1*seg2*x_mid1*x_mid2 + seg1**2*x_mid2**2)*yK**2 + (seg2**2*xB**2 - 2*seg2**2*xB*xK + seg2**2*xK**2)*y_mid1**2 + (seg1**2*xA**2 - 2*seg1**2*xA*xK + seg1**2*xK**2)*y_mid2**2 + 2*((seg1*seg2*x_mid1*x_mid2 - seg1**2*x_mid2**2)*yA - (seg2**2*x_mid1**2 - seg1*seg2*x_mid1*x_mid2)*yB)*yK - 2*((seg1*seg2*xB - seg1*seg2*xK)*x_mid2*yA + ((seg2**2*xB - seg2**2*xK)*x_mid1 - 2*(seg1*seg2*xA - seg1*seg2*xK)*x_mid2)*yB - ((seg2**2*xB - seg2**2*xK)*x_mid1 - (2*seg1*seg2*xA - seg1*seg2*xB - seg1*seg2*xK)*x_mid2)*yK)*y_mid1 - 2*((seg1*seg2*xA - seg1*seg2*xK)*x_mid1*yB - (2*(seg1*seg2*xB - seg1*seg2*xK)*x_mid1 - (seg1**2*xA - seg1**2*xK)*x_mid2)*yA - ((seg1*seg2*xA - 2*seg1*seg2*xB + seg1*seg2*xK)*x_mid1 + (seg1**2*xA - seg1**2*xK)*x_mid2)*yK + (seg1*seg2*xA*xB + seg1*seg2*xK**2 - (seg1*seg2*xA + seg1*seg2*xB)*xK)*y_mid1)*y_mid2))/div
    if t < 0:
        return None
    return t




def get_ms_behind(i, ps, pks, ms, offset, mids, bm, plen):
    i2 = (i + 1) % len(ps)
    i3 = (i - 1) % len(ps)
    p1 = ps[i]
    p2 = ps[i2]
    p3 = ps[i3]
    if p1.deg == 0:
        return   
    mid1 = mids[i]
    mid2 = mids[i2]
    mid3 = mids[i3]

    k1 = p1.vert.co
    k2 = p1.vert.co + mid1 * plen
    k3 = p2.vert.co    
    k4 = p2.vert.co + mid2 * plen
    k5 = p3.vert.co
    k6 = p3.vert.co + mid3 * plen

    # v1 = Vector((-0.5, 0.3, 0))
    # print(v1.normalized())

    for k in range(len(ps)):
        if k == i or k == i2 or k == i3:
            continue
        # if k == i4 or k == i5:
        #     continue
        pk1 = ps[k]  

        if is_inside(pk1.vert.co, [k1, k3, k4, k2]):
            if is_colinear(k1, k2, pk1.vert.co):
                continue
            if is_colinear(k3, k4, pk1.vert.co):
                continue

            if p1.deg > 0 and p2.deg > 0:
                dmid1 = mid1 / p1.deg
                dmid2 = mid2 / p2.deg
                if mid1.dot(mid2) == 1.0:
                    d1 = get_est_same(p1.vert.co, p2.vert.co, dmid1, pk1.vert.co)                
                else:
                    d1 = get_est(p1.vert.co, p2.vert.co, dmid1, dmid2, pk1.vert.co)                
                if d1 != None:                
                    # if d1 < 0.1:
                    #     # edge(bm, k1, pk1.vert.co)
                    # ms.append(d1 * 0.999)
                    d1 = dmid1.length * d1
                    ms.append(d1 * 0.999)

        if is_inside(pk1.vert.co, [k1, k2, k6, k5]):
            if is_colinear(k1, k2, pk1.vert.co):
                continue
            if is_colinear(k5, k6, pk1.vert.co):
                continue

            if p1.deg > 0 and p3.deg > 0:
                dmid1 = mid1 / p1.deg
                dmid3 = mid3 / p3.deg                
                if mid1.dot(mid3) == 1.0:
                    d1 = get_est_same(p3.vert.co, p1.vert.co, dmid3, pk1.vert.co)
                else:
                    d1 = get_est(p3.vert.co, p1.vert.co, dmid3, dmid1, pk1.vert.co)
                if d1 != None:
                    # if d1 < 0.1:
                    #     # edge(bm, k1, pk1.vert.co)                 
                    # ms.append(d1 * 0.999)  
                    d1 = dmid1.length * d1
                    ms.append(d1 * 0.999)


def is_colinear(p1, p2, p3):
    m1 = p2 - p1
    m2 = p3 - p1
    d1 = m1.normalized().dot(m2.normalized())
    if abs(d1) > 0.99:
        return True
    return False


# def get_ms_behind(i, ps, pks, ms, offset, mids, bm):
#     i2 = (i + 1) % len(ps)
#     i3 = (i - 1) % len(ps)
#     p1 = ps[i]
#     p2 = ps[i2]
#     p3 = ps[i3]
#     if p1.deg == 0:
#         return   
#     mid1 = mids[i]
#     mid2 = mids[i2]
#     mid3 = mids[i3]

#     k1 = p1.vert.co
#     k2 = p2.vert.co
#     k3 = p1.vert.co + mid1 * 1000
#     k4 = p2.vert.co + mid2 * 1000
#     k5 = p3.vert.co
#     k6 = p3.vert.co + mid3 * 1000

#     for k in range(len(ps)):
#         if k == i or k == i2 or k == i3:
#             continue
#         # if k == i4 or k == i5:
#         #     continue
#         pk1 = ps[k]  

#         if is_inside(pk1.vert.co, [k1, k2, k4, k3]):     
#             if mid1.dot(mid2) == 1.0:
#                 d1 = get_est_same(p1.vert.co, p2.vert.co, mid1, pk1.vert.co)
#             else:
#                 d1 = get_est(p1.vert.co, p2.vert.co, mid1, mid2, pk1.vert.co)
#             if d1 != None:                
#                 # if d1 < 0.1:
#                 #     # edge(bm, k1, pk1.vert.co)
#                 # ms.append(d1 * 0.999)
#                 ms.append((d1 * 0.999, ))

#         if is_inside(pk1.vert.co, [k1, k3, k6, k5]):
#             if mid1.dot(mid3) == 1.0:
#                 d1 = get_est_same(p3.vert.co, p1.vert.co, mid3, pk1.vert.co)
#             else:
#                 d1 = get_est(p3.vert.co, p1.vert.co, mid3, mid1, pk1.vert.co)
#             if d1 != None:
#                 # if d1 < 0.1:
#                 #     # edge(bm, k1, pk1.vert.co)                 
#                 ms.append(d1 * 0.999)        





def get_est_same(a, b, m1, k):
    m1_x, m1_y = m1[:2]
    x_a, y_a = a[:2]
    x_b, y_b = b[:2]
    x_k, y_k = k[:2]   
    div = m1_y*x_a - m1_y*x_b - m1_x*y_a + m1_x*y_b
    t = ((x_b - x_k)*y_a - (x_a - x_k)*y_b + (x_a - x_b)*y_k)/div
    if t < 0:
        return None
    return t

# def get_est(a, b, m1, m2, k):
#     m1_x, m1_y = m1[:2]
#     m2_x, m2_y = m2[:2]
#     x_a, y_a = a[:2]
#     x_b, y_b = b[:2]
#     x_k, y_k = k[:2]   
#     div = m1_y*m2_x - m1_x*m2_y
#     if div == 0:
#         return None
#     t = 1/2*(m2_y*x_a - m1_y*x_b + (m1_y - m2_y)*x_k - m2_x*y_a + m1_x*y_b - (m1_x - m2_x)*y_k + sqrt(m2_y**2*x_a**2 - 2*m1_y*m2_y*x_a*x_b + m1_y**2*x_b**2 + m2_x**2*y_a**2 + m1_x**2*y_b**2 + (m1_y**2 - 2*m1_y*m2_y + m2_y**2)*x_k**2 + (m1_x**2 - 2*m1_x*m2_x + m2_x**2)*y_k**2 + 2*((m1_y*m2_y - m2_y**2)*x_a - (m1_y**2 - m1_y*m2_y)*x_b)*x_k - 2*(m2_x*m2_y*x_a + (m1_y*m2_x - 2*m1_x*m2_y)*x_b - (m1_y*m2_x - (2*m1_x - m2_x)*m2_y)*x_k)*y_a - 2*(m1_x*m1_y*x_b + m1_x*m2_x*y_a - (2*m1_y*m2_x - m1_x*m2_y)*x_a - (m1_x*m1_y - 2*m1_y*m2_x + m1_x*m2_y)*x_k)*y_b - 2*((2*m1_y*m2_x - (m1_x + m2_x)*m2_y)*x_a - (m1_x*m1_y + m1_y*m2_x - 2*m1_x*m2_y)*x_b + (m1_x*m1_y - m1_y*m2_x - (m1_x - m2_x)*m2_y)*x_k - (m1_x*m2_x - m2_x**2)*y_a + (m1_x**2 - m1_x*m2_x)*y_b)*y_k))/div
#     if t < 0:
#         return None
#     return t


def get_est(a, b, m1, m2, k):
    m1_x, m1_y = m1[:2]
    m2_x, m2_y = m2[:2]
    x_a, y_a = a[:2]
    x_b, y_b = b[:2]
    x_k, y_k = k[:2]   
    div = m1_y*m2_x - m1_x*m2_y
    if div == 0:
        return None
    t = 1/2*(m2_y*x_a - m1_y*x_b + (m1_y - m2_y)*x_k - m2_x*y_a + m1_x*y_b - (m1_x - m2_x)*y_k + sqrt(m2_y**2*x_a**2 - 2*m1_y*m2_y*x_a*x_b + m1_y**2*x_b**2 + m2_x**2*y_a**2 + m1_x**2*y_b**2 + (m1_y**2 - 2*m1_y*m2_y + m2_y**2)*x_k**2 + (m1_x**2 - 2*m1_x*m2_x + m2_x**2)*y_k**2 + 2*((m1_y*m2_y - m2_y**2)*x_a - (m1_y**2 - m1_y*m2_y)*x_b)*x_k - 2*(m2_x*m2_y*x_a + (m1_y*m2_x - 2*m1_x*m2_y)*x_b - (m1_y*m2_x - (2*m1_x - m2_x)*m2_y)*x_k)*y_a - 2*(m1_x*m1_y*x_b + m1_x*m2_x*y_a - (2*m1_y*m2_x - m1_x*m2_y)*x_a - (m1_x*m1_y - 2*m1_y*m2_x + m1_x*m2_y)*x_k)*y_b - 2*((2*m1_y*m2_x - (m1_x + m2_x)*m2_y)*x_a - (m1_x*m1_y + m1_y*m2_x - 2*m1_x*m2_y)*x_b + (m1_x*m1_y - m1_y*m2_x - (m1_x - m2_x)*m2_y)*x_k - (m1_x*m2_x - m2_x**2)*y_a + (m1_x**2 - m1_x*m2_x)*y_b)*y_k))/div
    if t < 0:
        return None
    return t



def get_ms_origin(i, ps, pks, ms, offset, mids, bm):
    p1 = ps[i]
    mid = mids[i]
    # edge(bm, p1.vert.co, p1.vert.co + mid * 0.5)

    d1 = get_min_height_distance(ps, i, mids, bm)   
    if d1 == None:
        return
    d1, r1, pro1 = d1
    # edge(bm, p1.vert.co, r1.vert.co)
    ms.append(d1)




def get_ms_base(i, ps, pks, ms, offset, mids):
    i2 = (i + 1) % len(ps)
    p1 = ps[i]
    if p1.deg == 0:
        return    
    p2 = ps[i2]
    k1 = pks[i]
    k2 = pks[i2]
    poly = [p1.vert.co, p2.vert.co, k2.vert.co, k1.vert.co]
    # m1 = k2.vert.co - k1.vert.co
    for k in range(len(ps)):
        if k == i or k == i2:
            continue        
        pv = ps[k].vert.co
        if is_inside(pv, poly):
            mid1 = mids[i]
            mid2 = mids[i2]
            d1 = get_ds(p1, p2, pv, mid1, mid2)
            if d1 == None:
                continue
            d1 = d1 / p1.deg
            ms.append(d1 * 0.999)
    i2 = (i - 1) % len(ps)
    p1 = ps[i]
    p2 = ps[i2]
    k1 = pks[i]
    k2 = pks[i2]
    poly = [p2.vert.co, p1.vert.co, k1.vert.co, k2.vert.co]
    # m1 = k2.vert.co - k1.vert.co
    for k in range(len(ps)):
        if k == i or k == i2:
            continue
        pv = ps[k].vert.co
        if is_inside(pv, poly):
            mid1 = mids[i]
            mid2 = mids[i2]
            d1 = get_ds(p2, p1, pv, mid2, mid1)
            if d1 == None:
                continue
            d1 = d1 / p1.deg
            ms.append(  max(d1 - offset, 0) )
        





# def get_ms_base(i, ps, pks, ms, offset, mids):
#     i2 = (i + 1) % len(ps)
#     p1 = ps[i]
#     if p1.deg == 0:
#         return    
#     p2 = ps[i2]
#     k1 = pks[i]
#     k2 = pks[i2]
#     k1.vert.co.z = 0
#     k2.vert.co.z = 0
#     poly = [p1.vert.co, p2.vert.co, k2.vert.co, k1.vert.co]
#     # m1 = k2.vert.co - k1.vert.co
#     for k in range(len(ps)):
#         if k == i or k == i2:
#             continue        
#         pv = ps[k].vert.co
#         if is_inside(pv, poly):
#             mid1 = mids[i]
#             mid2 = mids[i2]
#             d1 = get_ds(p1, p2, pv, mid1, mid2)
#             if d1 == None:
#                 continue
#             d1 = d1 / p1.deg
#             # ms.append(d1 * 0.999)
#             ms.append(  max(d1 - offset, 0) )
#     i2 = (i - 1) % len(ps)
#     p1 = ps[i]
#     p2 = ps[i2]
#     k1 = pks[i]
#     k2 = pks[i2]
#     k1.vert.co.z = 0
#     k2.vert.co.z = 0    
#     poly = [p2.vert.co, p1.vert.co, k1.vert.co, k2.vert.co]
#     # m1 = k2.vert.co - k1.vert.co
#     for k in range(len(ps)):
#         if k == i or k == i2:
#             continue
#         pv = ps[k].vert.co
#         if is_inside(pv, poly):
#             mid1 = mids[i]
#             mid2 = mids[i2]
#             d1 = get_ds(p2, p1, pv, mid2, mid1)
#             if d1 == None:
#                 continue
#             d1 = d1 / p1.deg
#             ms.append(  max(d1 - offset, 0) )
        



def get_ms_sides(i2, i3, ps, p1, mids, mid1, ms):
    sd1 = ps[i2]
    sd2 = ps[i3]
    mid2 = mids[i2]
    mid3 = mids[i3]
    pin = intersect2d(p1.vert.co, p1.vert.co + mid1 * 1000, sd1.vert.co, sd1.vert.co + mid2 * 1000)
    if pin != None:
        d1 = (pin - p1.vert.co).length
        ms.append(d1)
    pin2 = intersect2d(p1.vert.co, p1.vert.co + mid1 * 1000, sd2.vert.co, sd2.vert.co + mid3 * 1000)
    if pin2 != None:
        d1 = (pin2 - p1.vert.co).length
        ms.append(d1)


def get_ms_plane(i, ps, pks, p1, pk, ms, offset):
    for k in range(len(pks)):
        k2 = (k + 1) % len(pks)
        if k == i or k2 == i:
            continue
        p2 = ps[k]
        p3 = ps[k2]
        pk2 = pks[k]
        pk3 = pks[k2] 
        poly = [p2.vert.co, p3.vert.co, pk3.vert.co, pk2.vert.co]
        s1 = get_sn(poly)                     
        pin = line_poly_intersect(p1, pk, poly, s1, offset)            
        if pin != None:                                
            pin.z = 0 
            d1 = (pin - p1.vert.co).length                               
            # ms.append(d1)
            ms.append(d1)




def get_min_height_distance(ps, i, mids, bm):
    i2 = (i + 1) % len(ps)
    p1 = ps[i]
    ppn = ps[i2]
    # m0 = ppn.vert.co - p1.vert.co
    mid1 = mids[i]
    if mid1.length == 0:
        return None
    hs = []
    for k in range(len(ps)):
        if k == i or k == i2:
            continue
        r1 = ps[k]
        m1 = r1.vert.co - p1.vert.co
        pro1 = m1.project(mid1)
        # h1 = m1 - pro1
        hs.append((pro1.length, r1, pro1))
    d1, r1, pro1 = min(hs, key=lambda x: x[0])    
    # edge(bm, p1.vert.co, p1.vert.co + pro1)
    return d1, r1, pro1






def solve_face(bm, ps, pes, plen, offset):
    global mat
    sn = Vector((0,0,1))
    maxlen = get_max_bound(ps)
    mids = []
    es = []
    for i in range(len(ps)):
        p1 = ps[i]
        p1.deg = math.sin(angle(p1)/2)

        i2 = (i + 1) % len(ps)
        i3 = (i - 1) % len(ps)
        ppn = ps[i2]
        ppv = ps[i3]

        e1 = check_bound_mov(ps, i, pes)
        # e2 = check_bound_mov(ps, i2, pes)
        e3 = check_bound_mov(ps, i3, pes)

        es.append((e1, e3))

        if e1 and e3:
            mid = get_ps_mid(p1, sn)
        elif e1 and e3 == False:
            mid = ppv.vert.co - p1.vert.co
            mid = mid.normalized()
        elif e1 == False and e3:
            mid = ppn.vert.co - p1.vert.co
            mid = mid.normalized()
        elif e1 == False and e3 == False:
            mid = Vector()
        # mid = get_ps_mid(p1, sn)
        # edge(bm, p1.vert.co, p1.vert.co + mid * 0.1)
        mids.append(mid)

    pks = []
    for i in range(len(ps)):
        p1 = ps[i]
        mid = mids[i]
        # dmin = plen / p1.deg
        if p1.deg == 0:
            dmin = maxlen
        else:
            dmin = maxlen / p1.deg
        d1 = mid * dmin
        pk = Loop()
        pk.vert.co = p1.vert.co + d1
        pk.vert.co.z = maxlen
        pks.append(pk)

    ps2 = []
    for i in range(len(ps)):        
        i2 = (i + 1) % len(ps)
        i3 = (i - 1) % len(ps)
        p1 = ps[i]
        pc = pks[i]
        ms = []
        mid = mids[i]

        get_ms_behind(i, ps, pks, ms, offset, mids, bm, plen)
        get_ms_plane(i, ps, pks, p1, pc, ms, offset)        

        pt = pad(p1)  
        e1, e3 = es[i]     

        if len(ms) == 0:
            # dlen = 0
            if p1.deg == 0:
                d1 = 0
            else:
                if e1 and e3:
                    d1 = plen / p1.deg   
                else:                
                    deg = angle(p1)
                    d1 = plen / math.sin(deg)
            # pin = p1.vert.co.copy()
        else:
            # dlen = min(ms)
            dlen = min(ms)
            # d1 = dlen * p1.deg
            if p1.deg == 0:
                d2 = 0
            else:
                if e1 and e3:
                    d2 = plen / p1.deg
                    d1 = min(dlen, d2)                    
                else:                    
                    deg = angle(p1)                    
                    d2 = plen / math.sin(deg)
                    # d1 = min(dlen, d2)
            d1 = min(dlen, d2)

        pk = Loop()
        off2 = max(1.0 - offset, 0)
        pk.vert.co = p1.vert.co + mid * d1 * off2
        pk.realvert = p1.realvert
        p1.next = pk
        ps2.append(pk)     
    
    moves = []
    for i in range(len(ps)):         
        p1 = ps[i]
        p2 = ps2[i]
        p1n = ps[(i + 1) % len(ps)]
        ms = []
        for k in range(len(ps)):
            k2 = (k + 1) % len(ps)
            if k == i or k2 == i:
                continue
            p3 = ps2[k]
            p4 = ps2[k2]
            pin = intersect2d(p1.vert.co, p2.vert.co, p4.vert.co, p3.vert.co)
            if pin != None:
                m1 = pin - p1.vert.co                
                ms.append((m1.length, m1))
                continue
        if len(ms) == 0:
            continue
        d1, m1 = min(ms, key=lambda x: x[0])
        moves.append((p2, p1.vert.co + m1 * 0.999))

    for p2, pin in moves:
        p2.vert.co = pin.copy()

    link_loops(ps2)    
    return ps2




def edge2(bm, v1, v2):
    v1 = bm.verts.new( v1)
    v2 = bm.verts.new( v2)
    e1 = bm.edges.new([v1, v2])
    e1.select = True


def edge(bm, v1, v2):
    global mat
    v1 = bm.verts.new( mat @ v1)
    v2 = bm.verts.new( mat @ v2)
    e1 = bm.edges.new([v1, v2])
    e1.select = True
    return e1


def edge_end(bm, v1, v2):
    global mat
    # e1 = bm.edges.new([v1, v2])
    m1 = Vector((0, 0, 0.02))
    m2 = Vector((0, 0.02, 0))
    e1 = edge(bm, v1, v2)
    e1.select = True
    e2 = edge(bm, v1 - m1 * 0.1, v1 + m1 * 0.1)
    e2.select = True
    e3 = edge(bm, v1 - m2 * 0.1, v1 + m2 * 0.1)
    e3.select = True
    e4 = edge(bm, v2 - m1, v2 + m1)
    e4.select = True
    e5 = edge(bm, v2 - m2, v2 + m2)
    e5.select = True


def text(bm, text, loc):
    global mat
    loc = mat @ loc    
    font_curve = bpy.data.curves.new(type="FONT", name="Font Curve")
    font_curve.body = text
    font_curve.size = 0.02
    font_obj = bpy.data.objects.new(name="Font Object", object_data=font_curve)
    bpy.context.scene.collection.objects.link(font_obj) 
    font_obj.location = loc



def pad(p1):
    m1 = get_ps_mid(p1, Vector((0, 0, 1)))
    m1.normalize()
    v2 = p1.vert.co + m1 * 0.03
    return v2



def is_cross_region(p1, p2, poly):
    # for i in range(len(poly)):
    #     i2 = (i + 1) % len(poly)
    #     k1 = poly[i]
    #     k2 = poly[i2]
    #     pin = intersect2d(p1, p2, k1, k2)
    #     if pin != None:
    #         return pin
    if len(poly) < 4:
        return None
    v1 = poly[2]
    v2 = poly[3]
    pin = intersect2d(p1, p2, v1, v2)
    if pin != None:
        return pin    
    if is_inside(p1, poly):
        return p1
    # if is_inside(p2, poly):
    #     return p1
    return None



def get_sn(poly):
    A = poly[0]
    B = poly[1]
    C = poly[2]
    AB = B - A
    AC = C - A
    n = AB.cross(AC)
    n.normalize()
    return n




def point_line_near(pin, pe1, pe2, offset):
    m1 = pe2 - pe1
    m2 = pin - pe1
    pro = m1.dot(m2) / m1.dot(m1)
    # if pro < 0 or pro > 1:
    #     return False
    pro_v = pe1 + m1 * pro
    h1 = pin - pro_v

    if h1.length < offset:
        return True
    return False



def line_poly_intersect(p1, p2, poly, normal, offset):
    cen = sum(poly, Vector()) / len(poly) 
    # cen = (poly[0] + poly[1])/2
    # cen = poly[0]   
    pin = line_plane_intersection(p1.vert.co, p2.vert.co, cen, normal)
    if pin == None:
        return None
    
    poly2 = []
    for p in poly:
        m1 = p - cen
        m2 = m1.normalized()
        p2 = cen + m2 * (m1.length + offset)
        poly2.append(p2)
    poly = poly2
    
    k1 = poly[0]
    k2 = poly[1]
    k3 = poly[2]
    k4 = poly[3]
    n1 = point_line_near(pin, k1, k4, offset)
    n2 = point_line_near(pin, k2, k3, offset)
             
    if n1 or n2 or is_point_inside_polygon(pin, poly, normal, cen): 
        return pin
    return None


def line_plane_intersection(P1, P2, P0, normal):
    num = normal.dot(P0 - P1)
    den = normal.dot(P2 - P1)
    if abs(den) < 1e-6:
        return None
    t = num / den
    intersection = P1 + t * (P2 - P1)
    if t < 0 or t > 1:
        return None
    return intersection


def is_point_inside_polygon(point, polygon, sn, cen):
    mat = get_matrix_vs(polygon, sn, cen)
    ps2 = [mat @ p for p in polygon]
    point2 = mat @ point
    # return is_point_inside_polygon_flat(point2, ps2)
    return is_inside(point2, ps2)



def is_left(p0, p1, p2):
    return (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p2[0] - p0[0]) * (p1[1] - p0[1])


def is_inside(point, polygon):
    wn = 0
    n = len(polygon)    
    for i in range(n):
        if polygon[i][1] <= point[1]:
            if polygon[(i + 1) % n][1] > point[1]:
                if is_left(polygon[i], polygon[(i + 1) % n], point) > 0:
                    wn += 1
        else:
            if polygon[(i + 1) % n][1] <= point[1]:
                if is_left(polygon[i], polygon[(i + 1) % n], point) < 0:
                    wn -= 1
    return wn > 0



def get_matrix_vs(ps, sn, cen):
    m1 = Vector()
    for i in range(len(ps)):
        p2 = ps[i]
        p3 = ps[(i + 1) % len(ps)]
        m1 = p3 - p2
        if m1.length > 0:
            break
    if m1.length == 0:
        return None
    m2 = sn.cross(m1)
    mat = get_matrix(m1, m2, sn, cen)
    return mat.inverted()



    
def get_connected_es(fs2):
    es = set()
    for f1 in fs2:
        for e1 in f1.edges:
            es.add(e1)
    es = list(es)
    es2 = []
    for e1 in es:
        elen = len(e1.link_loops)
        if elen != 2:
            continue   
        es2.append(e1)
    return es2 
    



def filter_fs(fss):
    fs = []
    for v1 in fss:
        if v1 not in fs:
            fs.append(v1)
    return fs


def get_loop_vert(f1, v1):
    for p1 in f1.loops:
        if p1.vert == v1:
            return p1
    return None

        
        

def forward(p1, ct):
    for i in range(ct):
        p1 = p1.link_loop_next
    return p1


def get_final_node(p1):
    pk = p1
    while True:        
        p2 = pk.next
        if p2 == None:
            return pk
        if p2 == p1:
            return pk
        pk = p2    


def check_bound_mov(ps, i, pes):
    p1 = ps[i]
    ppn = ps[(i + 1) % len(ps)]
    if ((p1.realvert.index, ppn.realvert.index) not in pes) and \
        ((ppn.realvert.index, p1.realvert.index) not in pes):
        return False
    return True


def solve_bevel(bm, sel, prop_plen, prop_ths, prop_merge, prop_mdist, cut, prop_engine):
    selresult = True
    fs1 = []
    for e1 in sel:
        for f1 in e1.link_faces:
            fs1.append(f1)
    fs1 = set(fs1)
    fso = set(bm.faces) - fs1
    es = sel

    # add custom layer for vertices
    layer1 = bm.verts.layers.float_vector.new("original")
    for v in bm.verts:
        v[layer1] = v.co.copy()

    # 0.001
    res = bmesh.ops.bevel(bm, geom=es, offset=0.001, offset_type='OFFSET', segments=1, profile=0.5,  affect='EDGES')
    bm.verts.ensure_lookup_table()    
    fs1 = res['faces']

    voriginal = {}
    for f1 in fs1:
        for p1 in f1.loops:
            v = p1.vert[layer1]
            voriginal[p1.vert] = v

    pes = []
    for f1 in fs1:
        f1.select = True and selresult
        for p1 in f1.loops:
            pes.append((p1.vert.index, p1.link_loop_next.vert.index))

    pes = set(pes)

    fs2 = set(bm.faces) - set(fs1) - fso
    fs2 = list(fs2)

    vmap = {}
    for f1 in fs2:
        for v1 in f1.verts:
            vmap[v1] = []

    global mat    
    for f1 in fs2:
        matp = get_matrix_face(f1)
        ps = create_ps(f1, matp)
        mat = matp.inverted()
        ps2 = solve_face(bm, ps, pes, prop_plen, prop_ths)  
        for p in ps2:
            if p.realvert != None and p.vert.co != None:
                # vmap[p.realvert] = mat @ p.vert.co
                vmap[p.realvert].append( mat @ p.vert.co)
    
    for v1 in vmap:
        # v1.co = vmap[v1]
        mv = vmap[v1]
        if len(mv) == 0:
            continue
        elif len(mv) == 1:
            v1.co = mv[0]
        else:
            ms = []
            for v2 in mv:
                d1 = (v2 - v1.co).length
                ms.append((d1, v2))
            d1, v2 = min(ms, key=lambda x: x[0])
            v1.co = v2

    
    vs2 = []
    for f1 in fs2:
        for v1 in f1.verts:
            vs2.append(v1)
    vs2 = list(set(vs2))
        
    if cut > 0:
        surround_net(bm, fs1, fs2, prop_ths, cut, voriginal, prop_plen, prop_engine, selresult)

    if prop_merge:
        bmesh.ops.remove_doubles(bm, 
                verts=vs2, dist=prop_mdist)



def get_round(p1, p2, p3):
    v1 = p1.vert
    vs = []
    for e1 in v1.link_edges:
        v2 = e1.other_vert(v1)
        if v2 == p2.vert or v2 == p3.vert:
            continue
        vs.append(v2)
    return vs


def flip(p1):
    p2 = p1.link_loop_radial_next
    p3 = p2.link_loop_next.link_loop_next
    return p3


def get_back_linked_edge(p1):
    p2 = flip(p1)
    p3 = p2.link_loop_prev
    e1 = p3.edge
    return e1




def bend_face(bm, vs2, voriginal, snmap, cut, vcen):
    ps = vs2[0]
    for i in range(len(ps)):
        i2 = (i + 1) % len(ps)
        p1, sub1 = ps[i]
        p2, _ = ps[i2]
        co = get_bend_sub(bm, p1, p2, voriginal, snmap, cut)        
        if co == None:
            continue
        for k in range(len(sub1)):
            pk = sub1[k]
            c1 = co[k]
            pk.co = c1


def colinear(v1, v2):
    m1 = v1.normalized()
    m2 = v2.normalized()
    if abs(m1.dot(m2)) > 0.999:
        return True
    return False


def get_bend_sub(bm, p1, p2, voriginal, snmap, cut):
    if p1 not in voriginal:
        return None
    elif p2 not in voriginal:
        return None

    if p1 not in snmap or p2 not in snmap:
        return None
    else:
        s1 = snmap[p1]
        s2 = snmap[p2]
        c1 = s1.cross(s2)
        if c1.length == 0:
            return None

    q1 = voriginal[p1]
    q2 = voriginal[p2]

    s1 = snmap[p1]
    s2 = snmap[p2]
    c1 = s1.cross(s2)

    ss1 = c1.cross(s1)
    ss2 = s2.cross(c1)

    ot1 = p1.co + ss1
    ot2 = p2.co + ss2

    if colinear(ss1, ss2):
        return None
    
    pin = intersect3d(p1.co, ot1, p2.co, ot2)
    # if pin != None:
    #     edge2(bm, p1.co, pin)

    if pin == None:
        return None
        
    # if pin == None:
    #     po1 = get_loop(p1, p2)
    #     po2 = get_loop(p2, p1)
    #     if po1 == None or po2 == None:
    #         return None
        
    #     b1 = rotate_side(po1, 2)
    #     b2 = rotate_side(po2, 2)

    #     ot1 = b1.edge.other_vert(p1)
    #     ot2 = b2.edge.other_vert(p2)
    #     if ot1 not in voriginal or ot2 not in voriginal:
    #         return None
    #     d1 = voriginal[ot1] - voriginal[p1]
    #     d2 = voriginal[ot2] - voriginal[p2]

    #     pin = intersect3d(p1.co, p1.co + d1, p2.co, p2.co + d2)
    #     if pin == None:
    #         return None

    m1 = pin - p1.co
    m2 = pin - p2.co

    bs = mathutils.geometry.interpolate_bezier(p1.co, p1.co + m1/2, p2.co + m2/2, p2.co, cut+2)

    # q3 = (voriginal[p1] + voriginal[p2]) / 2            
    bs2 = bs[1:-1]
    return bs2




def fillet_poly(bm, vs2, snmap, voriginal, cut, vcen, plen, prop_engine):
    ps = vs2[0]

    bounds = []
    for p1, sub in ps:
        bounds.append(p1.co[:])
        for v1 in sub:
            bounds.append(v1.co[:])

    for i in range(len(ps)):
        i2 = (i + 1) % len(ps)
        p1, sub = ps[i]
        p2, _ = ps[i2]
        sub2 = get_bend_sub(bm, p1, p2, voriginal, snmap, cut)
        if sub2 == None:
            continue
        if len(sub) != len(sub2):
            continue
        for k in range(len(sub)):
            v1 = sub[k]
            po1 = sub2[k]
            v1.co = po1
    
    bounds2 = []
    for p1, sub in ps:
        bounds2.append(p1.co[:])
        for v1 in sub:
            bounds2.append(v1.co[:])

    points = []
    for ps in vs2[1:]:
        for p1, sub in ps:
            points.append(p1.co[:])
            for v1 in sub:
                points.append(v1.co[:])
    for v in vcen:
        points.append(v.co[:])

    if prop_engine == 1:
        points2 = move_forward(points, bounds, bounds2)
    elif prop_engine == 2:
        points2 = move_forward_type2(points, bounds, bounds2)
    cc = 0

    dislimit = plen * 2


    for ps in vs2[1:]:
        for p1, sub in ps:
            a1 = Vector(points2[cc])            
            if (a1 - p1.co).length < dislimit:                
                p1.co = a1
            cc += 1
            for v1 in sub:
                a1 = Vector(points2[cc])                
                if (a1 - v1.co).length < dislimit:
                    v1.co = a1                
                cc += 1
    for v1 in vcen:
        a1 = Vector(points2[cc])        
        if (a1 - v1.co).length < dislimit:
            v1.co = a1        
        cc += 1

    return vs2



def engine2(r, epsilon=1.0):
    return np.exp(-epsilon * r**2)

def move_forward_type2(points, boundary_points, new_boundary_points):
    points = np.array(points)
    boundary_points = np.array(boundary_points)
    new_boundary_points = np.array(new_boundary_points)
    
    Phi = np.zeros((len(boundary_points), len(boundary_points)))
    for i in range(len(boundary_points)):
        for j in range(len(boundary_points)):
            r = np.linalg.norm(boundary_points[i] - boundary_points[j])
            Phi[i, j] = engine2(r)
        
    D = new_boundary_points - boundary_points
    # weights = np.linalg.solve(Phi, D)
    weights, _, _, _ = np.linalg.lstsq(Phi, D, rcond=None)
        
    displacements = np.zeros_like(points)
    for i, p in enumerate(points):
        for j, bp in enumerate(boundary_points):
            r = np.linalg.norm(bp - p)
            displacements[i] += weights[j] * engine2(r)
        
    new_points = points + displacements
    return new_points



def core_func(r, d=1.0):
    if r > d:
        return 0
    else:
        return (1 - r/d)**4 * (4 * r/d + 1)


def move_forward(points, boundary_points, new_boundary_points, support_distance=1.0):
    points = np.array(points)
    boundary_points = np.array(boundary_points)
    new_boundary_points = np.array(new_boundary_points)
    
    n_boundary = len(boundary_points)
    Phi = np.zeros((n_boundary, n_boundary))
    for i in range(n_boundary):
        for j in range(n_boundary):
            r = np.linalg.norm(boundary_points[i] - boundary_points[j])
            Phi[i, j] = core_func(r, support_distance)
    
    D = new_boundary_points - boundary_points    
    weights, _, _, _ = np.linalg.lstsq(Phi, D, rcond=None)
    
    
    displacements = np.zeros_like(points)
    for i, p in enumerate(points):
        for j, bp in enumerate(boundary_points):
            r = np.linalg.norm(bp - p)
            displacements[i] += weights[j] * core_func(r, support_distance)
    
    new_points = points + displacements
    return new_points




def get_slice_fs(bm, ps, cut):    
    vs2 = []    
    for i in range(len(ps)):
        i2 = (i + 1) % len(ps)
        p1 = ps[i]
        p2 = ps[i2]
        m1 = p2.co - p1.co
        m2 = m1 / (cut + 1)        
        sub = []
        for k in range(cut):
            v2 = p1.co + m2 * (k + 1)
            v3 = bm.verts.new(v2)
            # v3.select = True
            sub.append(v3)
        vs2.append((p1, sub))
        
    if cut > 1:
        inner = []
        co = [p1.co for p1 in ps]
        cen = sum(co, Vector()) / len(co)
        for i in range(len(ps)):
            p1 = ps[i]
            mid = p1.co - cen
            m1 = mid / (cut + 1)
            v1 = bm.verts.new(p1.co - m1 * 2)
            inner.append(v1)
        vs3 = get_slice_fs(bm, inner, cut - 2)
        return [vs2] + vs3
    else:
        return [vs2]
    


def get_sub_slice(bm, ps, cut):                 
    if cut > 1:
        inner = []
        co = []
        for p1, sub in ps:
            co.append(p1.co)

        cen = sum(co, Vector()) / len(co)
        for i in range(len(ps)):
            p1, _ = ps[i]
            mid = p1.co - cen
            m1 = mid / (cut + 1)
            v1 = bm.verts.new(p1.co - m1 * 2)
            inner.append(v1)        

        vs2 = []    
        for i in range(len(inner)):
            i2 = (i + 1) % len(inner)
            p1 = inner[i]
            p2 = inner[i2]
            m1 = p2.co - p1.co
            m2 = m1 / (cut + 1-2)        
            sub = []
            for k in range(cut-2):
                v2 = p1.co + m2 * (k + 1)
                v3 = bm.verts.new(v2)
                # v3.select = True
                sub.append(v3)
            vs2.append((p1, sub))

        vs3 = get_sub_slice(bm, vs2, cut - 2)

        return [ps] + vs3
    else:
        return [ps]
    



def link_edge(bm, v1, v2):
    e1 = bm.edges.new([v1, v2])
    # e1.select = True
    return e1
    
        
# def connect_inner(bm, vs2, cut):
#     for i in range(len(vs2) - 1):
#         i2 = i + 1
#         n1 = vs2[i]
#         n2 = vs2[i2]        
#         for k in range(len(n1)):
#             k2 = (k + 1) % len(n1)
#             p1, sub1 = n1[k]
#             p2, sub2 = n2[k]
#             p2b, sub2b = n2[k2]
#             s1 = sub1
#             s2 = [p2] + sub2 + [p2b]
#             for a, b in zip(s1, s2):
#                 link_edge(bm, a, b)
#     for ps in vs2:
#         for i in range(len(ps)):
#             i2 = (i + 1) % len(ps)
#             p1, sub1 = ps[i]
#             p2, sub2 = ps[i2]
#             if len(sub1) == 0:
#                 link_edge(bm, p1, p2)
#                 continue
#             else:
#                 link_edge(bm, p1, sub1[0])
#                 link_edge(bm, sub1[-1], p2)
#                 for k in range(len(sub1) - 1):
#                     k2 = k + 1
#                     link_edge(bm, sub1[k], sub1[k2])
#     center = None
#     if cut % 2 == 1:
#         ps = vs2[-1]
#         vs = [p1 for p1, sub1 in ps]
#         co = [p1.co for p1 in vs]
#         cen = sum(co, Vector()) / len(co)
#         v1 = bm.verts.new(cen)
#         center = v1
#         # v1.select = True
#         for p1, sub1 in ps:
#             if len(sub1) > 0:
#                 v2 = sub1[0]
#                 link_edge(bm, v1, v2)



def rotate_side(p1, num):
    for i in range(num):
        p1 = p1.link_loop_radial_next.link_loop_next
    return p1


def get_loop(p1, p2):
    for p in p1.link_loops:
        e1 = p.edge
        if e1.other_vert(p1) == p2:
            return p
    return None

    
def connect_inner_face(bm, vs2, cut, selresult):         
    for i in range(len(vs2) - 1):
        i2 = i + 1
        n1 = vs2[i]
        n2 = vs2[i2]        
        for k in range(len(n1)):
            k2 = (k - 1) % len(n1)
            p1, sub1 = n1[k]
            p2, sub2 = n2[k]
            p2b, sub2b = n1[k2]
            if len(sub1) == 0:
                continue
            if len(sub2b) == 0:
                continue            
            v1 = sub1[0]
            v2 = sub2b[-1]
            f2 = bm.faces.new([p1, v1, p2, v2])
            f2.select = True and selresult
    for i in range(len(vs2) - 1):
        i2 = i + 1
        n1 = vs2[i]
        n2 = vs2[i2]        
        for k in range(len(n1)):
            k2 = (k + 1) % len(n1)
            p1, sub1 = n1[k]
            p2, sub2 = n2[k]
            p2b, sub2b = n2[k2]
            ins = [p2] + sub2 + [p2b]
            for j in range(len(sub1) - 1):
                j2 = j + 1
                v1 = sub1[j]
                v2 = sub1[j2]
                v3 = ins[j2]
                v4 = ins[j]
                f2 = bm.faces.new([v1, v2, v3, v4])
                f2.select = True and selresult
    # center = None
    if cut % 2 == 1:
        ps = vs2[-1]
        vs = [p1 for p1, sub1 in ps]
        co = [p1.co for p1 in vs]
        cen = sum(co, Vector()) / len(co)
        vcen = bm.verts.new(cen)
        # center = vcen
        # v1.select = True
        for i in range(len(ps)):
            i2 = (i - 1) % len(ps)
            p1, sub1 = ps[i]
            p2, sub2 = ps[i2]
            if len(sub1) > 0 and len(sub2) > 0:
                v2 = sub1[0]
                v3 = sub2[-1]
                f2 = bm.faces.new([p1, v2, vcen, v3])
                f2.select = True and selresult
        return [vcen]
    else:
        ps = vs2[-1]
        vs = [p1 for p1, sub1 in ps]
        if len(vs) >= 3:
            f2 = bm.faces.new(vs)
            f2.select = True and selresult
        return []
                 


def get_outer_normal(bm, fs2):
    vmap = {}
    for f1 in fs2:
        for v1 in f1.verts:
            vmap[v1] = []
    
    for f1 in fs2:
        for v1 in f1.verts:
            vmap[v1].append(f1.normal.copy())

    for v1 in vmap:
        vmap[v1] = sum(vmap[v1], Vector()) / len(vmap[v1])
        vmap[v1].normalize()

    return vmap



def intersect3d(p1, p2, p3, p4):
    pin = mathutils.geometry.intersect_line_line(p1, p2, p3, p4)
    if pin == None:
        return None
    a, b = pin
    c = (a + b) / 2
    return c


# def surround_net(bm, fs1, fs2, prop_ths, cut, voriginal):
#     global mat
#     vs = []
#     for f1 in fs2:
#         for p1 in f1.loops:
#             vs.append(p1.vert)
#     vs = list(set(vs))

#     es = set()
#     border = set()
#     for f1 in fs2:
#         # f1.select = True
#         for p1 in f1.loops:
#             e1 = get_back_linked_edge(p1)
#             es.add(e1)
#             border.add(p1.edge)

#     snmap = get_outer_normal(fs2)
    
#     side = {}
#     tube = []
#     for f1 in fs1:
#         flen = len(f1.loops)
#         fc = 0
#         for p1 in f1.loops:
#             if p1.edge in es:
#                 fc += 1
#         if fc == flen:
#             # f1.select = True
#             vs = [p1.vert for p1 in f1.loops]
#             vs2 = get_slice_fs(bm, vs, cut)  
#             vs2 = deform_poly(bm, vs, vs2, snmap, voriginal, cut)          
#             s1 = vs2[0]
#             for i in range(len(f1.loops)):
#                 p1 = f1.loops[i]
#                 pk, sub = s1[i]
#                 side[p1.edge] = list(reversed(sub))

#             connect_inner_face(bm, vs2, cut)
#         else:
#             tube.append(f1)

#     make_tubes(fs1, tube, side, es, bm, border)
#     # bmesh.ops.delete(bm, geom=list(fs1), context='FACES')
                    
                        
def divide_edge(bm, e1, cut):
    if len(e1.link_loops) != 2:
        return None
    p1 = e1.link_loops[0]
    p2 = e1.link_loops[1]
    m1 = p2.vert.co - p1.vert.co
    m2 = m1 / (cut + 1)
    sub = []
    for i in range(cut):
        v2 = p1.vert.co + m2 * (i + 1)
        v3 = bm.verts.new(v2)
        # v3.select = True
        sub.append(v3)
    res = ((p1, sub), (p2, list(reversed(sub))))
    return res



def surround_net(bm, fs1, fs2, prop_ths, cut, voriginal, plen, prop_engine, selresult):
    esbevel = set()
    esborder = set()
    for f1 in fs2:
        # f1.select = True
        for e1 in f1.edges:
            esborder.add(e1)
    for f1 in fs1:                
        for e1 in f1.edges:
            esbevel.add(e1)
    hs = esbevel - esborder

    submap = {}
    snmap = get_outer_normal(bm, fs2)

    for e1 in hs:
        # e1.select = True
        sub = divide_edge(bm, e1, cut)
        if sub == None:
            continue
        ((p1, sub1), (p2, sub2)) = sub
        submap[p1] = sub1
        submap[p2] = sub2    
        # a, b = e1.verts
        # edge2(bm, a.co, b.co)    

    fscore = set()
    fstube = set()
    for f1 in fs1:
        flen = len(f1.loops)
        fc = 0
        for p1 in f1.loops:
            if p1.edge in hs:
                fc += 1
        if fc == flen:
            fscore.add(f1)
        else:
            fstube.add(f1)

    fsvs = []
    fscen = []

    for f1 in fscore:        
        vs = []
        for p1 in f1.loops:
            if p1 not in submap:
                continue
            sub = submap[p1]
            # vs.append(p1.vert)
            vs.append((p1.vert, sub))

        vs2 = get_sub_slice(bm, vs, cut)
        cens = connect_inner_face(bm, vs2, cut, selresult)
        fsvs.append(vs2)
        fscen.append(cens)

    nondelete = set()

    for f1 in fstube:
        # f1.select = True
        ec = []
        for p1 in f1.loops:
            e1 = p1.edge
            if e1 in hs:
                ec.append(p1)
        if len(ec) == 0:
            nondelete.add(f1)
            continue            

        elif len(ec) == 1:
            p1 = ec[0]
            if p1 in submap:
                vs = [p.vert for p in f1.loops]
                pindex = vs.index(p1.vert)
                sub1 = submap[p1]
                vs2 = vs[:pindex+1] + sub1 + vs[pindex+1:]
                f2 = bm.faces.new(vs2)
                f2.select = True and selresult
                
        elif len(ec) == 2:
            p1, p2 = ec
            if p1 in submap and p2 in submap:
                sub1 = [p1.vert] + submap[p1] + [p1.link_loop_next.vert]
                sub2 = [p2.vert] + submap[p2] + [p2.link_loop_next.vert]
                sub2 = list(reversed(sub2)) 
                for i in range(len(sub1) - 1):
                    i2 = i + 1
                    v1 = sub1[i]
                    v2 = sub1[i2]
                    v3 = sub2[i2]
                    v4 = sub2[i]
                    f2 = bm.faces.new([v1, v2, v3, v4])
                    f2.select = True and selresult

    for i in range(len(fscore)):
        vs2 = fsvs[i]
        vcen = fscen[i]
        fillet_poly(bm, vs2, snmap, voriginal, cut, vcen, plen, prop_engine)


    for e1 in hs:
        if len(e1.link_loops) == 0:
            continue
        p1 = e1.link_loops[0]
        v2 = e1.other_vert(p1.vert)
        # p2 = e1.link_loops[1]
        if p1 not in submap:
            continue
        sub1 = submap[p1]
        co = get_bend_sub(bm, p1.vert, v2, voriginal, snmap, cut)        
        if co == None:
            continue
        for k in range(len(sub1)):
            pk = sub1[k]
            c1 = co[k]
            pk.co = c1

    fdel = set(fs1) - nondelete
    if len(fdel) > 0:
        bmesh.ops.delete(bm, geom=list(fdel), context='FACES')





def make_tubes(fs1, tube, side, es, bm, border):
    added = set()
    for f1 in tube:
        # f1.select = True
        for p1 in f1.loops:            
            p2 = p1.link_loop_next
            p3 = p2.link_loop_next
            p4 = p3.link_loop_next
            in_es = p1.edge in es and p3.edge in es
            in_side = p1.edge in side and p3.edge in side
            if in_es and in_side:
                sub1 = side[p1.edge]
                sub2 = side[p3.edge]
                for i in range(len(sub1) - 1):
                    i2 = i + 1
                    i3 = len(sub1) - i - 1
                    i4 = len(sub1) - i2 - 1
                    v1 = sub1[i]
                    v2 = sub2[i3]
                    v3 = sub2[i4]
                    v4 = sub1[i2]
                    if (p1.edge, p3.edge) in added:
                        continue
                    added.add((p3.edge, p1.edge))
                    bm.faces.new([v1, v2, v3, v4])                    
                    
                v1 = p1.vert
                v2 = sub1[0]
                v3 = sub2[-1]
                v4 = p4.vert
                bm.faces.new([v1, v2, v3, v4])   


 



class HardBevelOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.hard_bevel_operator"
    bl_label = "Hard Bevel —— 安全倒角"
    bl_options = {"REGISTER", "UNDO"}
    #, "GRAB_CURSOR", "BLOCKING"


    prop_plen: FloatProperty(
        name="Bevel size",
        description="Bevel size",
        default=0.15,
        step=0.2,
        min=0,
    )    

    prop_ths: FloatProperty(
        name="Threshold",
        description="检查限制的阈值",
        default=0.01,
        step=0.2,
        min=0
    )          


    prop_merge: BoolProperty(
        name="Merge Result",
        description="合并结果的闭合顶点",
        default=False,
    )    



    prop_mdist: FloatProperty(
        name="Merge Distance",
        description="Merge Distance",
        default=0.04,
        step=0.2,
        min=0
    )    


    prop_engine: IntProperty(
        name="Fillet Engine",
        description="圆角的类型",
        default=1,
        min=1,
        max=2
    )          


    prop_cut: IntProperty(
        name="切割次数",
        description="切割次数",
        default=1,
        min=1
    )       




    def get_bm(self):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        return bm



    def process(self, context):
        bm = self.get_bm() 
        # sel = [f1 for f1 in bm.faces if f1.select]
        sel = [e1 for e1 in bm.edges if e1.select]

        cut = self.prop_cut - 1
        solve_bevel(bm, sel, self.prop_plen, self.prop_ths, self.prop_merge, self.prop_mdist, cut, self.prop_engine)

        obj = bpy.context.active_object                
        me = bpy.context.active_object.data
        bmesh.update_edit_mesh(me)  


    def execute(self, context):
        self.process(context)      
        return {'FINISHED'}    

    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        selecting = active_object is not None and active_object.type == 'MESH'        
        editing = context.mode == 'EDIT_MESH' 
        is_vert_mode, is_edge_mode, is_face_mode = context.tool_settings.mesh_select_mode
        return selecting and editing 


    def invoke(self, context, event): 
        self.prop_plen = 0.15 
        self.prop_ths = 0.01                    
                
        if context.edit_object:
            self.process(context)
            return {'FINISHED'} 
        else:
            return {'CANCELLED'}



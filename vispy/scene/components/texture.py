# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Normal components are modular shader components used for retrieving or
generating surface normal vectors.

These components generate a function in the fragment shader that accepts no
arguments and returns a vec4 normal vector. Typically, the normal vector
is computed in the vertex shader and passed by varying to the fragment
shader.
"""

from __future__ import division

from .component import VisualComponent
from ..shaders import Varying
from ... import gloo


class TextureComponent(VisualComponent):
    """
    Component that reads a texture uniform.

    A separate texture coordinate component must be provided.
    If the texture coordinate is outside the edge of the texture, then
    the fragment is discarded.
    """

    SHADERS = dict(
        frag_color="""
            vec4 texture_read() {
                vec2 tex_coord = $texture_coordinate();
                if(tex_coord.x < 0.0 || tex_coord.x > 1.0 ||
                tex_coord.y < 0.0 || tex_coord.y > 1.0) {
                    discard;
                }
                return texture2D($texture, tex_coord.xy);
            }
        """)

    def __init__(self, texture, tex_coord_comp):
        super(TextureComponent, self).__init__()
        self.tex_coord_comp = tex_coord_comp
        self.texture = texture
        self._deps = [tex_coord_comp]

    def activate(self, program, mode):
        # Texture coordinates are generated by a separate component.
        ff = self._funcs['frag_color']
        ff['texture_coordinate'] = self.tex_coord_comp.coord_shader()
        #ff['texture'] = ('uniform', 'sampler2D', self.texture)
        ff['texture'] = self.texture


class VertexTextureCoordinateComponent(VisualComponent):
    """
    Class that reads texture coordinates from a vertex buffer.
    """
    SHADERS = dict(
        vert_post_hook="""
            void texture_coord_support() {
                $tex_local_pos = $local_pos;
            }
        """,
        texture_coord="""
            vec2 vertex_tex_coord() {
                vec4 tex_coord = $map_local_to_tex($tex_local_pos);
                return tex_coord.xy;
            }
        """)

    # exclude texture_coord when auto-attaching shaders because the visual
    # does not have a 'texture_coord' hook; instead this function will be
    # called by another component.
    AUTO_ATTACH = ['vert_post_hook']

    def __init__(self, transform):
        super(VertexTextureCoordinateComponent, self).__init__()
        self.transform = transform

    def coord_shader(self):
        """
        Return the fragment shader function that returns a texture coordinate.
        """
        return self._funcs['texture_coord']

    def activate(self, program, mode):
        ff = self.coord_shader()
        ff['tex_local_pos'] = Varying('v_tex_local_pos', dtype='vec4')
        ff['map_local_to_tex'] = self.transform.shader_map()
        self._funcs['vert_post_hook']['tex_local_pos'] = ff['tex_local_pos']
        self._funcs['vert_post_hook']['local_pos'] = self.visual._program.vert['local_pos']


class TextureCoordinateComponent(VisualComponent):
    """
    Component that outputs texture coordinates derived from the local vertex
    coordinate and a transform.
    """

    SHADERS = dict(
        vert_post_hook="""
            void texture_coord_support() {
                $tex_coord_output = $tex_coord;
            }
        """,
        texture_coord="""
            vec2 tex_coord() {
                return $tex_coord_input;
            }
        """)

    # exclude texture_coord when auto-attaching shaders because the visual
    # does not have a 'texture_coord' hook; instead this function will be
    # called by another component.
    AUTO_ATTACH = ['vert_post_hook']

    def __init__(self, coords):
        super(TextureCoordinateComponent, self).__init__()
        self.coords = coords
        self._vbo = None

    def coord_shader(self):
        """
        Return the fragment shader function that returns a texture coordinate.
        """
        return self._funcs['texture_coord']

    @property
    def vbo(self):
        if self._vbo is None:
            self._vbo = gloo.VertexBuffer(self.coords)
        return self._vbo

    def activate(self, program, mode):
        vf = self._funcs['vert_post_hook']
        vf['tex_coord_output'] = Varying('v_tex_coord', dtype='vec2')
        self._funcs['texture_coord']['tex_coord_input'] = \
            vf['tex_coord_output']
        vf['tex_coord'] = self.vbo  # attribute vec2

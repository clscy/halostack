#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014

# Author(s):

# Panu Lahtinen <pnuu+git@iki.fi>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

'''Module for coaligning images'''

import numpy as np

class Align(object):
    '''Class to coalign images
    '''
    def __init__(self, img, ref_loc=None, srch_area=None, mode='simple'):

        modes = {'simple': self._simple_match}

        self.img = img
        self.ref_loc = ref_loc
        self.srch_area = srch_area
        self.ref = None
        try:
            self.align_func = modes[mode]
        except AttributeError:
            self.align_func = self._simple_match

        if ref_loc is not None:
            self._set_ref()
        if srch_area is None:
            y_size, x_size = self.img.shape
            self.srch_area = [0, 0, y_size, x_size]

    def set_reference(self, area):
        '''Set the reference area *area*.
        param area: 3-tuple of the form (x, y, radius)
        '''
        self.ref_loc = area

    def set_search_area(self, area):
        '''Set the reference search area *area*.
        param area: 4-tuple of the form (x1, x2, y1, y2)
        '''
        self.srch_area = area

    def align(self, img):
        '''Align the given image with the reference image.
        '''

        # Get the correlation and the location of the best match
        corr, x_loc, y_loc = self.align_func(img)
        # Calculate shift
        x_shift, y_shift = self._calc_shift(x_loc, y_loc)
        # Shift the image
        img = self._shift(img, x_shift, y_shift)

        return img

    def _set_ref(self):
        '''Set reference values.
        '''
        self.ref = self.img[self.ref_loc[0]-self.ref_loc[2]:\
                                self.ref_loc[0]+self.ref_loc[2]+1,
                            self.ref_loc[1]-self.ref_loc[2]:\
                                self.ref_loc[1]+self.ref_loc[2]+1]

    def _find_reference(self, img):
        '''Find the reference area from the given image.
        '''
        pass

    def _fft_match(self, img):
        '''Use FFT to find the best alignment.
        '''
        pass

    def _simple_match(self, img):
        '''Use least squared difference to find the best alignment. Slow.
        '''

        # Image and reference sizes
        img_shp = list(img.shape)
        # loop is from {x,y} +- ref_{x,y} so divide by two
        ref_shp = [x/2 for x in self.ref.shape]

        ylims = [self.srch_area[1]-self.srch_area[2],
                 self.srch_area[1]+self.srch_area[2]]
        xlims = [self.srch_area[0]-self.srch_area[2],
                 self.srch_area[0]+self.srch_area[2]]

        # Check area limits
        # minimums
        if xlims[0] < ref_shp[1]:
            xlims[0] = ref_shp[1]
        if ylims[0] < ref_shp[0]:
            ylims[0] = ref_shp[0]
        # maximums
        if xlims[1] >= img_shp[1] - ref_shp[1]:
            xlims[1] = img_shp[1] - ref_shp[1] - 1
        if ylims[1] >= img_shp[0] - ref_shp[0]:
            ylims[1] = img_shp[0] - ref_shp[0] - 1

        best_res = [2**64, None, None]

        for i in range(xlims[0], xlims[1]):
            xran = range(i-ref_shp[1], i+ref_shp[1]+1)
            for j in range(ylims[0], ylims[1]):
                sqdif = ((img[j-ref_shp[0]:j+ref_shp[0]+1,
                              xran]-self.ref)**2).sum()
                if sqdif < best_res[0]:
                    best_res = [sqdif, i, j]

        # Calculate correlation coeff for the best fit
        best_fit_data = img[best_res[2]-ref_shp[0]:best_res[2]+ref_shp[0]+1,
                            best_res[1]-ref_shp[1]:best_res[1]+ref_shp[1]+1]
        best_fit_data = best_fit_data.flatten()
        ref_flat = self.ref.flatten()
        best_corr = np.corrcoef(best_fit_data, ref_flat)**2

        print "###########"
        print xlims, ylims
        print best_corr[0, 1], best_res[1], best_res[2]
        print "###########"

        return (best_corr[0, 1], best_res[1], best_res[2]) # corr, x, y

    def _calc_shift(self, x_loc, y_loc):
        '''Calculate how much the images need to be shifted.
        '''
        print "--------------------"
        print x_loc, y_loc, self.ref_loc
        print "--------------------"
        return self.ref_loc[0] - x_loc, self.ref_loc[1] - y_loc

    def _shift(self, img, x_shift, y_shift):
        '''Shift the image by x_shift and y_shift pixels.
        '''
        new_img = 0*img
        output_x_range, output_y_range, input_x_range, input_y_range = \
            self._calc_shift_ranges(x_shift, y_shift)
        print "##########"
        print self.img.shape
        print x_shift, y_shift
        print output_x_range, output_y_range
        print input_x_range, input_y_range
        print "##########"
        new_img[output_y_range[0]:output_y_range[1],
                output_x_range[0]:output_x_range[1], :] = \
            img[input_y_range[0]:input_y_range[1],
                input_x_range[0]:input_x_range[1], :]

        return new_img

    def _calc_shift_ranges(self, x_shift, y_shift):
        '''Calculate shift indices for input and output arrays.
        '''
        # width of the portion to be moved
        width = self.img.shape[1] - int(np.fabs(x_shift))
        # height of the portion to be moved
        height = self.img.shape[0] - int(np.fabs(y_shift))

        # Calculate the corner indices of the area to be moved
        if x_shift < 0:
            n_x1, n_x2 = 0, width
            o_x1, o_x2 = -1*x_shift, -1*x_shift+width
        else:
            n_x1, n_x2 = x_shift, x_shift+width
            o_x1, o_x2 = 0, width
        if y_shift < 0:
            n_y1, n_y2 = 0, height
            o_y1, o_y2 = -1*y_shift, -1*y_shift+height
        else:
            n_y1, n_y2 = y_shift, y_shift+height
            o_y1, o_y2 = 0, height

        output_x_range = (n_x1, n_x2)
        output_y_range = (n_y1, n_y2)
        input_x_range = (o_x1, o_x2)
        input_y_range = (o_y1, o_y2)

        return output_x_range, output_y_range, input_x_range, input_y_range

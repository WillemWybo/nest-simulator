# -*- coding: utf-8 -*-
#
# test_compartmental_model.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

"""
Tests for the compartmental model
"""

import nest
import unittest
import math
import numpy as np


SP =  {'C_m': 1.00, 'g_c': 0.00, 'g_L': 0.100, 'e_L': -70.0}
DP = [
      {'C_m': 0.10, 'g_c': 0.10, 'g_L': 0.010, 'e_L': -70.0},
      {'C_m': 0.08, 'g_c': 0.11, 'g_L': 0.007, 'e_L': -70.0},
      {'C_m': 0.09, 'g_c': 0.07, 'g_L': 0.011, 'e_L': -70.0},
      {'C_m': 0.15, 'g_c': 0.12, 'g_L': 0.014, 'e_L': -70.0},
      {'C_m': 0.20, 'g_c': 0.32, 'g_L': 0.022, 'e_L': -55.0},
      {'C_m': 0.12, 'g_c': 0.12, 'g_L': 0.010, 'e_L': -23.0},
      {'C_m': 0.32, 'g_c': 0.09, 'g_L': 0.032, 'e_L': -32.0},
      {'C_m': 0.01, 'g_c': 0.05, 'g_L': 0.001, 'e_L': -88.0},
      {'C_m': 0.02, 'g_c': 0.03, 'g_L': 0.002, 'e_L': -90.0},
     ]


def create_1dend_1comp(dt=0.1):
    """
    0
    |
    1
    """
    # create nest model with two compartments
    nest.ResetKernel()
    nest.SetKernelStatus(dict(resolution=dt))
    n_neat = nest.Create('cm_main')
    nest.SetStatus(n_neat, {'V_th': 100.})


    nest.AddCompartment(n_neat, 0, -1, SP)
    nest.AddCompartment(n_neat, 1, 0, DP[0])

    m_neat = nest.Create('multimeter', 1, {'record_from': ['v_comp0', 'v_comp1'], 'interval': .1})
    nest.Connect(m_neat, n_neat)

    # create equivalent matrices for inversion test
    aa = np.zeros((2,2))
    bb = np.zeros(2)

    aa[0,0] = SP['C_m'] / dt + SP['g_L'] / 2. +  DP[0]['g_c'] / 2.
    aa[0,1] = -DP[0]['g_c'] / 2.;
    aa[1,0] = -DP[0]['g_c'] / 2.;
    aa[1,1] = DP[0]['C_m'] / dt + DP[0]['g_L'] / 2. + DP[0]['g_c'] / 2.

    bb[0] = SP['C_m'] / dt * SP['e_L'] + SP['g_L'] * SP['e_L'] / 2. - \
            DP[0]['g_c'] * (SP['e_L'] - DP[0]['e_L']) / 2.
    bb[1] = DP[0]['C_m'] / dt * DP[0]['e_L'] + DP[0]['g_L'] * DP[0]['e_L'] / 2. - \
            DP[0]['g_c'] * (DP[0]['e_L'] - SP['e_L']) / 2.

    # create steady state matrix for attenuation test
    ss = np.zeros((2,2))

    ss[0,0] = - SP['g_L'] - DP[0]['g_c']
    ss[0,1] = DP[0]['g_c']
    ss[1,0] = DP[0]['g_c']
    ss[1,1] = - DP[0]['g_L'] - DP[0]['g_c']

    return (n_neat, m_neat), (aa, bb), ss


def create_2dend_1comp(dt=0.1):
    """
      0
     / \
    1   2
    """
    # create nest model with two compartments
    nest.ResetKernel()
    nest.SetKernelStatus(dict(resolution=dt))
    n_neat = nest.Create('cm_main')
    nest.SetStatus(n_neat, {'V_th': 100.})

    nest.AddCompartment(n_neat, 0, -1, SP)
    nest.AddCompartment(n_neat, 1, 0, DP[0])
    nest.AddCompartment(n_neat, 2, 0, DP[1])

    m_neat = nest.Create('multimeter', 1, {'record_from': ['v_comp0', 'v_comp1', 'v_comp2'], 'interval': .1})
    nest.Connect(m_neat, n_neat)

    # create equivalent matrices for inversion test
    aa = np.zeros((3,3))
    bb = np.zeros(3)

    aa[0,0] = SP['C_m'] / dt + SP['g_L'] / 2. + DP[0]['g_c'] / 2. + DP[1]['g_c'] / 2.

    aa[0,1] = -DP[0]['g_c'] / 2.;
    aa[1,0] = -DP[0]['g_c'] / 2.;
    aa[1,1] = DP[0]['C_m'] / dt + DP[0]['g_L'] / 2. + DP[0]['g_c'] / 2.

    aa[0,2] = -DP[1]['g_c'] / 2.;
    aa[2,0] = -DP[1]['g_c'] / 2.;
    aa[2,2] = DP[1]['C_m'] / dt + DP[1]['g_L'] / 2. + DP[1]['g_c'] / 2.

    bb[0] = SP['C_m'] / dt * SP['e_L'] + SP['g_L'] * SP['e_L'] / 2. - \
            DP[0]['g_c'] * (SP['e_L'] - DP[0]['e_L']) / 2. - \
            DP[1]['g_c'] * (SP['e_L'] - DP[1]['e_L']) / 2.
    bb[1] = DP[0]['C_m'] / dt * DP[0]['e_L'] + DP[0]['g_L'] * DP[0]['e_L'] / 2. - \
            DP[0]['g_c'] * (DP[0]['e_L'] - SP['e_L']) / 2.
    bb[2] = DP[1]['C_m'] / dt * DP[1]['e_L'] + DP[1]['g_L'] * DP[1]['e_L'] / 2. - \
            DP[1]['g_c'] * (DP[1]['e_L'] - SP['e_L']) / 2.

    # create steady state matrix for attenuation test
    ss = np.zeros((3,3))

    ss[0,0] = - SP['g_L'] - DP[0]['g_c'] - DP[1]['g_c']

    ss[0,1] = DP[0]['g_c']
    ss[1,0] = DP[0]['g_c']
    ss[1,1] = - DP[0]['g_L'] - DP[0]['g_c']

    ss[0,2] = DP[1]['g_c']
    ss[2,0] = DP[1]['g_c']
    ss[2,2] = - DP[1]['g_L'] - DP[1]['g_c']

    return (n_neat, m_neat), (aa, bb), ss


def create_1dend_2comp(dt=0.1):
    """
    0
    |
    1
    |
    2
    """
    # create nest model with two compartments
    nest.ResetKernel()
    nest.SetKernelStatus(dict(resolution=dt))
    n_neat = nest.Create('cm_main')
    nest.SetStatus(n_neat, {'V_th': 100.})

    nest.AddCompartment(n_neat, 0, -1, SP)
    nest.AddCompartment(n_neat, 1, 0, DP[0])
    nest.AddCompartment(n_neat, 2, 1, DP[1])

    m_neat = nest.Create('multimeter', 1, {'record_from': ['v_comp0', 'v_comp1', 'v_comp2'], 'interval': .1})
    nest.Connect(m_neat, n_neat)

    # create equivalent matrices for inversion test
    aa = np.zeros((3,3))
    bb = np.zeros(3)

    aa[0,0] = SP['C_m'] / dt + SP['g_L'] / 2. + DP[0]['g_c'] / 2.

    aa[0,1] = -DP[0]['g_c'] / 2.;
    aa[1,0] = -DP[0]['g_c'] / 2.;
    aa[1,1] = DP[0]['C_m'] / dt + DP[0]['g_L'] / 2. + DP[0]['g_c'] / 2. + DP[1]['g_c'] / 2.

    aa[1,2] = -DP[1]['g_c'] / 2.;
    aa[2,1] = -DP[1]['g_c'] / 2.;
    aa[2,2] = DP[1]['C_m'] / dt + DP[1]['g_L'] / 2. + DP[1]['g_c'] / 2.

    bb[0] = SP['C_m'] / dt * SP['e_L'] + SP['g_L'] * SP['e_L'] / 2. - \
            DP[0]['g_c'] * (SP['e_L'] - DP[0]['e_L']) / 2.
    bb[1] = DP[0]['C_m'] / dt * DP[0]['e_L'] + DP[0]['g_L'] * DP[0]['e_L'] / 2. - \
            DP[0]['g_c'] * (DP[0]['e_L'] - SP['e_L']) / 2. - \
            DP[1]['g_c'] * (DP[0]['e_L'] - DP[1]['e_L']) / 2.
    bb[2] = DP[1]['C_m'] / dt * DP[1]['e_L'] + DP[1]['g_L'] * DP[1]['e_L'] / 2. - \
            DP[1]['g_c'] * (DP[1]['e_L'] - SP['e_L']) / 2.

    # create steady state matrix for attenuation test
    ss = np.zeros((3,3))

    ss[0,0] = - SP['g_L'] - DP[0]['g_c']

    ss[0,1] = DP[0]['g_c']
    ss[1,0] = DP[0]['g_c']
    ss[1,1] = - DP[0]['g_L'] - DP[0]['g_c'] - DP[1]['g_c']

    ss[1,2] = DP[1]['g_c']
    ss[2,1] = DP[1]['g_c']
    ss[2,2] = - DP[1]['g_L'] - DP[1]['g_c']

    return (n_neat, m_neat), (aa, bb), ss


def create_tdend_4comp(dt=0.1):
    """
        0
        |
        1
        |
        2
       / \
      3   4
    """
    # create nest model with two compartments
    nest.ResetKernel()
    nest.SetKernelStatus(dict(resolution=dt))
    n_neat = nest.Create('cm_main')
    nest.SetStatus(n_neat, {'V_th': 100.})

    nest.AddCompartment(n_neat, 0, -1, SP)
    nest.AddCompartment(n_neat, 1, 0, DP[0])
    nest.AddCompartment(n_neat, 2, 1, DP[1])
    nest.AddCompartment(n_neat, 3, 2, DP[2])
    nest.AddCompartment(n_neat, 4, 2, DP[3])

    m_neat = nest.Create('multimeter', 1,
                         {'record_from': ['v_comp%d'%ii for ii in range(5)],
                                          'interval': .1})
    nest.Connect(m_neat, n_neat)

    # create equivalent matrices for inversion test
    aa = np.zeros((5,5))
    bb = np.zeros(5)

    aa[0,0] = SP['C_m'] / dt + SP['g_L'] / 2. + DP[0]['g_c'] / 2.

    aa[0,1] = -DP[0]['g_c'] / 2.;
    aa[1,0] = -DP[0]['g_c'] / 2.;
    aa[1,1] = DP[0]['C_m'] / dt + DP[0]['g_L'] / 2. + DP[0]['g_c'] / 2. + DP[1]['g_c'] / 2.

    aa[1,2] = -DP[1]['g_c'] / 2.;
    aa[2,1] = -DP[1]['g_c'] / 2.;
    aa[2,2] = DP[1]['C_m'] / dt + DP[1]['g_L'] / 2. + DP[1]['g_c'] / 2. + DP[2]['g_c'] / 2. + DP[3]['g_c'] / 2.

    aa[2,3] = -DP[2]['g_c'] / 2.;
    aa[3,2] = -DP[2]['g_c'] / 2.;
    aa[3,3] = DP[2]['C_m'] / dt + DP[2]['g_L'] / 2. + DP[2]['g_c'] / 2.

    aa[2,4] = -DP[3]['g_c'] / 2.;
    aa[4,2] = -DP[3]['g_c'] / 2.;
    aa[4,4] = DP[3]['C_m'] / dt + DP[3]['g_L'] / 2. + DP[3]['g_c'] / 2.

    bb[0] = SP['C_m'] / dt * SP['e_L'] + SP['g_L'] * SP['e_L'] / 2. - \
            DP[0]['g_c'] * (SP['e_L'] - DP[0]['e_L']) / 2.
    bb[1] = DP[0]['C_m'] / dt * DP[0]['e_L'] + DP[0]['g_L'] * DP[0]['e_L'] / 2. - \
            DP[0]['g_c'] * (DP[0]['e_L'] - SP['e_L']) / 2. - \
            DP[1]['g_c'] * (DP[0]['e_L'] - DP[1]['e_L']) / 2.
    bb[2] = DP[1]['C_m'] / dt * DP[1]['e_L'] + DP[1]['g_L'] * DP[1]['e_L'] / 2. - \
            DP[1]['g_c'] * (DP[1]['e_L'] - DP[0]['e_L']) / 2. - \
            DP[2]['g_c'] * (DP[1]['e_L'] - DP[2]['e_L']) / 2. - \
            DP[3]['g_c'] * (DP[1]['e_L'] - DP[3]['e_L']) / 2.
    bb[3] = DP[2]['C_m'] / dt * DP[2]['e_L'] + DP[2]['g_L'] * DP[2]['e_L'] / 2. - \
            DP[2]['g_c'] * (DP[2]['e_L'] - DP[1]['e_L']) / 2.
    bb[4] = DP[3]['C_m'] / dt * DP[3]['e_L'] + DP[3]['g_L'] * DP[3]['e_L'] / 2. - \
            DP[3]['g_c'] * (DP[3]['e_L'] - DP[1]['e_L']) / 2.

    # create steady state matrix for attenuation test
    ss = np.zeros((5,5))

    ss[0,0] = - SP['g_L'] - DP[0]['g_c']

    ss[0,1] = DP[0]['g_c']
    ss[1,0] = DP[0]['g_c']
    ss[1,1] = - DP[0]['g_L'] - DP[0]['g_c'] - DP[1]['g_c']

    ss[1,2] = DP[1]['g_c']
    ss[2,1] = DP[1]['g_c']
    ss[2,2] = - DP[1]['g_L'] - DP[1]['g_c']  - DP[2]['g_c'] - DP[3]['g_c']

    ss[2,3] = DP[2]['g_c']
    ss[3,2] = DP[2]['g_c']
    ss[3,3] = - DP[2]['g_L'] - DP[2]['g_c']

    ss[2,4] = DP[3]['g_c']
    ss[4,2] = DP[3]['g_c']
    ss[4,4] = - DP[3]['g_L'] - DP[3]['g_c']

    return (n_neat, m_neat), (aa, bb), ss


def create_2tdend_4comp(dt=0.1):
    """
             0
            / \
           1   5
          /     \
         2       6
        / \     / \
       3   4   7   8
    """
    # create nest model with two compartments
    nest.ResetKernel()
    nest.SetKernelStatus(dict(resolution=dt))
    n_neat = nest.Create('cm_main')
    nest.SetStatus(n_neat, {'V_th': 100.})

    nest.AddCompartment(n_neat, 0, -1, SP)
    # dendrite 1
    nest.AddCompartment(n_neat, 1, 0, DP[0])
    nest.AddCompartment(n_neat, 2, 1, DP[1])
    nest.AddCompartment(n_neat, 3, 2, DP[2])
    nest.AddCompartment(n_neat, 4, 2, DP[3])
    # dendrite 2
    nest.AddCompartment(n_neat, 5, 0, DP[4])
    nest.AddCompartment(n_neat, 6, 5, DP[5])
    nest.AddCompartment(n_neat, 7, 6, DP[6])
    nest.AddCompartment(n_neat, 8, 6, DP[7])

    m_neat = nest.Create('multimeter', 1,
                         {'record_from': ['v_comp%d'%ii for ii in range(9)],
                                          'interval': .1})
    nest.Connect(m_neat, n_neat)

    # create equivalent matrices for inversion test
    aa = np.zeros((9,9))
    bb = np.zeros(9)

    aa[0,0] = SP['C_m'] / dt + SP['g_L'] / 2. + DP[0]['g_c'] / 2. + DP[4]['g_c'] / 2.

    aa[0,1] = -DP[0]['g_c'] / 2.;
    aa[1,0] = -DP[0]['g_c'] / 2.;
    aa[1,1] = DP[0]['C_m'] / dt + DP[0]['g_L'] / 2. + DP[0]['g_c'] / 2. + DP[1]['g_c'] / 2.

    aa[1,2] = -DP[1]['g_c'] / 2.;
    aa[2,1] = -DP[1]['g_c'] / 2.;
    aa[2,2] = DP[1]['C_m'] / dt + DP[1]['g_L'] / 2. + DP[1]['g_c'] / 2. + DP[2]['g_c'] / 2. + DP[3]['g_c'] / 2.

    aa[2,3] = -DP[2]['g_c'] / 2.;
    aa[3,2] = -DP[2]['g_c'] / 2.;
    aa[3,3] = DP[2]['C_m'] / dt + DP[2]['g_L'] / 2. + DP[2]['g_c'] / 2.

    aa[2,4] = -DP[3]['g_c'] / 2.;
    aa[4,2] = -DP[3]['g_c'] / 2.;
    aa[4,4] = DP[3]['C_m'] / dt + DP[3]['g_L'] / 2. + DP[3]['g_c'] / 2.

    aa[0,5] = -DP[4]['g_c'] / 2.;
    aa[5,0] = -DP[4]['g_c'] / 2.;
    aa[5,5] = DP[4]['C_m'] / dt + DP[4]['g_L'] / 2. + DP[4]['g_c'] / 2. + DP[5]['g_c'] / 2.

    aa[5,6] = -DP[5]['g_c'] / 2.;
    aa[6,5] = -DP[5]['g_c'] / 2.;
    aa[6,6] = DP[5]['C_m'] / dt + DP[5]['g_L'] / 2. + DP[5]['g_c'] / 2. + DP[6]['g_c'] / 2. + DP[7]['g_c'] / 2.

    aa[6,7] = -DP[6]['g_c'] / 2.;
    aa[7,6] = -DP[6]['g_c'] / 2.;
    aa[7,7] = DP[6]['C_m'] / dt + DP[6]['g_L'] / 2. + DP[6]['g_c'] / 2.

    aa[6,8] = -DP[7]['g_c'] / 2.;
    aa[8,6] = -DP[7]['g_c'] / 2.;
    aa[8,8] = DP[7]['C_m'] / dt + DP[7]['g_L'] / 2. + DP[7]['g_c'] / 2.

    bb[0] = SP['C_m'] / dt * SP['e_L'] + SP['g_L'] * SP['e_L'] / 2. - \
            DP[0]['g_c'] * (SP['e_L'] - DP[0]['e_L']) / 2. - \
            DP[4]['g_c'] * (SP['e_L'] - DP[4]['e_L']) / 2.

    bb[1] = DP[0]['C_m'] / dt * DP[0]['e_L'] + DP[0]['g_L'] * DP[0]['e_L'] / 2. - \
            DP[0]['g_c'] * (DP[0]['e_L'] - SP['e_L']) / 2. - \
            DP[1]['g_c'] * (DP[0]['e_L'] - DP[1]['e_L']) / 2.
    bb[2] = DP[1]['C_m'] / dt * DP[1]['e_L'] + DP[1]['g_L'] * DP[1]['e_L'] / 2. - \
            DP[1]['g_c'] * (DP[1]['e_L'] - DP[0]['e_L']) / 2. - \
            DP[2]['g_c'] * (DP[1]['e_L'] - DP[2]['e_L']) / 2. - \
            DP[3]['g_c'] * (DP[1]['e_L'] - DP[3]['e_L']) / 2.
    bb[3] = DP[2]['C_m'] / dt * DP[2]['e_L'] + DP[2]['g_L'] * DP[2]['e_L'] / 2. - \
            DP[2]['g_c'] * (DP[2]['e_L'] - DP[1]['e_L']) / 2.
    bb[4] = DP[3]['C_m'] / dt * DP[3]['e_L'] + DP[3]['g_L'] * DP[3]['e_L'] / 2. - \
            DP[3]['g_c'] * (DP[3]['e_L'] - DP[1]['e_L']) / 2.

    bb[5] = DP[4]['C_m'] / dt * DP[4]['e_L'] + DP[4]['g_L'] * DP[4]['e_L'] / 2. - \
            DP[4]['g_c'] * (DP[4]['e_L'] - SP['e_L']) / 2. - \
            DP[5]['g_c'] * (DP[4]['e_L'] - DP[5]['e_L']) / 2.
    bb[6] = DP[5]['C_m'] / dt * DP[5]['e_L'] + DP[5]['g_L'] * DP[5]['e_L'] / 2. - \
            DP[5]['g_c'] * (DP[5]['e_L'] - DP[4]['e_L']) / 2. - \
            DP[6]['g_c'] * (DP[5]['e_L'] - DP[6]['e_L']) / 2. - \
            DP[7]['g_c'] * (DP[5]['e_L'] - DP[7]['e_L']) / 2.
    bb[7] = DP[6]['C_m'] / dt * DP[6]['e_L'] + DP[6]['g_L'] * DP[6]['e_L'] / 2. - \
            DP[6]['g_c'] * (DP[6]['e_L'] - DP[5]['e_L']) / 2.
    bb[8] = DP[7]['C_m'] / dt * DP[7]['e_L'] + DP[7]['g_L'] * DP[7]['e_L'] / 2. - \
            DP[7]['g_c'] * (DP[7]['e_L'] - DP[5]['e_L']) / 2.

    # create steady state matrix for attenuation test
    ss = np.zeros((9,9))

    ss[0,0] = - SP['g_L'] - DP[0]['g_c'] - DP[4]['g_c']

    ss[0,1] = DP[0]['g_c']
    ss[1,0] = DP[0]['g_c']
    ss[1,1] = - DP[0]['g_L'] - DP[0]['g_c'] - DP[1]['g_c']

    ss[1,2] = DP[1]['g_c']
    ss[2,1] = DP[1]['g_c']
    ss[2,2] = - DP[1]['g_L'] - DP[1]['g_c']  - DP[2]['g_c'] - DP[3]['g_c']

    ss[2,3] = DP[2]['g_c']
    ss[3,2] = DP[2]['g_c']
    ss[3,3] = - DP[2]['g_L'] - DP[2]['g_c']

    ss[2,4] = DP[3]['g_c']
    ss[4,2] = DP[3]['g_c']
    ss[4,4] = - DP[3]['g_L'] - DP[3]['g_c']

    ss[0,5] = DP[4]['g_c']
    ss[5,0] = DP[4]['g_c']
    ss[5,5] = - DP[4]['g_L'] - DP[4]['g_c'] - DP[5]['g_c']

    ss[5,6] = DP[5]['g_c']
    ss[6,5] = DP[5]['g_c']
    ss[6,6] = - DP[5]['g_L'] - DP[5]['g_c']  - DP[6]['g_c'] - DP[7]['g_c']

    ss[6,7] = DP[6]['g_c']
    ss[7,6] = DP[6]['g_c']
    ss[7,7] = - DP[6]['g_L'] - DP[6]['g_c']

    ss[6,8] = DP[7]['g_c']
    ss[8,6] = DP[7]['g_c']
    ss[8,8] = - DP[7]['g_L'] - DP[7]['g_c']

    return (n_neat, m_neat), (aa, bb), ss


@nest.ll_api.check_stack
class NEASTTestCase(unittest.TestCase):
    """ tests for compartmental NEST models """

    def test_inversion(self, dt=0.1, model_name='1dend_1comp'):
        """
        Test the matrix inversion corresponding to one integration step
        """
        (n_neat, m_neat), (aa, bb), _ = eval('create_%s(dt=dt)'%model_name)

        n_comp = len(bb)
        i_in = 0.1 * np.arange(1, n_comp + 1)

        for ii, i_amp in enumerate(i_in):
            # add current
            nest.Connect(nest.Create('dc_generator', {'amplitude': i_amp}), n_neat,
                         syn_spec={'synapse_model': 'static_synapse', 'weight': 1.,
                                   'delay': dt, 'receptor_type': ii}
                        )

            bb[ii] += i_amp

        # run the NEST model for 2 timesteps (input arrives only on second step)
        nest.Simulate(3.*dt)
        events_neat = nest.GetStatus(m_neat, 'events')[0]
        v_neat = np.array([events_neat['v_comp%d'%ii][-1] for ii in range(n_comp)])

        # construct numpy solution
        v_sol = np.linalg.solve(aa, bb)

        self.assertTrue(np.allclose(v_neat, v_sol))

    def test_all_inversion(self, dt=0.1):
        self.test_inversion(dt=dt, model_name='1dend_1comp')
        self.test_inversion(dt=dt, model_name='2dend_1comp')
        self.test_inversion(dt=dt, model_name='1dend_2comp')
        self.test_inversion(dt=dt, model_name='tdend_4comp')

    def test_no_inp_inversion(self, dt=0.1, model_name='2tdend_4comp'):
        """
        Test the matrix inversion corresponding to one integration step when
        leak potentials vary across the neuron.

        We can not apply input because it can arrive at the earliest at the
        second time-step, but the initial conditions will be differen from
        the leak reversal
        """
        (n_neat, m_neat), (aa, bb), _ = eval('create_%s(dt=dt)'%model_name)

        # need to add zero input otherwise the simulation don't run
        n_comp = len(bb)
        i_in = np.zeros(n_comp)

        for ii, i_amp in enumerate(i_in):
            # add current
            nest.Connect(nest.Create('dc_generator', {'amplitude': i_amp}), n_neat,
                         syn_spec={'synapse_model': 'static_synapse', 'weight': 1.,
                                   'delay': dt, 'receptor_type': ii}
                        )

            bb[ii] += i_amp

        # run the NEST model for 1 timestep
        nest.Simulate(2.*dt)
        events_neat = nest.GetStatus(m_neat, 'events')[0]
        v_neat = np.array([events_neat['v_comp%d'%ii][0] for ii in range(n_comp)])

        # construct numpy solution
        v_sol = np.linalg.solve(aa, bb)

        self.assertTrue(np.allclose(v_neat, v_sol))

    def test_attenuation(self, model_name='1dend_1comp', dt=0.1, i_amp=1., t_max=2000.):
        """
        Test the attenuation properties of the models
        """
        (n_neat, m_neat), _, gg = eval('create_%s(dt=dt)'%model_name)
        n_comp = gg.shape[0]

        # compute impedance matrix from conductance matrix
        zz = np.linalg.inv(-gg)

        for ii in range(n_comp):
            (n_neat, m_neat), _, gg = eval('create_%s(dt=dt)'%model_name)
            # add current
            nest.Connect(nest.Create('dc_generator', {'amplitude': i_amp}), n_neat,
                         syn_spec={'synapse_model': 'static_synapse', 'weight': 1.,
                                   'delay': t_max/2., 'receptor_type': ii})

            # run the NEST model
            nest.Simulate(t_max)
            events_neat = nest.GetStatus(m_neat, 'events')[0]
            v_neat = np.array([events_neat['v_comp%d'%ii][-1] - \
                               events_neat['v_comp%d'%ii][int(t_max/(2.*dt))-1] \
                               for ii in range(n_comp)])

            att_neat = v_neat / v_neat[ii]
            att_sol = zz[ii,:] / zz[ii,ii]

            self.assertTrue(np.allclose(att_neat, att_sol))

    def test_all_attenuation(self, dt=0.1, i_amp=1., t_max=300.):
        self.test_attenuation(model_name='1dend_1comp', dt=dt, i_amp=i_amp, t_max=t_max)
        self.test_attenuation(model_name='2dend_1comp', dt=dt, i_amp=i_amp, t_max=t_max)
        self.test_attenuation(model_name='1dend_2comp', dt=dt, i_amp=i_amp, t_max=t_max)
        self.test_attenuation(model_name='tdend_4comp', dt=dt, i_amp=i_amp, t_max=t_max)
        self.test_attenuation(model_name='2tdend_4comp', dt=dt, i_amp=i_amp, t_max=t_max)

    def test_equilibrium(self, dt=0.1, t_max=200., model_name='2tdend_4comp'):
        """
        Test whether the model converges to the correct equilibrium potential
        """
        (n_neat, m_neat), _, gg = eval('create_%s(dt=dt)'%model_name)
        n_comp = gg.shape[0]

        gl = np.array([SP['g_L']] + [DP[ii]['g_L'] for ii in range(n_comp-1)])
        el = np.array([SP['e_L']] + [DP[ii]['e_L'] for ii in range(n_comp-1)])

        # add current
        nest.Connect(nest.Create('dc_generator', {'amplitude': 0.}), n_neat,
                     syn_spec={'synapse_model': 'static_synapse', 'weight': 1.,
                               'delay': .1, 'receptor_type': 0})

        # run the NEST model
        nest.Simulate(t_max)
        events_neat = nest.GetStatus(m_neat, 'events')[0]
        v_neat = np.array([events_neat['v_comp%d'%ii][-1] for ii in range(n_comp)])

        # explicit solution for steady state voltage
        v_sol = np.linalg.solve(-gg, gl*el)

        print(v_neat)
        print(v_sol)

        self.assertTrue(np.allclose(v_neat, v_sol))

    def test_conductance_input(self, model_name='1dend_1comp', dt=.01, t_max=300.):
        """
        Test whether the voltage is correct under steady state conductance input
        (input spike every time-step)
        """
        # ampa synapse constants
        tau_r = .2
        tau_d = 3.
        weight = .001
        # synaptic conductance window surface
        tp = (tau_r * tau_d) / (tau_d - tau_r) * np.log(tau_d / tau_r);
        surf = (tau_d - tau_r ) / (-np.exp(-tp / tau_r) + np.exp(-tp / tau_d));

        # create the nest model
        (n_neat, m_neat), _, gg = eval('create_%s(dt=dt)'%model_name)
        n_comp = gg.shape[0]

        gl = np.array([SP['g_L']] + [DP[ii]['g_L'] for ii in range(n_comp-1)])
        el = np.array([SP['e_L']] + [DP[ii]['e_L'] for ii in range(n_comp-1)])
        print(el)

        syn_weights = weight * np.arange(1,n_comp+1)

        # average synaptic conductances
        gs = np.zeros(n_comp)
        gs = syn_weights * surf

        for ii, sw in enumerate(syn_weights):
            syn_idx = nest.AddReceptor(n_neat, ii, "AMPA")

            # add AMPA synapse
            sg = nest.Create('spike_generator', 1, {'spike_times': np.arange(0.1, t_max, dt)})
            nest.Connect(sg, n_neat,
                         syn_spec={'synapse_model': 'static_synapse', 'weight': sw*dt,
                                   'delay': .1, 'receptor_type': syn_idx})

        # run the NEST model
        nest.Simulate(t_max)
        events_neat = nest.GetStatus(m_neat, 'events')[0]
        v_neat = np.array([events_neat['v_comp%d'%ii][-1] for ii in range(n_comp)])

        # explicit solution for steady state voltage
        v_sol = np.linalg.solve(-gg + np.diag(gs), gl*el)

        print(v_neat)
        print(v_sol)

        self.assertTrue(np.allclose(v_neat, v_sol, rtol=1e-4))

    def test_all_conductance_input(self, dt=.01, t_max=300.):
        self.test_conductance_input(model_name='1dend_1comp')
        self.test_conductance_input(model_name='2dend_1comp')
        self.test_conductance_input(model_name='1dend_2comp')
        self.test_conductance_input(model_name='tdend_4comp')
        self.test_conductance_input(model_name='2tdend_4comp')


    def test_spike_transmission(self, dt=.01):
        dt = 0.1

        nest.ResetKernel()
        nest.SetKernelStatus(dict(resolution=dt))

        soma_params = {
            'C_m': 1.0,
            'g_c': 0.1,
            'g_L': 0.1,
            'e_L': -70.0,
        }

        n_neat_0 = nest.Create('cm_main')
        nest.AddCompartment(n_neat_0, 0, -1, soma_params)

        n_neat_1 = nest.Create('cm_main')
        nest.AddCompartment(n_neat_1, 0, -1, soma_params)
        syn_idx = nest.AddReceptor(n_neat_1, 0, "AMPA")

        nest.Connect(n_neat_0, n_neat_1, syn_spec={'synapse_model': 'static_synapse', 'weight': .1,
                                                   'receptor_type': syn_idx})

        dc = nest.Create('dc_generator', {'amplitude': 2.0})
        nest.Connect(dc, n_neat_0, syn_spec={'synapse_model': 'static_synapse', 'weight': 1.,
                                             'receptor_type': 0})

        m_neat_0 = nest.Create('multimeter', 1, {'record_from': ['v_comp0'], 'interval': dt})
        nest.Connect(m_neat_0, n_neat_0)

        m_neat_1 = nest.Create('multimeter', 1, {'record_from': ['v_comp0'], 'interval': dt})
        nest.Connect(m_neat_1, n_neat_1)

        nest.Simulate(100.)

        events_neat_0 = nest.GetStatus(m_neat_0, 'events')[0]
        events_neat_1 = nest.GetStatus(m_neat_1, 'events')[0]

        self.assertTrue(np.any(events_neat_0['v_comp0'] != soma_params['e_L']))
        self.assertTrue(np.any(events_neat_1['v_comp0'] != soma_params['e_L']))


def suite():

    # makeSuite is sort of obsolete http://bugs.python.org/issue2721
    # using loadTestsFromTestCase instead.
    suite = unittest.TestLoader().loadTestsFromTestCase(NEASTTestCase)
    return unittest.TestSuite([suite])


def run():
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())


if __name__ == "__main__":
    run()

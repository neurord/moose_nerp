from collections import namedtuple
import engineering_notation as eng

Chn_param = namedtuple("params", "A_A A_B A_C A_D A_F B_A B_B B_C B_D B_F")
Voltage_scale = namedtuple("Voltage_scale", "VDIVS VMIN VMAX")

#EREST_ACT = -70e-3
EREST_ACT = eng.EngUnit('-70mV')

def get_voltage_scales():
    global EREST_ACT
    VMIN = -30e-3 + EREST_ACT
    VMAX = 120e-3 + EREST_ACT
    VDIVS = 3000
    return Voltage_scale(VDIVS, VMIN, VMAX)

def get_na_m_params(vshift=0, tau_multiplier=1, f_offset=0):
  global EREST_ACT
  return Chn_param(
  A_A = -1e5 * (-25e-3 - EREST_ACT - vshift)*tau_multiplier,
  A_B = -1e5*tau_multiplier,
  A_C = -1.0,
  A_D = -25e-3 - EREST_ACT - vshift,
  A_F = -10e-3 + f_offset,

  B_A = 4e3*tau_multiplier,
  B_B = 0.0*tau_multiplier,
  B_C = 0.0,
  B_D = 0.0 - EREST_ACT - vshift,
  B_F = 18e-3 + f_offset)

def get_na_h_params(vshift=0, tau_multiplier=1, f_offset=0):
  global EREST_ACT
  return Chn_param(
  A_A = 70.0*tau_multiplier,
  A_B = 0.0*tau_multiplier,
  A_C = 0.0,
  A_D = 0.0 - EREST_ACT - vshift,
  A_F = 0.02 + f_offset,

  B_A = 1000.0*tau_multiplier,
  B_B = 0.0*tau_multiplier,
  B_C = 1.0,
  B_D = -30e-3 - EREST_ACT - vshift,
  B_F =  -0.01 + f_offset)

def get_k_n_params(vshift=0, tau_multiplier=1, f_offset=0):
  global EREST_ACT
  return Chn_param(
  A_A = -1e4 * (-10e-3 - EREST_ACT - vshift)*tau_multiplier,
  A_B = -1e4*tau_multiplier,
  A_C = -1.0,
  A_D = -10e-3 - EREST_ACT - vshift,
  A_F = -10e-3 + f_offset,

  B_A = 0.125e3*tau_multiplier,
  B_B = 0.0*tau_multiplier,
  B_C = 0.0,
  B_D = 0.0 - EREST_ACT - vshift,
  B_F = 80e-3 + f_offset)

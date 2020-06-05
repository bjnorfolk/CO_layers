#### MLM : Molecular Layer Mapper

import casa_cube as casa
import measure_height
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import rotate
from colorama import Fore, Style
import os

#Sz (y,x) = 750, 752  , WaOph6 (y,x) = 720,719  , HD142527 (y,x) = channel 1 = 170, 161, channel 110 = 162, 155 == 166, 158
#sources systemic velocity:
# IM Lupi = 48 inc, 143 PA, 4.5 km/s , 161 pc. point scatter(limit) < 0.04 and star limit < 0.025

#sources = ['AS209', 'HD163296', 'SR4', 'Sz129', 'WaOph6', 'DoAR25', 'Elias27', 'GWLup', 'HD142666', 'HD143006', HD142527]
#inc_list = [35, 47, 22, 34, 47, 67, 56, 38, 62, 19, 69]
#PA_list = [87, 133, 18, 151, 174, 111, 119, 38, 162, 169, 160]
#v_syst_list = [4.75, 5.7, 5, 4, 3.85]#, -, -, -, -, -, 3.45]
#distance_list = [121, 101, 134, 161, 123, 138, 116, 155, 148, 165, 230]

### plotting options
plot_layers = False
plot_continuum = False
plot_rotated_cube = False

### adjust these parameters for each source
source_name = 'HD142527'
isotope = ['12CO','13CO','C18O']
inclination = 20                  # in degrees
position_angle = 160#95              # in degrees    
systemic_velocity = 3.45           # same units as in the cube
distance = 230                    # in parsecs
iso = 1                          # no. of isotopes from 'isotope' list to run

###############################################################################################################

plot = ['height', 'velocity', 'brightness temperature']
axis = ['r (au)', 'h (au)', 'v (km/s)', 'Tb (K)']

inc = np.radians(inclination)
PA = position_angle
v_syst = systemic_velocity
sigma = 5
condition = False

continuum = casa.Cube(f'{source_name}_continuum.fits')
source_cube = casa.Cube(f'{source_name}_{isotope[0]}_contsub.fits')
for j in range(100):
    y_star, x_star = measure_height.star_location(source_cube, continuum, j, PA=PA, condition=condition) 
    condition = input("happy with star coordinates? [y/n] : ")
    if condition == 'y':
        if plot_continuum is True:
            plt.grid(b=None)
            plt.legend(loc='upper right', prop={'size': 8})
            plt.savefig(f'{source_name}_continuum.png')
        plt.close()
        break

directory = f'{source_name}_layers_contsub_test'
if not os.path.exists(directory):
    os.mkdir(directory)

for k in range(3):
    plt.figure(plot[k])
    plt.clf()
    plt.xlabel(axis[0], labelpad=7)
    plt.ylabel(axis[k+1], labelpad=7)

for i in range(iso):
        
    source = casa.Cube(f'{source_name}_{isotope[i]}_contsub.fits')
    print(f'{source_name}_{isotope[i]}')
    
    n, x, y, T, P, x_old, y_old, n0 = measure_height.detect_surface(source, i, isotope, directory, PA=PA, plot=plot_rotated_cube, sigma=sigma, y_star=y_star, x_star=x_star, v_syst=v_syst)

    r, h, v, Tb = measure_height.measure_mol_surface(source, n, x, y, T, inc=inc, x_star=x_star, y_star=y_star, v_syst=v_syst, distance=distance)
    
    measure_height.plotting_mol_surface(r, h, v, Tb, i, isotope)
    
    if plot_layers is True:
        
        nv = source.nv
        for iv in range(nv):
            measure_height.plot_surface(source, n, x, y, T, iv, P, x_old, y_old, n0, PA=PA, win=20)
            plt.plot(x_star, y_star, '.', color='white')
            plt.savefig(f'{directory}/{source_name}_{isotope[i]}_channel_{iv+1}.png')
          
for k in range(3):
    plt.figure(plot[k])
    plt.legend(loc='best')
    plt.savefig(f'{directory}/{source_name}_{isotope[0]}_{plot[k]}.png')
    
plt.show()
   

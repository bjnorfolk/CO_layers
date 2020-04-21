<<<<<<< HEAD
#HD163 = casa.Cube("/Users/cpinte/Observations/HD163/ALMA/Isella/mine/HD163296_CO_100m.s-1.image.fits.gz")
#measure_surface(HD163, 61, plot=True, PA=-45,plot_cut=534,sigma=10, y_star=478)

from scipy.ndimage import rotate, shift
from scipy.interpolate import interp1d
import scipy.constants as sc
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import binned_statistic

import matplotlib.pyplot as plt


def measure_mol_surface(cube, n, x, y, T, inc=None, x_star=None, y_star=None, v_syst= None, plot=None, distance=None, optimize_x_star=None):
    """
    inc (float): Inclination of the source in [degrees].
    """

    inc_rad = np.radians(inc)

    #-- Computing the radius and height for each point
    y_c = 0.5 * (np.sum(y[:,:,:], axis=2)) - y_star
    y_f = y[:,:,1] - y_star
    y_n = y[:,:,0] - y_star

    r = np.hypot(x - x_star, (y_f - y_c) / np.cos(inc_rad)) # does not depend on y_star
    h = y_c / np.sin(inc_rad)
    v = (cube.velocity[:,np.newaxis] - v_syst) * r / ((x - x_star) * np.sin(inc_rad)) # does not depend on y_star

=======
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import rotate, shift
from scipy.interpolate import interp1d
import scipy.constants as sc
from scipy.stats import binned_statistic
from astropy.io import fits
from skimage.transform import resize

##############################################################################

def measure_mol_surface(cube, n, x, y, T, inc=None, x_star=None, y_star=None, v_syst= None, distance=None, optimize_x_star=None):

    ### some things to note:
        # value of x_star plays on dispersion of h and v
        # value of PA creates a huge dispersion
        # value of y_star shift the curve h(r) vertically, massive change on flaring exponent
        # value of inc changes the shape a bit, but increases dispersion on velocity
        # a = above , b = below

    np.set_printoptions(threshold=np.inf) 

    ### computing the radius and height 
    y_a = y[:,:,1]                        # y[channel number, x value, y value above star]
    y_b = y[:,:,0]                        # y[channel number, x value, y value below star]

    y_c = (y_a + y_b) / 2.
    mask = (y_c == 0)                     # removing x coordinates with no mapping.
    y_centre = np.ma.masked_array(y_c,mask).compressed()
    
    if (len(np.where(y_centre.ravel()<y_star)[0]) > 0.5*len(y_centre.ravel())):
        print('upper layer below y_star')
        h = -(y_c - y_star) / np.sin(inc)
        r = np.sqrt((x - x_star)**2 + ((y_c - y_b)/np.cos(inc))**2)
    else:
        print('upper layer above y_star')
        h = (y_c - y_star) / np.sin(inc)
        r = np.sqrt((x - x_star)**2 + ((y_a - y_c)/np.cos(inc))**2)
    
    v = (cube.velocity[:,np.newaxis] - v_syst) * r / ((x - x_star) * np.sin(inc))

    B = np.mean(T[:,:,:],axis=2)
    
>>>>>>> master-holder
    r *= cube.pixelscale
    h *= cube.pixelscale
    if distance is not None:
        r *= distance
        h *= distance

<<<<<<< HEAD
    # value of x_star plays on dispersion of h and v
    # value of PA creates a huge dispersion
    # value of y_star shift the curve h(r) vertically, massive change on flaring exponent
    # value of inc changes the shape a bit, but increases dispersion on velocity

    # -- we remove the points with h<0 (they correspond to values set to 0 in y)
    # and where v is not defined
    mask = (h<0) | np.isinf(v) | np.isnan(v)

    # -- we remove channels that are too close to the systemic velocity
    mask = mask | (np.abs(cube.velocity - v_syst) < 1.5)[:,np.newaxis]

    r = np.ma.masked_array(r,mask)
    h = np.ma.masked_array(h,mask)
    v = np.ma.masked_array(v,mask)
    T = np.ma.masked_array(T[:,:,0],mask)


    # -- If the disc rotates in the opposite direction as expected
    if (np.mean(v) < 0):
        v = -v

    plt.figure('height')
    plt.clf()
    plt.scatter(r.ravel(),h.ravel(),alpha=0.2,s=5)
    plt.show()

    plt.figure('velocity')
    plt.clf()
    plt.scatter(r.ravel(),v.ravel(),alpha=0.2,s=5)
    plt.show()

    #-- Ignoring channels close to systemic velocity
    # change of mind : we do it later

    #-- fitting a power-law
    P, res_h, _, _, _ = np.ma.polyfit(np.log10(r.ravel()),np.log10(h.ravel()),1, full=True)
    x = np.linspace(np.min(r),np.max(r),100)
    plt.figure('height')
    plt.plot(x, 10**P[1] * x**P[0])

    r_data = r.ravel()[np.invert(mask.ravel())]
    h_data = h.ravel()[np.invert(mask.ravel())]
    v_data = v.ravel()[np.invert(mask.ravel())]
    T_data = T.ravel()[np.invert(mask.ravel())]

    #plt.scatter(r_data,h_data)

    bins, _, _ = binned_statistic(r_data,[r_data,h_data], bins=30)
    std, _, _  = binned_statistic(r_data,h_data, 'std', bins=30)

    print("STD =", np.median(std))
    plt.errorbar(bins[0,:], bins[1,:],yerr=std, color="red")

    bins_v, _, _ = binned_statistic(r_data,[r_data,v_data], bins=30)
    std_v, _, _  = binned_statistic(r_data,v_data, 'std', bins=30)

    print("STD =", np.median(std_v))  # min seems a better estimate for x_star than std_h
    plt.figure('velocity')
    plt.errorbar(bins_v[0,:], bins_v[1,:], yerr=std_v, color="red", marker="o", fmt=' ', markersize=2)


    bins_T, _, _ = binned_statistic(r_data,[r_data,T_data], bins=30)
    std_T, _, _  = binned_statistic(r_data,T_data, 'std', bins=30)

    plt.figure('Brightness temperature')
    plt.errorbar(bins_T[0,:], bins_T[1,:], yerr=std_T, color="red", marker="o", fmt=' ', markersize=2)

    # -- Optimize position, inclination (is that posible without a model ?), PA (need to re-run detect surface)
    return r, h, v



=======
    print(f'total no. of points = {len(r.ravel()) - np.sum(mask)}')
    mask1 = np.isinf(v) | np.isnan(v)
    print(f'no. of points with undefined velocities removed = {np.sum(mask1)}')
    mask2 = mask1 | (h<0) | (r>1000)#| (np.abs(cube.velocity[:,np.newaxis] - v_syst) < 0.4)
    print(f'no. of negative height outliers removed = {np.sum(mask2)-np.sum(mask1) - np.sum(mask)}')

    r = np.ma.masked_array(r,mask2).compressed()
    h = np.ma.masked_array(h,mask2).compressed()
    v = np.ma.masked_array(v,mask2).compressed()
    B = np.ma.masked_array(B,mask2).compressed()

    if (np.mean(v) < 0):
        v = -v
    
    mask3 = (v<0)
    print(f'no. of negative velocity outliers removed = {np.sum(mask3)}')
    
    r = np.ma.masked_array(r,mask3).compressed()
    h = np.ma.masked_array(h,mask3).compressed()
    v = np.ma.masked_array(v,mask3).compressed()
    B = np.ma.masked_array(B,mask3).compressed()
    
    Tb = cube._Jybeam_to_Tb(B)

    print(f'no. of plots left for plotting = {len(r.ravel())}')
    
    return r, h, v, Tb



def plotting_mol_surface(r, h, v, Tb, i, isotope):

    bins = 70
    plot = ['height', 'velocity', 'brightness temperature']
    var = [h, v, Tb]
    stat = ['mean', 'mean', 'max']

    for k in range(3):
        plt.figure(plot[k])

        data,_,_ = binned_statistic(r, [r, var[k]], statistic=stat[k], bins=bins)
        std,_,_ = binned_statistic(r, var[k], statistic='std', bins=bins)

        plt.scatter(data[0,:], data[1,:], alpha=0.7, s=5, label=isotope[i])
        plt.errorbar(data[0,:], data[1,:], yerr=std, ls='none')
    
    ### polynomial fitting
    '''
    plt.figure('height') ###
    
    P, res_h, _, _, _ = np.ma.polyfit(np.log10(r.ravel()),np.log10(h.ravel()), 1, full=True)
    #x = np.linspace(np.min(r), 300, 100)
    x = np.linspace(np.min(r),np.max(r),100)
    
    plt.plot(x, 10**P[1] * x**P[0])
    '''
    

    
>>>>>>> master-holder
class Surface(dict):
    """ Represents the set of points defining the molecular surface
    extracted from a cube

    n : int
        Number of abscices where data points were extracted

    x : int
        Abcises of the points

    y : ndarray(float,2)
        Ordinates of the points

    T : ndarray(float,2)
        Brigtness temperature of the points

    PA : best PA found

    Notes
    -----
    There may be additional attributes not listed above depending of the
    specific solver. Since this class is essentially a subclass of dict
    with attribute accessors, one can see which attributes are available
    using the `keys()` method.
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __repr__(self):
        if self.keys():
            m = max(map(len, list(self.keys()))) + 1
            return '\n'.join([k.rjust(m) + ': ' + repr(v)
                              for k, v in sorted(self.items())])
        else:
            return self.__class__.__name__ + "()"

    def __dir__(self):
        return list(self.keys())


<<<<<<< HEAD
def detect_surface(cube, PA=None, plot=False, plot_cut=None, sigma=None, y_star=None, win=20):
    """
    Infer the upper emission surface from the provided cube
    extract the emission surface in each channel and loop over channels

    Args:
        cube (casa instance): An imgcube instance of the line data.

        PA (float): Position angle of the source in [degrees].
        y_star (optional) : position of star in  pixel (in rorated image), used to filter some bad data
        without y_star, more points might be rejected
    """

    nx, nv = cube.nx, cube.nv

=======
def detect_surface(cube, i, isotope, directory, PA=None, plot=False, sigma=None, y_star=None, x_star=None):
    
    nx, nv = cube.nx, cube.nv
    
>>>>>>> master-holder
    n_surf = np.zeros(nv, dtype=int)
    x_surf = np.zeros([nv,nx])
    y_surf = np.zeros([nv,nx,2])
    Tb_surf = np.zeros([nv,nx,2])
<<<<<<< HEAD

    # Measure the rms in 1st channel
    std = np.nanstd(cube.image[1,:,:])

    surface_color = ["red","blue"]

    # Loop over the channels
    for iv in range(nv):
        print(iv,"/",nv-1)
        # Rotate the image so major axis is aligned with x-axis.
=======
    P = np.zeros([nv,2])
    x_old = np.zeros([nv,nx])
    y_old = np.zeros([nv,nx,2])
    n0_surf = np.zeros(nv, dtype=int)
    
    ### measure rms in the 1st channel 
    std = np.nanstd(cube.image[1,:,:])

    ### stepping through each channel map
    for iv in range(nv):

        if iv == nv-1:
            print(f'total number of channels = {nv}')

        ### rotate the image so semi-major axis is aligned with x-axis
>>>>>>> master-holder
        im = np.nan_to_num(cube.image[iv,:,:])
        if PA is not None:
            im = np.array(rotate(im, PA - 90.0, reshape=False))

<<<<<<< HEAD
        # plot channel map as bakcground
        if plot:
            #pdf = PdfPages('CO_layers.pdf')
            plt.figure(win)
            plt.clf()
            plt.imshow(im, origin="lower")#, interpolation="bilinear")


        # Loop over the pixels along the x-axis to find surface
        in_surface = np.full(nx,False)
        j_surf = np.zeros([nx,2], dtype=int)
        j_surf_exact = np.zeros([nx,2])
        T_surf = np.zeros([nx,2])

        for i in range(nx):
            # find the maxima in each vertical cut, at signal above X sigma
            # ignore maxima not separated by at least a beam
            vert_profile = im[:,i]
            j_max = search_maxima(vert_profile,threshold=sigma*std, dx=cube.bmaj/cube.pixelscale)

            if (j_max.size>1): # We need at least 2 maxima to locate the surface
                in_surface[i] = True

                # indices of the back and front side
                j_surf[i,:] = np.sort(j_max[:2])

                # exclude maxima that do not make sense
                if y_star is not None:
                    if (j_surf[i,1] < y_star):
                        # Houston, we have a pb : the back side of the disk cannot appear below the star
                        j_max_sup = j_max[np.where(j_max > y_star)]
                        if j_max_sup.size:
                            j_surf[i,1] = j_max_sup[0]
                            j_surf[i,0] = j_max[0]
                        else:
                            in_surface[i] = False

                    if (np.mean(j_surf[i,:]) < y_star):
                        # the average of the top surfaces cannot be below the star
                        in_surface[i] = False

            # - We have found points in the 2 surfaces
            if in_surface[i]:
                if plot_cut:
                    if plot_cut==i:
                        plt.figure(21)
                        plt.clf()
                        plt.plot(im[:,i])
                        plt.plot(im[:,i],"o", markersize=1)
                        plt.plot(j_max[0],im[j_max[0],i],"o",color=color[0])
                        plt.plot(j_max[1],im[j_max[1],i],"o",color=color[1])

                #-- We find a spatial quadratic to refine position of maxima (like bettermoment does in velocity)
                for k in range(2):
                    j = j_surf[i,k]

=======
        ### plotting rotated velocity cube (if needed)
        if plot is True:
            if iv==0:
                img_rotated_list=[]

            img_rotated_list.append(im)
            img_rotated_array = np.array(img_rotated_list)

            if iv==nv-1:
                fits.writeto(f'{directory}/{isotope[i]}_rotated.fits', img_rotated_array, overwrite=True)
        
        ### setting up arrays in each channel map
        in_surface = np.full(nx,False)         #creates an array the size of nx without a fill value (False).
        j_surf = np.zeros([nx,2], dtype=int)
        j_surf_exact = np.zeros([nx,2])
        T_surf = np.zeros([nx,2])
        
        ### LOOPING THROUGH EACH X-COORDINATE 
        for i in range(nx):
            vert_profile = im[:,i]

            ### finding the flux maxima for each slice in the x-axis
            j_max = search_maxima(vert_profile, y_star, threshold=sigma*std, dx=cube.bmaj/cube.pixelscale)
                
            ### require a minimum of 2 points; to identify surfaces above and below the star 
            if (len(j_max) > 1) & (abs(i - x_star) < 300): 
                in_surface[i] = True
                
                ### storing only the 2 brightest maxima. want j[i,0] to be below the star and j[i,1] to be above.
                j_surf[i,:] = j_max[:2]
                
                ### in case both the brightest points are on one side of the disk
                 
                if (j_surf[i,0] < y_star and j_surf[i,1] < y_star):
                    j_max_2nd = j_max[np.where(j_max > y_star)]
                    if len(j_max_2nd) > 0:
                        j_surf[i,1] = j_max_2nd[0]
                    else:
                        in_surface[i] = False
                            
                elif (j_surf[i,0] > y_star and j_surf[i,1] > y_star):
                    j_max_2nd = j_max[np.where(j_max < y_star)]
                    if len(j_max_2nd) > 0:
                        j_surf[i,0] = j_max_2nd[0]
                    else:
                        in_surface[i] = False
                else:
                    j_surf[i,:] = np.sort(j_max[:2])

                if ((j_surf[i,1] - y_star) > 300) or ((y_star - j_surf[i,0]) > 300):
                    in_surface[i] = False
                
                ### refining position of maxima using a spatial quadratic
                for k in range(2):
                    j = j_surf[i,k]
                    
>>>>>>> master-holder
                    f_max = im[j,i]
                    f_minus = im[j-1,i]
                    f_plus = im[j+1,i]

                    # Work out the polynomial coefficients
                    a0 = 13. * f_max / 12. - (f_plus + f_minus) / 24.
                    a1 = 0.5 * (f_plus - f_minus)
                    a2 = 0.5 * (f_plus + f_minus - 2*f_max)

                    # Compute the maximum of the quadratic
                    y_max = j - 0.5 * a1 / a2
                    f_max = a0 - 0.25 * a1**2 / a2

                    # Saving the coordinates
                    j_surf_exact[i,k] = y_max
<<<<<<< HEAD
                    T_surf[i,k] = cube._Jybeam_to_Tb(f_max) # Converting to Tb (currently assuming the cube is in Jy/beam)

        #-- Now we try to clean out a bit the surfaces we have extracted

        #-- We test if front side is too high or the back side too low
        # this happens when the data gets noisy or diffuse and there are local maxima
        # fit a line to average curve and remove points from front if above average
        # and from back surface if  below average (most of these case should have been dealt with with test on star position)

        # could search for other maxima but then it means that data is noisy anyway
        #e.g. measure_surface(HD163, 45, plot=True, PA=-45,plot_cut=503,sigma=10, y_star=478)
        if np.any(in_surface):
            x = np.arange(nx)
            x1 = x[in_surface]

            y1 = np.mean(j_surf_exact[in_surface,:],axis=1)
            P = np.polyfit(x1,y1,1)

            #x_plot = np.array([0,nx])
            #plt.plot(x_plot, P[1] + P[0]*x_plot)

            #in_surface_tmp = in_surface &  (j_surf_exact[:,0] < (P[1] + P[0]*x)) # test only front surface
            in_surface_tmp = in_surface &  (j_surf_exact[:,0] < (P[1] + P[0]*x)) & (j_surf_exact[:,1] > (P[1] + P[0]*x))

            # We remove the weird point and reddo the fit again to ensure the slope we use is not too bad
            x1 = x[in_surface_tmp]
            y1 = np.mean(j_surf_exact[in_surface_tmp,:],axis=1)
            P = np.polyfit(x1,y1,1)

            #in_surface = in_surface &  (j_surf_exact[:,0] < (P[1] + P[0]*x)) # test only front surface
            in_surface = in_surface & (j_surf_exact[:,0] < (P[1] + P[0]*x)) & (j_surf_exact[:,1] > (P[1] + P[0]*x))

            # Saving the data
            n = np.sum(in_surface)
            n_surf[iv] = n # number of points in that surface
            if n:
                x_surf[iv,:n] = x[in_surface]
                y_surf[iv,:n,:] = j_surf_exact[in_surface,:]
                Tb_surf[iv,:n,:] = T_surf[in_surface,:]

                # We plot the detected points
                if plot:
                    plt.figure(win)
                    plt.plot(x_surf,y_surf[:,0],"o",color=surface_color[0],markersize=1)
                    plt.plot(x_surf,y_surf[:,1],"o",color=surface_color[1],markersize=1)
                    #plt.plot(x_surf,np.mean(y_surf,axis=1),"o",color="white",markersize=1)

                    # We zoom on the detected surfaces
                    plt.xlim(np.min(x_surf) - 10*cube.bmaj/cube.pixelscale,np.max(x_surf) + 10*cube.bmaj/cube.pixelscale)
                    plt.ylim(np.min(y_surf) - 10*cube.bmaj/cube.pixelscale,np.max(y_surf) + 10*cube.bmaj/cube.pixelscale)

                    plt.savefig('layers/channel_'+str(iv+1)+'.png')
                    plt.close()

            #-- test if we have points on both side of the star
            # - remove side with the less points

    #--  Additional spectral filtering to clean the data
    return n_surf, x_surf, y_surf, Tb_surf

    #measure_surface(HD163, 50, plot=True, PA=-45,plot_cut=534,sigma=10, y_star=478)




def plot_surface(cube, n, x, y, Tb, iv, PA=None, win=20):
=======
                    T_surf[i,k] = f_max

        # CLEANING EACH CHANNEL MAP
        if np.any(in_surface):
            
            x = np.arange(nx) 

            n0 = np.sum(in_surface)
            n0_surf[iv] = n0
            if n0 > 0:
                x_old[iv,:n0] = x[in_surface]
                y_old[iv,:n0,:] = j_surf_exact[in_surface,:]
            
            x1 = x[in_surface]
            y1 = np.mean(j_surf_exact[in_surface,:],axis=1)
            y0 = j_surf_exact[in_surface,:]
            
            if np.size(x1) > 10:
                limit = int(np.size(x1)/4)
            else:
                limit = int(np.size(x1))

            if np.size(x1) > 10:
                if (np.mean(x1) < x_star):
                    limit = int(3*limit)
                    x2 = x1[limit:]
                    y2 = y1[limit:]
                else:
                    x2 = x1[:limit]
                    y2 = y1[:limit]
            else:
                x2 = x1[:limit]
                y2 = y1[:limit]
            
            P[iv,:] = np.polyfit(x2,y2,1)

            trend_limit = abs(np.mean(j_surf_exact[:,:],axis=1) - (P[iv,0]*x + P[iv,1])) / (y0[limit-1,1] - y0[limit-1,0])
            
            star_limit = abs(y_star - (P[iv,0]*x_star + P[iv,1])) / (y0[limit-1,1] - y0[limit-1,0]) #(P[iv,0]*x_star + P[iv,1])
            
            in_surface = in_surface & (trend_limit < 0.10) & (star_limit < 0.10)
            
            # Saving the data
            n = np.sum(in_surface)
            n_surf[iv] = n # number of points in that surface
            if n > 0:
                x_surf[iv,:n] = x[in_surface]
                y_surf[iv,:n,:] = j_surf_exact[in_surface,:]
                Tb_surf[iv,:n,:] = T_surf[in_surface,:]
                

    return n_surf, x_surf, y_surf, Tb_surf, P, x_old, y_old, n0_surf



def plot_surface(cube, n, x, y, Tb, iv, P, x_old, y_old, n0, PA=None, win=20):
>>>>>>> master-holder

    im = np.nan_to_num(cube.image[iv,:,:])
    if PA is not None:
        im = np.array(rotate(im, PA - 90.0, reshape=False))

    plt.figure(win)
    plt.clf()
<<<<<<< HEAD
    plt.imshow(im, origin="lower")#, interpolation="bilinear")

    if n[iv]:
        plt.plot(x[iv,:n[iv]],y[iv,:n[iv],0],"o",color="red",markersize=1)
        plt.plot(x[iv,:n[iv]],y[iv,:n[iv],1],"o",color="blue",markersize=1)
        #plt.plot(x,np.mean(y,axis=1),"o",color="white",markersize=1)

        # We zoom on the detected surfaces
        plt.xlim(np.min(x[iv,:n[iv]]) - 10*cube.bmaj/cube.pixelscale,np.max(x[iv,:n[iv]]) + 10*cube.bmaj/cube.pixelscale)
        plt.ylim(np.min(y[iv,:n[iv],:]) - 10*cube.bmaj/cube.pixelscale,np.max(y[iv,:n[iv],:]) + 10*cube.bmaj/cube.pixelscale)




def search_maxima(y, threshold=None, dx=0):
    """
    Returns the indices of the maxima of a function
    Indices are sorted by decreasing values of the maxima

    Args:
         y : array where to search for maxima
         threshold : minimum value of y for a maximum to be detected
         dx : minimum spacing between maxima [in pixel]
    """

    # A maxima is a positive dy followed by a negative dy
    dy = y[1:] - y[:-1]
    i_max = np.where((np.hstack((0, dy)) > 0) & (np.hstack((dy, 0)) < 0))[0]

    if threshold:
        i_max = i_max[np.where(y[i_max]>threshold)]

    # Sort the peaks by height
    i_max = i_max[np.argsort(y[i_max])][::-1]

    # detect small maxima closer than minimum distance dx from a higher maximum
    if i_max.size:
=======
    plt.imshow(im, origin="lower")#, interpolation="bilinear")  

    y_mean = np.mean(y[:,:,:],axis=2)

    y0_mean = np.mean(y_old[:,:,:],axis=2)

    if n0[iv]:
        plt.plot(x_old[iv,:n0[iv]],y_old[iv,:n0[iv],0],"o",color="fuchsia",markersize=1.5, label='B.S. points removed')
        plt.plot(x_old[iv,:n0[iv]],y_old[iv,:n0[iv],1],"o",color="cyan",markersize=1.5, label='T.S. points removed')
        plt.plot(x_old[iv,:n0[iv]],y0_mean[iv,:n0[iv]],"o",color="yellow",markersize=1.5, label='avg. of points removed')
        plt.plot(x_old[iv,:n0[iv]], P[iv,0]*x_old[iv,:n0[iv]] + P[iv,1], '--', color='black', markersize=0.5, label='trend line')
    
    if n[iv]:
        plt.plot(x[iv,:n[iv]],y[iv,:n[iv],0],"o",color="red",markersize=1.5, label='B.S. points kept')
        plt.plot(x[iv,:n[iv]],y[iv,:n[iv],1],"o",color="blue",markersize=1.5, label='T.S. points kept')
        plt.plot(x[iv,:n[iv]],y_mean[iv,:n[iv]],"o",color="orange",markersize=1.5, label='avg. of points kept')

    if n0[iv]:
        # zoom-in on the detected surfaces
        plt.xlim(np.min(x_old[iv,:n0[iv]]) - 5*cube.bmaj/cube.pixelscale, np.max(x_old[iv,:n0[iv]]) + 5*cube.bmaj/cube.pixelscale)
        plt.ylim(np.min(y_old[iv,:n0[iv],:]) - 5*cube.bmaj/cube.pixelscale, np.max(y_old[iv,:n0[iv],:]) + 5*cube.bmaj/cube.pixelscale)
        #adding a legend
        plt.legend(loc='best', prop={'size': 6})
    
        

def search_maxima(y, y_star, threshold=None, dx=0):
    ### passing im[:] as y[:] here ###
    
    ### measuring the change in flux between y[i] and y[i-1]
    dy = y[1:] - y[:-1]

    ### finding maxima. a positive dy followed by a negative dy. don't worry about notation.
    
    i_max = np.where((np.hstack((0, dy)) > 0) & (np.hstack((dy, 0)) < 0))[0]
    
    ### filtering out only y-coordinates above a signal to noise threshold
    if threshold:
        i_max = i_max[np.where(y[i_max]>threshold)]

    ### sorting y-coordinates from highest to lowest in flux
    i_max = i_max[np.argsort(y[i_max])][::-1]

    ### signals must be separated by at least a beam size. to ensure signal is resolved
    if i_max.size > 0:
>>>>>>> master-holder
        if dx > 1:
            flag_remove = np.zeros(i_max.size, dtype=bool)
            for i in range(i_max.size):
                if not flag_remove[i]:
                    flag_remove = flag_remove | (i_max >= i_max[i] - dx) & (i_max <= i_max[i] + dx)
                    flag_remove[i] = False # Keep current max
                    # remove the unwanted maxima
            i_max = i_max[~flag_remove]
<<<<<<< HEAD

    return i_max
=======
    
    return i_max



def star_location(cube, continuum, j, PA=False, condition=False):

    nx = cube.nx
    
    continuum = np.nan_to_num(continuum.image[0,:,:])
    continuum = resize(continuum, (nx,nx))
    continuum = np.array(rotate(continuum, PA - 90.0, reshape=False))

    if j==0:
        star_coordinates = np.where(continuum == np.amax(continuum))
        listofcordinates = list(zip(star_coordinates[0], star_coordinates[1]))
   
        for cord in listofcordinates:
            print('coordinates of maximum in continuum image (y,x) = '+str(cord))

        y_star = cord[0] 
        x_star = cord[1]

        plt.figure('continuum')
        plt.clf()
        plt.imshow(continuum, origin='lower')
        plt.plot(x_star,y_star, '.', color='red', label=f'(x,y) = ({x_star},{y_star})')
        plt.xlim(0.33*nx, 0.66*nx)
        plt.ylim(0.33*nx, 0.66*nx)
        plt.grid(color='white')
        plt.show(block=False)
        
    if condition == 'n':
        y_star = float(input("enter y_star index coordinate :"))
        x_star = float(input("enter x_star index coordinate :"))
        print(y_star,x_star)
        plt.close()

        plt.figure('continuum')
        plt.clf()
        plt.imshow(continuum, origin='lower')
        plt.plot(x_star,y_star, '.', color='red', label=f'(x,y) = ({x_star},{y_star})')
        plt.xlim(0.33*nx, 0.66*nx)
        plt.ylim(0.33*nx, 0.66*nx)
        plt.grid(color='white')
        plt.show(block=False)

    return y_star, x_star
    
>>>>>>> master-holder

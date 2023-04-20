import matplotlib.pyplot as plt
from perlin_noise import PerlinNoise
import numpy as np
from matplotlib.colors import LinearSegmentedColormap


elevation_steps = [0.0, 0.3, 0.7, 0.95, 1.0]

def get_elevation(size):
    xpix, ypix = size
    elevation = np.array([])
    '''Play around with perlin noise to get a better looking landscape (This is required for the lab)'''
    noise1 = PerlinNoise(octaves=5)
    noise2 = PerlinNoise(octaves=5)
    noise3 = PerlinNoise(octaves=6)
    #noise4 = PerlinNoise(octaves=200)
    
    elevation = np.empty((xpix, ypix))
    for i in range(xpix):
        row = np.array([])
        for j in range(ypix):
            noise_val = noise1([i/xpix, j/ypix])
            noise_val += noise2([i/xpix, j/ypix])
            noise_val += 0.5 * noise3([i/xpix, j/ypix])
            #noise_val += 0.07 * noise4([i/xpix, j/ypix])

            row = np.append(row, noise_val)
        elevation[i] = row
    #elevation= np.array([[noise([i/xpix, j/ypix]) for j in range(ypix)] for i in range(xpix)])
    #print(np.shape(elevation))
    return elevation

def elevation_to_rgba(elevation):
    xpix, ypix = np.array(elevation).shape
    
    water = [  79/255, 154/255, 241/255] 
    grass = [   4/255, 164/255,  13/255]
    stone = [  96/255,  96/255,  96/255]
    snow  = [ 217/255, 217/255, 217/255]
    
    mountain = {
        'red': (
            (elevation_steps[0], water[0], water[0]), # Lower Water
            (elevation_steps[1], water[0], grass[0]), # Upper Water/Lower Grass
            (elevation_steps[2], grass[0], stone[0]), # Upper Grass/Lower Stone
            (elevation_steps[3], stone[0],  snow[0]), # Upper Stone/Lower Snow
            (elevation_steps[4],  snow[0],  snow[0]), # Upper Snow
        ),
        'green': (
            (elevation_steps[0], water[1], water[1]), # Lower Water
            (elevation_steps[1], water[1], grass[1]), # Upper Water/Lower Grass
            (elevation_steps[2], grass[1], stone[1]), # Upper Grass/Lower Stone
            (elevation_steps[3], stone[1],  snow[1]), # Upper Stone/Lower Snow
            (elevation_steps[4],  snow[1],  snow[1]), # Upper Snow
        ),
        'blue': (
            (elevation_steps[0], water[2], water[2]), # Lower Water
            (elevation_steps[1], water[2], grass[2]), # Upper Water/Lower Grass
            (elevation_steps[2], grass[2], stone[2]), # Upper Grass/Lower Stone
            (elevation_steps[3], stone[2],  snow[2]), # Upper Stone/Lower Snow
            (elevation_steps[4],  snow[2],  snow[2]), # Upper Snow
        )
    }
    colormap = LinearSegmentedColormap('MountainTerrain', mountain)
    #colormap = plt.cm.get_cmap('gist_earth')
    elevation = (elevation - elevation.min())/(elevation.max()-elevation.min())
    ''' You can play around with colormap to get a landscape of your preference if you want '''
    landscape = np.array([colormap(elevation[i, j])[0:3] for i in range(xpix) for j in range(ypix)]).reshape(xpix, ypix, 3)*255
    landscape = landscape.astype('uint8')
    return landscape
 

get_landscape = lambda size: elevation_to_rgba(get_elevation(size))

if __name__ == '__main__':
    size = 640, 480
    elevation = get_elevation(size)
    pic = elevation_to_rgba(elevation)
    plt.imshow(pic, cmap='gist_earth')
    #plt.show()
    
    #for octaves in range(1,4):
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    x = np.array(range(0,size[1]))
    y = np.array(range(0,size[0]))
    X, Y = np.meshgrid(x, y)
    #Z = get_height(X,Y,get_elevation(size))
    #ax.plot_surface(X, Y, get_elevation(size), rstride=10, cstride=10, cmap='viridis', edgecolor='none')
    ax.plot_surface(X, Y, elevation, rstride=10, cstride=10, cmap='viridis', edgecolor='none')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.invert_xaxis()
    ax.set_zlim3d(-3,3)
    fig.show()
    
    
    plt.show()
    
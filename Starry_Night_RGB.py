# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 08:28:58 2022

@author: jogoz
"""

#Packages used
from PIL import Image             
import numpy as np                
import matplotlib.pyplot as plt   
import requests
from io import BytesIO
import pandas as pd 
import skimage

#Convert starry night hyperlink to python image

URL = 'https://www.moma.org/media/W1siZiIsIjQ2NzUxNyJdLFsicCIsImNvbnZlcnQiLCItcXVhbGl0eSA5MCAtcmVzaXplIDIwMDB4MTQ0MFx1MDAzZSJdXQ.jpg?sha=62618546638d742f'
response = requests.get(URL)
I = Image.open(BytesIO(response.content))

#Get blue channel
a = I
a = np.array(a)
a[:,:,0] *=0
a[:,:,1] *=0
a = Image.fromarray(a)

#Get green channel
G = I
G = np.array(G)
G[:,0,:] *=0
G[:,1,:] *=0
G = Image.fromarray(G)

#Get red channel
R = I
R = np.array(R)
R[0,:,:] *=0
R[1,:,:] *=0
R = Image.fromarray(R)

#Function to convert a specific channel to a set of x y coords
def image_to_dots(image, max_length= 300000, pixel_cutoff=.65, greater_than=False): 
    #Convert to black and white
    I1 = image.convert('L')
    #Convert to array
    img_array = np.asarray(I1)
    #Convert pixels to 0-1 range
    img_array = img_array/255
    #Downsample more and more until desired row count is achieved
    for j in range(3,4):
        r = skimage.measure.block_reduce(img_array[:, :],
                                 (j, j),
                                 np.mean)
        #Rotate our array
        r = np.rot90(r, 3)
        #Create empty DF
        image_df = pd.DataFrame()
        if greater_than is True: 
            #Create a df and get indices for pixels greater than pixel_cutoff
            image_df['X'],image_df['Y']  = np.where(r > pixel_cutoff)
        else: 
            #Create a df and get indices for pixels less than pixel_cutoff
            image_df['X'],image_df['Y']  = np.where(r < pixel_cutoff)
        
        #Break loop if finally under max_length threshold
        if image_df.shape[0] <= max_length:
            return(image_df)
            break

#Find blue X, Y coords
blue = image_to_dots(a, pixel_cutoff=.053, greater_than=False)
blue['Color'] = 'blue'

#Find Green X, Y coords
green = image_to_dots(G, pixel_cutoff=.45, greater_than=True)
green['Color'] = 'green'

#Find Red X,Y coords
red = image_to_dots(R, pixel_cutoff=.6, greater_than=True)
red['Color'] = 'red'

#Combin R,G,B
rgb_df = pd.concat([blue, green, red])

colors = {'blue':'#031985', 'green':'#f6ff00', 'red':'#ff0000'}


plt.scatter(rgb_df['X'], rgb_df['Y'], c= rgb_df['Color'].map(colors), alpha=0.5, s=.3)

plt.grid(False)
plt.axis('off')
plt.show()


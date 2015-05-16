'''Modules used for reading AMRVAC data, routines to be removed'''
#=============================================================================
import numpy as np
from scipy.interpolate import griddata
import vtk as v
import numpy_support as ah
import matplotlib.pyplot as plt
import read

#=============================================================================
def vtu_values(offset,varname,filenameout='data',attribute_mode='cell',type='vtu'):

    if type == 'vtu':
        filename=''.join([filenameout,repr(offset).zfill(4),'.vtu'])
        datareader = v.vtkXMLUnstructuredGridReader()
    elif type == 'pvtu':
        filename=''.join([filenameout,repr(offset).zfill(4),'.pvtu'])
        datareader = v.vtkXMLPUnstructuredGridReader()
        
    datareader.SetFileName(filename)
    datareader.Update()
    data = datareader.GetOutput()
    
    return read.extract(data,varname,attribute_mode=attribute_mode)

#=============================================================================
def vtu_points(offset,filenameout='data',type='vtu'):

    if type == 'vtu':
        filename=''.join([filenameout,repr(offset).zfill(4),'.vtu'])
        datareader = v.vtkXMLUnstructuredGridReader()
    elif type == 'pvtu':
        filename=''.join([filenameout,repr(offset).zfill(4),'.pvtu'])
        datareader = v.vtkXMLPUnstructuredGridReader()

    datareader.SetFileName(filename)
    datareader.Update()
    data = datareader.GetOutput()
    
    vtk_points=data.GetPoints().GetData()
    points=ah.vtk2array(vtk_points)
    return points

#=============================================================================
def vtu_regrid(offset,varname,nregrid,filenameout='data',xrange='none',yrange='none',
               zrange='none',attribute_mode='point',type='pvtu'):        

    if attribute_mode != 'point':
	var = vtu_values(offset,varname,filenameout=filenameout,attribute_mode='topoint',type=type)
    else:
    	var = vtu_values(offset,varname,filenameout=filenameout,attribute_mode=attribute_mode,type=type)
    
    points = read.vtu_points(offset,filenameout=filenameout,type=type)

    return regrid(var,points,nregrid,xrange='none',yrange='none',
               zrange='none')

#=============================================================================
def regrid(var,points,nregrid,xrange='none',yrange='none',
               zrange='none'):
    x=points[:,0]
    y=points[:,1]
    z=points[:,2]

    # reduce dimension of points:
    ndim = points.ndim
    
    # this is needed because griddata freaks out otherwise:
    smalldouble=0.

    if ndim == 1:
        if xrange=='none':
            tmp=(x.max()-x.min())*smalldouble
            xi = np.linspace(x.min()-tmp,x.max()+tmp,nregrid[0])
        else:
            xi = np.linspace(xrange[0],xrange[1],nregrid[0])
        data = griddata(x, var, xi, method='nearest')
 # mask out the faulty points:
        m = data +1. != data +1.
        data=np.ma.masked_array(data,m)
        data_dict={'data': data, 'x': xi}

    if ndim == 2:
        if xrange=='none':
            tmp=(x.max()-x.min())*smalldouble
            xi = np.linspace(x.min()-tmp,x.max()+tmp,nregrid[0])
        else:
            xi = np.linspace(xrange[0],xrange[1],nregrid[0])
        if yrange=='none':
            tmp=(y.max()-y.min())*smalldouble
            yi = np.linspace(y.min()-tmp,y.max()+tmp,nregrid[1])
        else:
            yi = np.linspace(yrange[0],yrange[1],nregrid[1])
        data = griddata((x,y), var, (xi[None,:],yi[:,None]),method='nearest')
 # mask out the faulty points:
        m = data +1. != data +1.
        data=np.ma.masked_array(data,m)
        data_dict={'data': data, 'x': xi, 'y': yi}

    # Not tested (must be very slow): 
    if ndim == 3:
        if xrange=='none':
            tmp=(x.max()-x.min())*smalldouble
            xi = np.linspace(x.min()-tmp,x.max()+tmp,nregrid[0])
        else:
            xi = np.linspace(xrange[0],xrange[1],nregrid[0])
        if yrange=='none':
            tmp=(y.max()-y.min())*smalldouble
            yi = np.linspace(y.min()-tmp,y.max()+tmp,nregrid[1])
        else:
            yi = np.linspace(yrange[0],yrange[1],nregrid[1])
        if zrange=='none':
            tmp=(z.max()-z.min())*smalldouble
            zi = np.linspace(z.min()-tmp,z.max()+tmp,nregrid[2])
        else:
            xi = np.linspace(zrange[0],zrange[1],nregrid[2])
        data = griddata((x,y,z), var, (xi[None,:,:],yi[:,:,None],zi[:,:,None]), method='nearest')
# mask out the faulty points:
        m = data +1. != data +1.
        data=np.ma.masked_array(data,m)
        data_dict={'data': data, 'x': xi, 'y': yi, 'z': zi}
    
    return data_dict
# ------------------------------------------------------
#=============================================================================
def vtk_values(offset,varname,filenameout='data',attribute_mode='point'):
    # This can be used for the legacy vtk data generated by paraview filters.  
    
    filename=''.join([filenameout,repr(offset),'.vtk'])

    datareader = v.vtkDataSetReader()
    datareader.SetFileName(filename)
    datareader.Update()
    data = datareader.GetOutput()
    
    if attribute_mode == 'cell':
        vtk_values = data.GetCellData().GetArray(varname)
    elif attribute_mode == 'point':
        vtk_values = data.GetPointData().GetArray(varname)
    else:
        print "attribute_mode is either 'cell' or 'point'"
        
# this is convenient to convert vtkarrays to numpy arrays
    value = ah.vtk2array(vtk_values)
    return value
# ------------------------------------------------------
#=============================================================================
def vtk_points(offset,filenameout='data'):

    filename=''.join([filenameout,repr(offset),'.vtk'])

    datareader = v.vtkDataSetReader()
    datareader.SetFileName(filename)
    datareader.Update()
    data = datareader.GetOutput()
    
    vtk_points=data.GetPoints().GetData()
    points=ah.vtk2array(vtk_points)
    return points

#=============================================================================
def quickplot(offset,varname,nregrid,min='none',max='none',filenameout='data',xrange='none',yrange='none',
               zrange='none',attribute_mode='topoint',type='pvtu',log='none',nlevels=256):

    data = vtu_regrid(offset,varname,nregrid,filenameout=filenameout,xrange=xrange,yrange=yrange,
               zrange=zrange,attribute_mode=attribute_mode,type=type)

    plt.contour(data,min=min,max=max,xrange=xrange,yrange=yrange,
               zrange=zrange,log='none',nlevels=nlevels)


#=============================================================================
def cplot(data,min='none',max='none',xrange='none',yrange='none',
               zrange='none',log='none',nlevels=256):

    plt.clf()
    plt.gca().set_aspect('equal')
    

    if log == 'none':
        if min == 'none': min = data.get('data').min()
        if max == 'none': max = data.get('data').max()
        v = np.linspace(min, max, nlevels, endpoint=True)
        plt.contourf(data.get('x'),data.get('y'),data.get('data'),v)
    else:
        if min == 'none': min = np.log10(data.get('data').min())
        if max == 'none': max = np.log10(data.get('data').max())
        v = np.linspace(min, max, nlevels, endpoint=True)
        plt.contourf(data.get('x'),data.get('y'),np.log10(data.get('data')),v)
    plt.colorbar()

#=============================================================================
def rgcplot(var,points,nregrid,min='none',max='none',xrange='none',yrange='none',
               zrange='none',log='none',nlevels=256):
    datarg = regrid(var,points,nregrid,xrange=xrange,yrange=yrange,
               zrange=zrange)
    cplot(datarg,min=min,max=max,xrange=xrange,yrange=yrange,
               zrange=zrange,log=log,nlevels=nlevels)
    

#=============================================================================
def quickload(offset,varname,nregrid,filenameout='data',attribute_mode='topoint',type='pvtu',
              xrange='none',yrange='none',zrange='none'):
    
    data = vtu_regrid(offset,varname,nregrid,filenameout=filenameout,xrange=xrange,yrange=yrange,
               zrange=zrange,attribute_mode=attribute_mode,type=type)

    return data.get('data')

#=============================================================================
def quickpoints(offset,nregrid,filenameout='data',type='pvtu',
                xrange='none',yrange='none',zrange='none'):

    
    points = vtu_points(offset,filenameout=filenameout,type=type)

    x=points[:,0]
    y=points[:,1]
    z=points[:,2]

    # reduce dimension of points:
    ndim = points.ndim
    
    # this is needed because griddata freaks out otherwise:
    smalldouble=0.

    if ndim == 1:
        if xrange=='none':
            tmp=(x.max()-x.min())*smalldouble
            xi = np.linspace(x.min()-tmp,x.max()+tmp,nregrid[0])
        else:
            xi = np.linspace(xrange[0],xrange[1],nregrid[0])
        return xi
    
    if ndim == 2:
        if xrange=='none':
            tmp=(x.max()-x.min())*smalldouble
            xi = np.linspace(x.min()-tmp,x.max()+tmp,nregrid[0])
        else:
            xi = np.linspace(xrange[0],xrange[1],nregrid[0])
        if yrange=='none':
            tmp=(y.max()-y.min())*smalldouble
            yi = np.linspace(y.min()-tmp,y.max()+tmp,nregrid[1])
        else:
            yi = np.linspace(yrange[0],yrange[1],nregrid[1])
        return xi,yi
    
    if ndim == 3:
        if xrange=='none':
            tmp=(x.max()-x.min())*smalldouble
            xi = np.linspace(x.min()-tmp,x.max()+tmp,nregrid[0])
        else:
            xi = np.linspace(xrange[0],xrange[1],nregrid[0])
        if yrange=='none':
            tmp=(y.max()-y.min())*smalldouble
            yi = np.linspace(y.min()-tmp,y.max()+tmp,nregrid[1])
        else:
            yi = np.linspace(yrange[0],yrange[1],nregrid[1])
        if zrange=='none':
            tmp=(z.max()-z.min())*smalldouble
            zi = np.linspace(z.min()-tmp,z.max()+tmp,nregrid[2])
        else:
            xi = np.linspace(zrange[0],zrange[1],nregrid[2])
        return xi,yi,zi
#=============================================================================

import numpy as np
import ipywidgets as widgets
import pandas as pd
from IPython.display import clear_output

class receptor:

   def get_srm2(self):

      self.FNO2_srm2 = widgets.BoundedFloatText(
          value=.199,
          min=0.,
          max=1.0,
          step=.01,
          description='FNO2_srm2:',
          disabled=False
         )

      self.conc_NOx_srm2 = widgets.BoundedFloatText(
         value=1.776,
         min = 0.,
         max = 100.,
         description='Conc NOx SRM2:',
         disabled=False
         )
      self.conc_PM10_srm2 = widgets.BoundedFloatText(
         value=.095875,
         min=0.,
         max=100.,
         description='Conc PM10 SRM2:',
         disabled=False
         )
      self.conc_PM25_srm2 = widgets.BoundedFloatText(
         value=.04,
         min=0.,
         max=100.,
         description='Conc PM2.5 SRM2:',
         disabled=False
         )

      display(self.FNO2_srm2)
      display(self.conc_NOx_srm2)
      display(self.conc_PM10_srm2) 
      display(self.conc_PM25_srm2)
  
   def dropdown_var_number_roadparts_eventhandler(self,change):

         clear_output()
         display(self.number_roadparts)

         for id in range(change['old']):            
            self.rijbanen[id].Srmwegtype.close()
            self.rijbanen[id].verkeer.close()
            self.rijbanen[id].FS.close()
            self.rijbanen[id].LWV.close()
            self.rijbanen[id].MWV.close()
            self.rijbanen[id].HWV.close()
            self.rijbanen[id].buses.close()
            self.rijbanen[id].wegtype.close()
            self.rijbanen[id].boomfrac.close()
            self.rijbanen[id].dist.close()

         self.nr_rijbanen(change['new'])

   def nr_rijbanen(self,nr):
         self.rijbanen = [None] * nr
         for nrr in range(nr):
            
            self.rijbanen[nrr] = rijbaan(nrr)
       
   def define_rijbanen(self):
      
    
      self.number_roadparts = widgets.widget_selection.Dropdown(
            options=[1,2],
            value = 1,
            description='Nr road tracks',
            disabled=False,
            )

      self.number_roadparts.observe(self.dropdown_var_number_roadparts_eventhandler,names='value')
      display(self.number_roadparts)
      self.nr_rijbanen(self.number_roadparts.value)
      

   def __init__(self):    
     
     align_kw = dict( _css   = (('.widget-label', 'min-width', '5000ex'),),
                      margin = '10px 20px 5px 12px'
                    )
     style    = {'description_width': '150px'}
     layout   = {'width': '300px'}
     self.RDW_x = widgets.BoundedFloatText(
                     value=133382.0,
                     min=0.,
                     max=280000.0,
                     step=10.,
                     description='RDW_x (m East):',
                     disabled=False,
                     style=style, layout=layout
                     )

     self.RDW_y = widgets.BoundedFloatText(
                     value = 454361.,
                     min=30000.0,
                     max=640000.0,
                     description='RDW_y (m North):',
                     disabled=False,
                     style=style, layout=layout
                     )

     self.year = widgets.widget_selection.Dropdown(
                     options=[2020,2025,2030],
                     value = 2020,
                     description='Year',
                     disabled=False,
                     style=style, layout=layout
                     )
       
     display(self.RDW_x)
     display(self.RDW_y)
     display(self.year)
    
class rijbaan:
  

   def __init__(self,nrr):    
      style    = {'description_width': '200px'}
      layout   = {'width': '400px'}

     
      self.Srmwegtype = widgets.widget_selection.Dropdown(
         options=['non-motorway','motorway'],
         value='non-motorway',
         description='SCM Road Type',
         disabled=False,
         style=style, layout=layout
          )

      self.verkeer = widgets.widget_selection.Dropdown(
         options=['urban normal','urban less congestion','provincial road'],
         value = 'urban normal',
         description='Traffic Type',
         disabled=False,
         style=style, layout=layout
         )   
      self.FS = widgets.BoundedFloatText(
         value=0.,
         min=0.,
         max=1.0,
         step=0.01,
         description='f_s Fraction Stagnation (-)',
         disabled=False,
         style=style, layout=layout
         )
      self.LWV = widgets.BoundedFloatText(
         value=6800.,
         min=0.,
         max=100000000.0,
         step=100,
         description='N_l Intensity Light (veh/24h)',
         disabled=False,
         style=style, layout=layout
         )
      self.MWV = widgets.BoundedFloatText(
          value=165.,
          min=0.,
          max=100000000.0,
          step=100,
          description='N_m Intensity Middle (veh/24h):',
          disabled=False,
         style=style, layout=layout
         )
      self.HWV = widgets.BoundedFloatText(
          value=65.,
          min=0.,
          max=100000000.0,
          step=100,
          description='N_h Intensity Heavy (veh/24h):',
          disabled=False,
         style=style, layout=layout
         )      
      self.buses = widgets.BoundedFloatText(
          value=0.,
          min=0.,
          max=100000000.0,
          step=100,
          description='N_b Intensity Buses (veh/24h)',
          disabled=False,
         style=style, layout=layout
         )
      self.wegtype = widgets.widget_selection.Dropdown(
         options=['1','2','3','4'],
         value = '1',
         description='Road Type',
         disabled=False,
         style=style, layout=layout
         )
      self.boomfrac = widgets.widget_selection.Dropdown(
         options=[1.0,1.25,1.5],
         value = 1.0,
         description='f_t Tree factor',
         disabled=False,
         style=style, layout=layout
         )
      self.dist = widgets.FloatText(
         value=13.0,
         description='Distance (m)',
         disabled=False,
         style=style, layout=layout
         )
  
      print('Give parameters for road section: ',nrr+1)
      display(self.Srmwegtype)
      display(self.verkeer)
      display(self.FS)
      display(self.LWV)
      display(self.MWV)
      display(self.HWV)
      display(self.buses)
      display(self.wegtype)
      display(self.boomfrac)
      display(self.dist)
    
def read_meteo(xloc,yloc,dir):
    

  f = np.flipud(np.loadtxt(dir+'/wv_05-14_280220.aps',skiprows=1))

  f = np.where(f > -1.,f,np.nan)

  nrcols = f.shape[1]
  nrrows = f.shape[0]
  
  xllcr = 0.
  yllcr = 300000.
  cellsize = 1000.
  
  xx = np.linspace(xllcr,xllcr+(nrcols-1)*cellsize,nrcols)
  yy = np.linspace(yllcr,yllcr+(nrrows-1)*cellsize,nrrows)
  
  ind_x = np.argwhere(xx > xloc)
  ind_y = np.argwhere(yy > yloc)
  
  ws = f[ind_y[0]-1,ind_x[0]-1]
  
  return float(ws)

def read_gcn(species,year,xloc,yloc,dir):

  NOx_GCN = dir+'conc_'+species+'_RR'+year+'_2002.asc'
  NOx_rwc = dir+'rwc_'+species+'_RR'+year+'_2002.asc'

  f = open(NOx_GCN,'r')
  lines = f.readlines()

  nrcols = int(lines[0].split(" ")[-1].strip())
  nrrows = int(lines[1].split(" ")[-1].strip())
  xllcr = float(lines[2].split(" ")[-1].strip())
  yllcr = float(lines[3].split(" ")[-1].strip())
  cellsize = float(lines[4].split(" ")[-1].strip())

  gcn_xy = np.flipud(np.loadtxt(NOx_GCN, skiprows=6))
  rwc_xy = np.flipud(np.loadtxt(NOx_rwc, skiprows=6))

  gcn_xy_b = gcn_xy
  gcn_xy_b_withrwc = gcn_xy - rwc_xy
  
  gcn_xy_bn = np.where(gcn_xy_b > -10.,gcn_xy_b,np.nan)
  gcn_xy_bn_withrwc = np.where(gcn_xy_b_withrwc > -10.,gcn_xy_b_withrwc,np.nan)

  xx = np.linspace(xllcr,xllcr+(nrcols-1)*cellsize,nrcols)
  yy = np.linspace(yllcr,yllcr+(nrrows-1)*cellsize,nrrows)

  ind_x = np.argwhere(xx > xloc)
  ind_y = np.argwhere(yy > yloc)
  
  gcn_point = gcn_xy_bn[ind_y[0]-1,ind_x[0]-1]
  gcn_point_withrwc = gcn_xy_bn_withrwc[ind_y[0]-1,ind_x[0]-1]
  
  return float(gcn_point),float(gcn_point_withrwc)


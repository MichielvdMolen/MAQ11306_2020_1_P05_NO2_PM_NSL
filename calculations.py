import pandas as pd

def calc_gcn_meteo_emissfacts(recep, CARII):
    dirin = './Data/'
    dirin = './Data/'
    gcn_bg = {}

#   find the gcn large-scale concentrations nad the gcn concentrations where the contribution of the closest motorways 
#   is substracted from the large scale concentration.
    for species in ['NOx','NO2','O3','PM10','PM25']:
            gcn,gcn_rwc = CARII.read_gcn(species,str(recep.year.value),recep.RDW_x.value,recep.RDW_y.value,dirin)
            gcn_bg.update({species+'_HWN':gcn})
            gcn_bg.update({species+'_noHWN':gcn_rwc})
    recep.gcn = gcn_bg 

#   find the local ten-year average wind speed
    recep.ws = CARII.read_meteo(recep.RDW_x.value,recep.RDW_y.value,dirin) 

#   load the file with emission factors
    recep.fact_emiss = pd.read_excel(dirin+'/Emissiefactoren_2020_v12mrt.xlsx',sheet_name='tabel_alle_stoffen_en_jaren',header=0,index_col=[0,5,6])

#   select only the emission factor for the year given above
    recep.fact_emiss_jaar = recep.fact_emiss[recep.fact_emiss['Jaar'] == recep.year.value]

# determine the regio factor based on the ten-year average wind speed
    recep.Fregio = 5./recep.ws


def calc_Emiss(recep):
    
    f_year = recep.fact_emiss_jaar 
    
# depending on the SCM Road type, emission factors for motorways or non-motorways are selected
    for rijbaan in recep.rijbanen:
        if rijbaan.Srmwegtype.value == 'non-motorway':
            f_all = f_year['Waarde'][f_year['Srmwegtype'] == 'niet-snelweg']
        elif rijbaan.Srmwegtype.value == 'motorway':
            print('Motorway not implemented yet')
            print('Switched to non-motorway')
            f_all = f_year['Waarde'][f_year['Srmwegtype'] == 'niet-snelweg']         
        else:
            print('Illegal Srmwegtype')

        if   rijbaan.verkeer.value == 'urban normal':
            verkeer = 'stad normaal'
        elif rijbaan.verkeer.value == 'urban less congestion':
            verkeer = 'stad doorstromend'
        elif rijbaan.verkeer.value == 'provincial road':
            verkeer = 'buitenweg'
        else:
            print('Incorrect road type')            

# here some copying is done, from rood_part characteristics to local variables.
        FS      = rijbaan.FS.value
        LWV     = rijbaan.LWV.value
        MWV     = rijbaan.MWV.value
        HWV     = rijbaan.HWV.value
        buses   = rijbaan.buses.value
#       verkeer = rijbaan.verkeer.value

# calculate the emissions
        E = {}
        for species in ['NOx','NO2','PM10totaal','PM2.5totaal']:
            E_LWV      = (1.-FS)*LWV  *f_all.loc['Licht wegverkeer',      verkeer,species]+FS  *LWV*f_all.loc['Licht wegverkeer',      'file',species]
            E_MWV      = (1.-FS)*MWV  *f_all.loc['Middelzwaar wegverkeer',verkeer,species]+FS  *MWV*f_all.loc['Middelzwaar wegverkeer','file',species]
            E_HWV      = (1.-FS)*HWV  *f_all.loc['Zwaar wegverkeer',      verkeer,species]+FS  *HWV*f_all.loc['Zwaar wegverkeer',      'file',species]         
            E_bus      = (1.-FS)*buses*f_all.loc['Bussen',                verkeer,species]+FS*buses*f_all.loc['Bussen',                'file',species]              
            E[species] = (E_LWV+E_MWV+E_HWV+E_bus)*1000./(24.*3600.)
        E['PM10'] = E['PM10totaal']
        E['PM25'] = E['PM2.5totaal']
        del(E['PM10totaal'])
        del(E['PM2.5totaal'])
        rijbaan.emiss = E


def calc_concs(recep):
    
# determining the parameters of all road types for calcultion the dispersion factor
    param_dict = {'1':{'a':3.25E-5,'b':-2.05E-2,'c':0.39,'alpha':0.856},'2':{'a':4.88E-4,'b':-3.08E-2,'c':0.59},
              '3':{'a':5.00E-4,'b':-3.16E-2,'c':0.57},'4':{'a':3.1E-4,'b':-1.82E-2,'c':0.33,'alpha':0.799}}
# sum the contributions of all read parts
    conc_NO2_dir  = 0.
    conc_tot_NO   = 0.
    conc_tot_pm10 = 0.
    conc_tot_pm25 = 0.

# perform the calculations for all read parts and sum them up
    for rijbaan in recep.rijbanen:      

# first, calculate for the road part under scop the disperion factor 
# the dispersion factor is a function of distance of the center line of the road part to the receptor point
# and the functional form depends on the distance
        if 3.5 <= rijbaan.dist.value <= 30.:
              theta = param_dict[rijbaan.wegtype.value]['a']*rijbaan.dist.value**2.+param_dict[rijbaan.wegtype.value]['b']*rijbaan.dist.value +param_dict[rijbaan.wegtype.value]['c']
        else:
            try:
                theta = param_dict[rijbaan.wegtype.value]['alpha']*rijbaan.dist.value**(-.747)
            except:
                print('theta not defined for wegtype: ',rijbaan.wegtype.value)
                
# calculation the contribution of the road part under scope to NOx
        conc_NOx = .62*rijbaan.emiss['NOx']*theta*rijbaan.boomfrac.value*recep.Fregio

# calculate the contribution to NO2 by direct emissions of NO2 and add it to the total concentration
        conc_NO2_dir += rijbaan.emiss['NO2']/rijbaan.emiss['NOx']*conc_NOx

# calculate the contribution to NO by the road part under scope and add it to the total contribution
        conc_tot_NO += (1.-rijbaan.emiss['NO2']/rijbaan.emiss['NOx'])*conc_NOx

# calculate the contribution to PM10 by the road part under scope and add it to the total contribution
        conc_pm10 = .62*rijbaan.emiss['PM10']*theta*rijbaan.boomfrac.value*recep.Fregio
        conc_tot_pm10 += conc_pm10

# calculate the contribution to PM2.5 by the road part under scope and add it to the total contribution
        conc_pm25 = .62*rijbaan.emiss['PM25']*theta*rijbaan.boomfrac.value*recep.Fregio
        conc_tot_pm25 += conc_pm25
        
# make the the contribution of traffic by Srm2 road as an attribute of the receptor point
    recep.Cb = {}
    recep.Cb['NO2-dir_srm1'] = conc_NO2_dir # NO2 contributions of direct emissions of NO2 on Srm1 roads
    recep.Cb['NO_srm1']      = conc_tot_NO # NO contribution of Srm1 roads
    recep.Cb['NOx_srm1']     = conc_NO2_dir+conc_tot_NO # NOx contribution of Srm1 roads
    recep.Cb['PM10_srm1']    = conc_tot_pm10 # PM10 contribution of Srm1 roads
    recep.Cb['PM2.5_srm1']   = conc_tot_pm25 #PM2.5 contribution of Srm1 roads
    
    recep.Cb['NOx_srm2']     = recep.conc_NOx_srm2.value # NOx contribution of Srm2 roads
    recep.Cb['FNO2_srm2']    = recep.FNO2_srm2.value # fraction of NO2 emissions over NOx emissions
    recep.Cb['PM10_srm2']    = recep.conc_PM10_srm2.value # PM10 contribution of Srm2 roads
    recep.Cb['PM2.5_srm2']   = recep.conc_PM25_srm2.value # PM2.5 contribution of Srm2 roads
    
    conc_NO2_dir += recep.FNO2_srm2.value*recep.conc_NOx_srm2.value # total traffic contribution of Srm1 and Srm2 roads
    conc_srm2_NO = (1.-recep.FNO2_srm2.value)*recep.conc_NOx_srm2.value # total NO contribution of Srm1 and Srm2 roads

# psrt of the NO emitted by the traffic reacts with ozone, thus augmenting the concentrations of NO2 

    # calculate the equivalent contribution of NO because of traffic on Srm2 roads
    
    eps = conc_srm2_NO/(conc_srm2_NO+100.)*(1./.6)
    conc_NO_srm2_eq = eps/(1.-eps)*100.
    
    # add the equivalent contribution of NO because of traffic on Srm2 roads to the total NO contribution
    
    conc_tot_NO += conc_NO_srm2_eq

# calculation of the total contrition of traffic on Srm2 and Srm1 road on NO2
# it is calculated as the sum of the contribution of traffic because of direct emissions of NO2
# and a contribution to NO2 because part of the NO reacts with ozone to form NO2
    conc_tot_NO2 = conc_NO2_dir+.6*recep.gcn['O3_HWN']*conc_tot_NO/(conc_tot_NO+100.)

# make the the contribution of traffic by Srm1 and Srm2 road an attribute of the receptor point
    recep.Cb  ['NO-tot'] = recep.Cb['NO_srm1'] +conc_srm2_NO              # NO contribution
    recep.Cb  ['NOx'   ] = recep.Cb['NOx_srm1']+recep.conc_NOx_srm2.value # NOx contribution
    recep.Cb  ['NO2'   ] = conc_tot_NO2                                   # NO2 contribution
    recep.Cb  ['PM10'  ] = conc_tot_pm10+recep.conc_PM10_srm2.value       # PM10 contrubution
    recep.Cb  ['PM2.5' ] = conc_tot_pm25+recep.conc_PM25_srm2.value       # PM2.5 contribution

# calculate the total concentrations make them attributes of the receptor point
    recep.Ctot = {}
    recep.Ctot['NO2'   ] = recep.gcn['NO2_noHWN' ]+recep.Cb['NO2'  ]
    recep.Ctot['PM10'  ] = recep.gcn['PM10_noHWN']+recep.Cb['PM10' ]
    recep.Ctot['PM2.5' ] = recep.gcn['PM25_noHWN']+recep.Cb['PM2.5'] 
    recep.Ctot['NOx'   ] = recep.gcn['NOx_noHWN' ]+recep.Cb['NOx'  ]
from CDMSDataCatalog import *
import sys
from ROOT import TFile, TMacro, TString





#strip out file components
localpath=sys.argv[1] 
dcpath=localpath[ int(localpath.find("/CDMS/") ) : int(len(localpath))  ]
filename=dcpath[ dcpath.rfind('/')+1 : len(dcpath) ]
relpath=dcpath[0:dcpath.rfind('/')+1 ]
nEvents=0
f=TFile.Open( localpath ) 
firstSeries="0"
lastSeries="0"

#/CDMS/Soudan/R133/Processed/Releases/Prodv5-3_June2013/merged/byseries/ba/011305a_ba/calib_Prodv5-3_011305a_ba.root
prodv=dcpath[ dcpath.find("Releases/")+9: len(dcpath)]
prodv=prodv[0: prodv.find("/")]

fRun=133
wikilink="http://titus.stanford.edu/dokuwiki/doku.php?id=processing:ddc:r133_production_status"
if localpath.find('R134') >-1 :
    fRun=134
    wikilink="http://titus.stanford.edu/dokuwiki/doku.php?id=processing:ddc:r134_production_status"
if localpath.find('R135') >-1 :
    fRun=135
    wikilink="http://titus.stanford.edu/dokuwiki/doku.php?id=processing:ddc:r135_production_status;http://titus.stanford.edu/dokuwiki/doku.php?id=processing:ddc:prodr135"

dataType=-1
if localpath.find('bg') >-1 :
    dataType=0
if localpath.find('co') >-1 :
    dataType=1
if localpath.find('cf') >-1 :
    dataType=3
if localpath.find('cs') >-1 :
    dataType=8
if localpath.find('ba') >-1 :
    dataType=9
if localpath.find('ybe') >-1 :
    dataType=12
if localpath.find('sbbe') >-1 :
    dataType=13
if localpath.find('yblank') >-1 :
    dataType=14
if localpath.find('sbblank') >-1 :
    dataType=15


ProdStep = 'RQ'
tree=None
tree=f.Get("rqDir/eventTree") 
if filename.find('calib') >-1 :
    ProdStep = 'RRQ'
    try :
        tree=f.Get("rrqDir/calibevent") 
    except:
        print("Couldn't get metadata")

if localpath.find('cut') >-1 :
    ProdStep = 'Cut'
    try :
        tree=f.Get("cutDir/cutevent") 
    except:
        print("Couldn't get metadata")
        

       

if localpath.find("/Noise/") >-1 or   localpath.find("/noise/") >-1:
    ProdStep = 'Noise'
    exit()


if tree:
    nEvents=tree.GetEntries()
    try:
        firstSeries=str(int(tree.GetMinimum("SeriesNumber")))
        firstSeries=firstSeries[0:7]+'_'+firstSeries[7:11]
        lastSeries=str(int(tree.GetMaximum("SeriesNumber")))
        lastSeries=lastSeries[0:7]+'_'+lastSeries[7:11]
    except:
        print(" Couldn't get series")

 
#create Data Catalog instance (this loads the root config file)                                                                                                                                            
dc=CDMSDataCatalog()
#print(dcpath) 
dataset = []
try:
    dataset = dc.search(relpath+"*", query='name eq "'+filename+'*"' )
except :
    print( "Couldn't find " + dcpath+"/" +filename  ) 
    


dataset = dc.search(relpath)
#print(dataset)
foundFile = False
#if  len( dataset ) > 0 :
for i in dataset:
    if i.datasetName == filename :
        foundFile = True
if  foundFile :
    #print( len( dataset ) )
    #print("Found ", filename , " not registering"  )
    exit()
    #try:
    #    dc.rm( dcpath+"/" +filename  ) 
    #    dc.rm( dcpath ) 
    #except:
    #    print( "Couldn't rm " + dcpath+"/" +filename + " from ", dataset ) 


#dc.rm( dcpath+"/" +filename  ) 
#dc.rm( dcpath ) 

#exit()
#create a CDMS-style dataset. This initializes a minimum set of metadata based on the file type (here this is a DMC file)                                                                                  
ds=CDMSDataset( filename ,
               localpath, 
               fileFormat='root',site='SLAC', dataType=str(dataType)  )
ds.relativePath=relpath
 
ds.metadata['Facility']="Soudan"
ds.metadata['ProdStep']=ProdStep
ds.metadata['nEvAll']=nEvents
ds.metadata['nIsJunk']=0
ds.metadata['Dumps']=0
ds.metadata['nFridgeRun']=fRun
ds.metadata['nDataType']= dataType
ds.metadata['Series']=firstSeries+":"+lastSeries
ds.metadata['nEvBORR'] =    0  
ds.metadata['nEvBORTS'] =   0  
ds.metadata['nEvEORR'] =    0  
ds.metadata['nEvEORTS'] =   0  
ds.metadata['Processing_config'] = wikilink
ds.metadata['Analysis_config'] = wikilink
ds.metadata['ProdVersion'] = prodv
ds.metadata['CommentEnd'] = "Soudan data"
ds.metadata['CommentStart'] = "Soudan data"

if localpath.find('cut') >-1 :
    cutdate=localpath
    if cutdate.find("cuts_HT") >-1:
        cutdate=cutdate[ cutdate.find("cuts_HT")+8 : len(cutdate)]
    else:
        cutdate=cutdate[ cutdate.find("cuts")+5 : len(cutdate)]
    
    cutdate=cutdate[ 0 : cutdate.find("/")   ]
    ds.metadata['CutVersion'] = cutdate


#add to the data catalog                                                                                                                                                                                   
ds.info() 

notadded=True
attempt=1
while notadded:
    print("Attempt #",attempt," for ", localpath)
    attempt+=1
    try:
        dc.add(ds)
        notadded=False
    except FileAlreadyExistsException:
        try:
            dc.rm( dcpath+"/" +filename  ) 
            dc.rm( dcpath ) 
        except:
            print( "Couldn't rm " + dcpath+"/" +filename + " from ", dataset ) 
    
    
    
    
    


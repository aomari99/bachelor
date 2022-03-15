from Entity import Entity
from io import StringIO
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import json
from  model import  BertModels

model = BertModels()
def getBoundsOfChar(bounds):
    return [(bounds[0],bounds[1]),(bounds[0],bounds[3]),(bounds[2],bounds[1]),(bounds[2],bounds[3])]

def getBounds(array):
    Bounds = []
    temppage = array[0][2]
    boundobject = []
    for i in array:
        
        if(i[0] == "\n" and len(boundobject) > 0):
            Bounds.append((boundobject,temppage))
            boundobject = ()
            continue
        bound = getBoundsOfChar(i[1])
        if(temppage != i[2]):
            Bounds.append((boundobject,temppage))
            boundobject = ()
            temppage = i[2]
        
        if len(boundobject) == 0 :
            boundobject = [bound[1],bound[3],bound[0],bound[2]]
        else:
            boundobject = [boundobject[0],bound[3],boundobject[2],bound[2]]
        #print(boundobject)
        
    if(len(boundobject) != 0):
       Bounds.append((boundobject,temppage))
    return Bounds 
def Bounds_ToXFDF(bounds):
    bounds_new = []
    bound = {"coordinates" : "" , "page" : bounds[0][1] }
    for bounderi, page in bounds:
            bound = {"coordinates" : (",".join([str(value) for value in bounderi])).replace("(","").replace(")","").replace(" ", "") , "page" : page }
            bounds_new.append(bound)
    return bounds_new

from timeit import default_timer as timer
def analyse(file):
    start = timer()
    output_string = StringIO()
    output =[]
    EntitysList =[]

    page = 0
    for page_layout in extract_pages(file):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    for character in text_line:
                        if isinstance(character, LTChar):
                            if(len(character._text) == 1):
                                output.append((character._text , character.bbox,page ))
                                output_string.write(output[-1][0])
                            else :
                                for i in character._text:
                                    output.append((i , character.bbox,page ))
                                    output_string.write(output[-1][0]) 
                    output.append(("\n", 0,page ))
                    output_string.write(output[-1][0])
        page = page + 1 
    #print(f"{len(output_string.getvalue())}/{len(output)}")
    
    #print(output_string.getvalue())
    ent , sim = model.analyse(output_string.getvalue())
  
    for i in ent:
        #print(i)
        #print((output[i[6]:][i[0]])[0])
        #print((output[i[6]:][i[0]+len(i[3].rstrip())-1])[0])
        EntitysList.append( Entity( Bounds_ToXFDF(getBounds(output[i[6]:][i[0]:i[1]])), i[2], i[3],i[4],i[5] ).__dict__)
    end = timer()
    return( { "Entitys":  EntitysList , "Sims" : sim  , "calc_time": end - start })
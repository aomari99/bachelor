from collections import Counter
class Entity():
    def __init__(self,bounds,type,word ,  extraktor ,score = None,startend = "",debug = False) -> None:
        self.Bounds = bounds  
        self.Entity = type
        self.word = word
        self.Extractor = extraktor
        #self.page = page
        if(debug):
            self.startend=startend
        if(type == "PERSON"):
            self.attributes = self.groupAttributesPerson(score)
        elif(type == "LOCATION"):
            self.attributes = self.groupAttributesLocation(score)
        else:
            self.attributes = {}
            for i in score:
                self.attributes.update(i)
    def groupAttributesLocation(self,att):
        l = []
        att2 = {}
        for i in att:
           l.extend(  i.keys())
        c = Counter(l)
        for i in c:
            if(c[i] > 1):      
                return {"LOCATION" : self.word}
        for i in att :
                att2.update(i)
        return att2
    def groupAttributesPerson(self,att):
        att2 = {}
        out = []
        for i in att:
            j = list(i.keys())[0]
            if( j in att2):
                att2[j] =  {'word': att2[j]['word']+" "+i[j]['word'], 'score': (att2[j]['score']+i[j]['score']) / 2}
            else:
                att2.update(i)
        for i in att2:
                out.append({i:att2[i]})
        return att2
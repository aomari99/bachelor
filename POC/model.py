import numpy as np
from collections import defaultdict
import numpy as np
from transformers import BertTokenizerFast, pipeline ,BertForTokenClassification
from sentence_transformers import SentenceTransformer, util
import itertools
class BertModels():
    def __init__(self) -> None: 
        #load all models and tokenizer       
        self.tokenizer = BertTokenizerFast.from_pretrained('./models/NEWS_TOK_2')
        self.model = BertForTokenClassification.from_pretrained('./models/NEWS_NER_2/', config = './models/NEWS_NER_2/')
        self.sentence_model = BertForTokenClassification.from_pretrained('./models/NEWS_Sentence_2/', config = './models/NEWS_Sentence_2/')
        self.sim_model = SentenceTransformer("./models/sentence_simalarity")
        self.nlp =  pipeline('ner', model=self.model, ignore_labels=["SENTENCE_END"], tokenizer=self.tokenizer , aggregation_strategy="max")
        #labelsdict={0: 'I-LOCATION', 1: 'I-ORGANIZATION', 2: 'B-LOCATION', 3: 'B-PERSON_FIRSTNAME', 4: 'I-SENTENCE_END', 5: 'I-LOCATION_STREET', 6: 'O', 7: 'B-SENTENCE_END', 8: 'I-PERSON_FIRSTNAME', 9: 'B-ORGANIZATION', 10: 'B-PERSON_AGE', 11: 'B-LOCATION_CITY', 12: 'I-LOCATION_ASSOSIATION', 13: 'I-PERSON_AGE', 14: 'B-LOCATION_STREET', 15: 'B-TELE_NUMMER', 16: 'B-LOCATION_ASSOSIATION', 17: 'B-PERSON_LASTNAME', 18: 'B-LOCATION_COUNTRY', 19: 'I-LOCATION_CITY', 20: 'I-TELE_NUMMER'}
        #self.model.config.id2label = labelsdict
    #get entities for entity sim and for returning the entities 
    def getEntites(self,string):
        output = []
        out2 = []  
        for start,i in self.getStringPackages(string,self.model):
                doc = (self.nlp(i))
                gr = self.groupEntities(doc,i,start)
                for ent in gr:
                        out2.append((ent["start"],ent["end"], ent["entity_group"],ent["word"],"ML_BERT",ent["attributes"],start))
                output.extend(gr)
        return output , out2

    #meausre tokensize of string 
    def IsTokenToBig(self,string):
        ids = self.tokenizer(string,  max_length= 512 , truncation=True)["input_ids"]
        if(np.count_nonzero(ids) < 512 ):
            return False
        string0 = self.tokenizer.convert_tokens_to_string(self.tokenizer.convert_ids_to_tokens(ids)[1:-1])
        if(len(string0) < len(string)):
            return True
        return False
    #split string into packages for the Model cause tokensize must be <= 512
    def getStringPackages(self,string,model):
        strings=[]
        temp_string = string
        start = 0
        while(self.IsTokenToBig(temp_string)):
            nlp = pipeline("ner",ignore_labels=["LOCATION","ORGANIZATION","PERSON_FIRSTNAME","LOCATION_STREET","O","PERSON_AGE","LOCATION_CITY","LOCATION_ASSOSIATION","TELE_NUMMER","PERSON_LASTNAME","LOCATION_COUNTRY"], model= model, tokenizer=self.tokenizer, aggregation_strategy ="max" )
            doc = nlp(temp_string)
            #print(temp_string)
            #print(doc)
            strings.append((start,temp_string[:doc[-1]["end"]]))
            start = doc[-1]["end"]
            temp_string = temp_string[doc[-1]["end"]:]
           # print(self.IsTokenToBig(temp_string))
        strings.append((start,temp_string))
        return strings


    #groups sub entities to main Entity
    def groupEntities(self,data, string,startpoint):
        entities = []
        ent = {"entity_group": "", "start":0, "end" :0 , "word": "" , "attributes" : [] }
        attributes = {}
        for i in data:
            #print(i)
            attributes.clear()
            if ent["entity_group"] == "":
                if i["entity_group"] in ["O","PERSON_AGE"]:
                    continue
                else:
                    ent["start"]= startpoint +i["start"]
                    ent["end"]=startpoint + i["end"]
                    ent["word"]=string[ent["start"]:ent["end"]]
                    splitt = i["entity_group"].split("_")
                    ent["entity_group"]=splitt[0]
                    attributes[splitt[-1]] ={ "word":i["word"],"score": float(i["score"]) }
                    ent["attributes"].append(attributes.copy())
            else:
                splitt = i["entity_group"].split("_")
                if splitt[0] == "O":
                    #check if a (, ) or "" than contiue else add it to entities and clear ent and create an empty
                    if i["word"] in ["." , "(", ")","„","“"]:
                        continue
                    else :
                        entities.append(ent.copy())
                        ent.clear()
                        ent = {"entity_group": "", "start":0, "end" :0 , "word": "" , "attributes" : [] }
                elif splitt[0] == ent["entity_group"]:
                        if((i["entity_group"].split("_")[0] == ent["entity_group"])):
                                            ent["end"]=startpoint +i["end"]
                                            ent["word"]=string[ent["start"]:ent["end"]]
                                            splitt = i["entity_group"].split("_")
                                            ent["entity_group"]=splitt[0]
                                            attributes[splitt[-1]] ={ "word":i["word"],"score": float(i["score"]) }
                                            ent["attributes"].append(attributes.copy())
                        else:
                            entities.append(ent.copy())
                            ent.clear()
                            ent = {"entity_group": "", "start":0, "end" :0 , "word": "" , "attributes" : [] }
                else :
                        entities.append(ent.copy())
                        ent.clear()
                        ent = {"entity_group": "", "start":0, "end" :0 , "word": "" , "attributes" : [] }
                    #add new attribute if its Person firt and than last  or the last or this one is a Assosiation opereator or the i is an Age and before was a person if Person first first than check simmaliary and isnt the same 
        return entities
    
    #removes duplicates from sentece pairs
    def removeDuplicates(self,lst):
        temp = [tuple(sorted(sub)) for sub in lst]
        return list(set(temp))

    #get sentence formatted for the  sim_ent model
    def get_Sentence(self,ent,sentecs,string):
        for i in sentecs:
            #print(i)
            #print(ent)
            if(ent["start"] >= i["start"] and ent["end"] <= i["end"]):
                data = string
                data = data[ 0:ent["end"] ] + "</Entity>" + data[ent["end"] : ]
                data = data[ 0:ent["start"]] + "<Entity>" + data[ent["start"] : ]
                return data[i["start"]:i["end"]+17]
        return "" 


    # get senteces of text
    def predict_sentences(self,data,ignore=["O","SENTENCE_END"]):
            ent = []
            nlp = pipeline("ner",ignore_labels=ignore, model=self.sentence_model, tokenizer=self.tokenizer, aggregation_strategy ="max" )
            html_strings = []
            for start,i in self.getStringPackages(data,self.sentence_model):
                for j in (nlp(i) ):
                    j["start"] = start+ j["start"]
                    j["end"] = start+ j["end"]
                    ent.append(j)
            return ent
    #calculate sim
    def get_sim(self,s1,s2):
        embeddings1 = self.sim_model.encode(s1, convert_to_tensor=True)
        embeddings2 = self.sim_model.encode(s2, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(embeddings1, embeddings2)
        #print(cosine_scores)
        return float(cosine_scores[0])

    #IE
    def analyse(self,string):
        train_sentences = []
        clean_sentences = []
        sims = []
        sentences = self.predict_sentences(string)
        doc,doc2 = self.getEntites(string)
       
        id = 0
        for j in doc:
            sent=   self.get_Sentence(j , sentences,string)
            if(sent == ""):
                id +=1
                continue
            train_sentences.append(( j["entity_group"],  sent , id))
            id +=1
        for i, j in itertools.product(train_sentences, train_sentences):
            if(i[0] != j[0] or i[1] == j[1]):
                continue
            clean_sentences.append((i[1],j[1],i[2],j[2]))

        for s1,s2,e1,e2 in  clean_sentences:
            score = self.get_sim(s1,s2)
            sims.append({ "Entity1" : e1,"Entity2" :e2 , "score" :score})

        return doc2,sims
from jpype import *
import jpype.imports
import base64

jar2 = "./pdfbox-app-3.0.0-alpha2.jar"
jar1 = "./test.jar"
args = f"-Djava.class.path={jar1};{jar2}" 

jvm_path = jpype.getDefaultJVMPath()
jpype.startJVM(jvm_path, "-ea", args)


from java.io import File;
from pdf.python import Parser


def parse(file):

    Parser.parseB64(base64.b64encode(file))
     
    return Parser.Text , Parser.Elements
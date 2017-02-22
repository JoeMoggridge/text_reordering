import sys
import os
import re
import fileinput

def get_file():
	myfile = open("Logging.Failure.txt", "r+")
	return myfile

def process_line (inputline) :

#(((?#optionalerrorcode)\\+(.+))*)(.*)
#'Logging\\.Failure\\(((?#errortext).+)(.*)\\+((?#txt).+)\\+((?#value).+)\\+((?#txt).+)\\+((?#value).+)\\);'
    MyRegex1 = re.compile('Logging\\.Failure\\((.{5,50}?)(\\+(.{5,20}))?\\+(.{5,50}?)\\+(.{5,20}?)\\+(.{5,50}?)\\+(.{5,20})?\\+(.{5,20})?\\);')
    searchforstart = re.compile('Logging\\.Failure\\((.{5,50})?\\+')
    searchforexpected = re.compile('\\+(.{0,2})(Expected (Value|value|.))(.{0,2})\\+(?P<expectedvariable>.+)\\+')
    searchforactual = re.compile  ('\\+(.{0,2})(Actual (Value|value|.))(.{0,2})\\+(?P<actualvariable>.+)\\+')

    matchedline = re.search(MyRegex1, inputline)
    if(not matchedline):
        return "line does not match"

    m_startbit = re.search(searchforstart, matchedline.group())

    if m_startbit :

        m_expected = re.search(searchforexpected, matchedline.group())
        if m_expected :
            s_expected = m_expected.group('expectedvariable')

            m_actual = re.search(searchforactual, matchedline.group())
            if m_actual :
                s_actual = m_actual.group('actualvariable')

                outputline = m_startbit.group() + " , " + s_expected + " , " + s_actual + "  );"

                return outputline

    return "line processing failed"

def stringify (inputline):
    #adds .ToString() to variables, if required
    MyRegEx2 = re.compile('Logging\\.Failure\\((?P<msgError>.+)(.*)((\\+(?P<valError>.+))*)(.*),(?P<valExpected>.+),(?P<valActual>.+)\\);')

    MyResult = re.search(MyRegEx2, inputline)

    if MyResult:

        matchedexpected = MyResult.group('valExpected')
        matchedactual = MyResult.group('valActual')

        #if either of the matched arguments do not start with "str", then add the ".ToString()" method on the end.

        if not re.match('str', matchedexpected):
            matchedexpected.strip()
            matchedexpected = matchedexpected+".ToString()"

        if not re.match('str', matchedactual):
            matchedactual.strip()
            matchedactual = matchedactual+".ToString()"

        return "Logging.Failure(" + MyResult.group('msgError')+ " + " +MyResult.group('msgError') + \
                                                                " , " + matchedexpected + " , " + matchedactual + ");"

    else:
        return "no match on this line"

# main
#==============

#with open("Logging.Failure.txt", "r+") as MyFile:


    #print ("---> Input file succesfully opened.\n")
i=0
    #pos= MyFile.seek(0)

for line in fileinput.input("logging.failure.txt", inplace=1):
    #for line in MyFile :
     i += 1

        # pos= MyFile.tell()
         #print (pos)

     if i > 1 :

        #1) process line
        result = process_line(line)

        if result == "line processing failed" :
            sys.stdout.write("for line " +str(i)+ ", processing failed!")
            #print("for line " +str(i)+ ", processing failed!")

        elif result == "line does not match" :
            print("line " + str(i) + ": does not match")

        else:
            line = result
            print("line " + str(i) + " overwriting with: "+ result)

        #2) stringify
        result= stringify(line)
        if result== "no match on this line":
            print("stringify: line " + str(i) + ": does not match ")
        else:
            #print(result, file=MyFile, flush=True)
            line=result
            print("stringify: line " + str(i) + " overwriting with: " + result)

    #cleanup
     #MyFile.close()
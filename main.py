import sys
import os
import re


def get_file():
	myfile = open("Logging.Failure.txt", "r+")
	return myfile

def process_line (inputline) :

#(((?#optionalerrorcode)\\+(.+))*)(.*)
#'Logging\\.Failure\\(((?#errortext).+)(.*)\\+((?#txt).+)\\+((?#value).+)\\+((?#txt).+)\\+((?#value).+)\\);'
    MyRegex1 = re.compile('Logging\\.Failure\\((.{5,100}?)(\\+(.{5,30}))?\\+(.{5,50}?)\\+(.{5,30}?)\\+(.{5,50}?)\\+(.{5,30})?\\+(.{3,20})?\\);')
    searchforstart = re.compile('Logging\\.Failure\\((.{5,50})?\\+')
    searchforexpected = re.compile('\\+(.{1,5})((E|e)xpected (((V|v)alue)|(.{2,10})))(.{1,5})\\+(?P<expectedvariable>.{5,20})(\\+|\\))')
    searchforactual = re.compile  ('\\+(.{1,5})((A|a)ctual (((V|v)alue)|(.{2,10})))(.{1,5})\\+(?P<actualvariable>.{5,20})(\\+|\\))')

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
    MyRegEx2 = re.compile('Logging\\.Failure\\((?P<msgError>.{5,100})?(.{1,5})((\\+(?P<valError>.{5,50}))*)(.{1,5}),(?P<valExpected>.{5,30})?,(?P<valActual>.{5,30})?\\);')

    MyResult = re.search(MyRegEx2, inputline)

    if MyResult:

        s_matchedexpected = MyResult.group('valExpected')
        s_matchedactual = MyResult.group('valActual')

        #if either of the matched arguments do not start with "str", then add the ".ToString()" method on the endof both
        s_matchedexpected = s_matchedexpected.strip()
        s_matchedactual = s_matchedactual.strip()
        if (not re.match('str', s_matchedexpected)) or (not re.match('str', s_matchedactual)):
            s_matchedexpected = s_matchedexpected.strip()
            s_matchedexpected = s_matchedexpected+".ToString()"
            s_matchedactual = s_matchedactual.strip()
            s_matchedactual = s_matchedactual+".ToString()"

        return "Logging.Failure(" + MyResult.group('msgError') +" , " + s_matchedexpected + " , " + s_matchedactual + ");"

    else:
        return "no match on this line"

# main
#==============

#firstly, reorder the arguments
with open("Logging.Failure.txt", "r") as InFile:
    with open("Logging.Failure_tmp.txt", "w") as OutFile:

        print("---> Input file succesfully opened.\n")
        line_num =0
        #pos= MyFile.seek(0)

        for line in InFile:

             line_num += 1

            # pos= MyFile.tell()
            #print (pos)

             if line_num > 0 :

                #1) process line
                result = process_line(line)

                if result == "line processing failed" :
                    print("for line " +str(line_num)+ ", processing failed!")
                    OutFile.write(line)


                elif result == "line does not match" :
                    print("line " + str(line_num) + ": does not match")
                    OutFile.write(line)

                else:
                    print("line " + str(line_num) + " overwriting with: "+ result)
                    OutFile.write(result+"\n")

    OutFile.close()
InFile.close()

# next, add .Tostring(), if required
with open("Logging.Failure_tmp.txt", "r") as InFile:
    with open("Logging.Failure_out.txt", "w") as OutFile:

        line_num = 0

        for stringy_ln in InFile:

            line_num += 1

            #2) stringify
            result= stringify(stringy_ln)
            if result== "no match on this line":
                print("stringify: line " + str(line_num) + ": does not match ")
                OutFile.write(stringy_ln)
            else:
                #print(result, file=MyFile, flush=True)
                OutFile.write(result+"\n")
                print("stringify: line " + str(line_num) + " overwriting with: " + result)

    #cleanup
    OutFile.close()
InFile.close()
os.remove("Logging.Failure_tmp.txt")
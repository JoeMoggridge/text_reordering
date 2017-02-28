import sys
import os
import re


def process_line (inputline) :

#(((?#optionalerrorcode)\\+(.+))*)(.*)
#'Logging\\.Failure\\(((?#errortext).+)(.*)\\+((?#txt).+)\\+((?#value).+)\\+((?#txt).+)\\+((?#value).+)\\);'
    MyRegex1 = re.compile('(.*?)Logging\\.Failure\\((.{5,150}?)(\\+(.{5,50}))?\\+(.{5,50}?)\\+(.{5,50}?)\\+(.{5,50}?)\\+(.{5,50}?)\\+(.{3,50}?)\\);')
    searchforstart = re.compile('(.*?)Logging\\.Failure\\((?P<msgError>.{5,150}?)\\+((?P<valError>.{5,50}?)|(.+?))(?=\\+)')
    searchforexpected = re.compile('\\+(.{1,10})((E|e)xpected (((V|v)alue)|(.{2,10})))(.{1,10})\\+(?P<expectedvariable>.{3,50}?)(\\+|\\))')
    searchforactual = re.compile  ('\\+(.{1,10})((A|a)ctual (((V|v)alue)|(.{2,10})))(.{1,10})\\+(?P<actualvariable>.{3,50}?)(\\+|\\))')

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

                #if the error mesage contains a value the we need to add a quote. if not then we need to not add a quote
                if m_startbit.group('valError')!= None:
                    outputline = m_startbit.group() + "+ \" \'"+" \", " + s_expected + " , " + s_actual + "  );"
                else:
                    outputline = m_startbit.group() + " , " + s_expected + " , " + s_actual + "  );"

                return outputline

    return "line processing failed"

def stringify (inputline):
    #adds .ToString() to variables, if required
    MyRegEx2 = re.compile('(?P<Whitespace>.*?)Logging\\.Failure\\((?P<msgError>.{5,100})?,(?P<valExpected>.{5,30})?,(?P<valActual>.{5,30})?\\);')

    MyResult = re.search(MyRegEx2, inputline)

    if MyResult:

        s_matchedexpected = MyResult.group('valExpected')
        s_matchedactual = MyResult.group('valActual')
        s_whitespace = MyResult.group('Whitespace')

        # first remove whitespace
        s_matchedexpected = s_matchedexpected.strip()
        s_matchedactual = s_matchedactual.strip()

        #if either of the matched arguments do not start with "str", then add the ".ToString()" method on the endof both
        if (not re.match('str', s_matchedexpected)) or (not re.match('str', s_matchedactual)):
            #if either of the matched arguments do not start with 'int' then we really are going to have to add '.ToString()' to the end.
            if (not re.match('int', s_matchedexpected)) or (not re.match('int', s_matchedactual)):
                s_matchedexpected = s_matchedexpected+".ToString()"
                s_matchedactual = s_matchedactual+".ToString()"

        return s_whitespace+ "Logging.Failure(" + MyResult.group('msgError') +" , " + s_matchedexpected + " , " + s_matchedactual + ");"

    #else
    return "no match on this line"

# main
#==============

#firstly, reorder the arguments

with open("input.txt", "r") as InFile:
    with open("TextReordering_tmp.txt", "w") as OutFile:

        print("---> Input file succesfully opened.\n")
        line_num =0
        doesnotmatchflag = False
        linecounter = 0

        for line in InFile:

             line_num += 1


             if line_num > 0 :

                #1) process line
                result = process_line(line)

                if result == "line processing failed" :
                    # first deal with previous lines whichmight be duplicates
                    if linecounter > 0:
                        print( "Re-order: ... " + str(linecounter) + "lines did not match the pattern")
                        linecounter=0
                    #next, log the current message:
                    print("Reorder: for line " +str(line_num)+ ", processing failed!")
                    OutFile.write(line)


                elif result == "line does not match" :
                    OutFile.write(line)

                    if linecounter == 0: #this line is not a duplicate, log it
                        print("Re-order: line " + str(line_num) + ": does not match")

                    # this is a duplicate, dont log it
                    linecounter += 1



                else:
                    #first deal with previous lines whichmight be duplicates
                    if linecounter > 0:
                        print( "Re-order: ...  " + str(linecounter) + " lines did not match")
                        linecounter=0
                    # next, log the current message:
                    print("Re-order: line " + str(line_num) + " overwriting with: "+ result)
                    OutFile.write(result+"\n")

    OutFile.close()
InFile.close()

# next, add .Tostring(), if required
with open("TextReordering_tmp.txt", "r") as InFile:
    with open("output.txt", "w") as OutFile:

        line_num = 0

        for stringy_ln in InFile:

            line_num += 1

            #2) stringify
            result= stringify(stringy_ln)

            if result== "no match on this line":
                OutFile.write(stringy_ln)

                if linecounter == 0:  # this line is not a duplicate, log it
                    print("stringify: line " + str(line_num) + ": does not match ")

                # this is a duplicate, dont log it
                linecounter += 1

            else:
                # first deal with previous lines whichmight be duplicates
                if linecounter > 0:
                    print("stringify: ... " + str(linecounter) + " lines did not match")
                    linecounter = 0

                # next, log the current message:
                OutFile.write(result+"\n")
                print("stringify: line " + str(line_num) + " overwriting with: " + result)

    #cleanup
    OutFile.close()
InFile.close()
os.remove("TextReordering_tmp.txt")
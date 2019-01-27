#!/usr/bin/python
'''
Created on Mar 30, 2012

FecthFunds, kopierar av aktuell fondkurser
@author: edo
'''

import httplib2
import sys
import sqlite3
import os.path

global DBfile
DBfile = "./fund_stats.sqlite"
global varMainLimit
varMainLimit = "-20"

# Format (["Name of Fund", "Current Andelar", "Anskaffningsvarde for Andelar", "Url at pensionsmyndigheten"])
fundList = (['AlfredBerg Fastighetsfond', '146.05', '15678', 'https://secure.pensionsmyndigheten.se/FondfaktasidaPopup.html?id=320176'],
            ['EastCapital Ryssland', '0.56', '612', 'https://secure.pensionsmyndigheten.se/FondfaktasidaPopup.html?id=834788'],
            ['HandelsBanken Sverige OMXSB', '252.63', '27167', 'https://secure.pensionsmyndigheten.se/FondfaktasidaPopup.html?id=465914'])

# Mail address to send to
mail_address = "xxxxxx@xxxxxxx"

# Mail configuaration
mailServer = "xxx"
fromAddress = "xxx"

varFunds = []
for fund in fundList:
    varFunds.append(fund[0])


def FetchSkandia(varName, varAndelar, varAnskaf, varUrl):
   '''
   Return Name, Kurs, Varde, Diff
   '''

   objHttp = httplib2.Http(disable_ssl_certificate_validation=True)
   varResp, varBody = objHttp.request(varUrl, "GET")

   varBody = varBody.split('\n')

   varCheckNextLine = False

   for line in varBody:

         if varCheckNextLine is True:
            varFundsKurs = line
            varFundsKurs = varFundsKurs.split('<span>')
            varFundsKurs = varFundsKurs[1].split('&')
            varFundsKurs = varFundsKurs[0]
            varCheckNextLine = False

         if not line.find('Fondkurs') == -1:
            varCheckNextLine = True

   varValue = float(varAndelar.replace(",", ".")) * float(varFundsKurs.replace(",", "."))

   if varValue < float(varAnskaf):
      varDiff = ((float(varValue) / float(varAnskaf)) - 1) * 100
   else:
      varDiff = 100 - (float(varAnskaf) / float(varValue) * 100)

   return varName, varFundsKurs, "%.2f" % varValue, "%.2f" % varDiff

#################################################################################


def CreateDB():

   connection = sqlite3.connect(DBfile)
   cursor = connection.cursor()

   def CreateTable(name, idcolumn, columndef):
      try:
         SQL="CREATE TABLE " + name + "(" + idcolumn + " " + columndef + ")"
         cursor.execute(SQL)
      except Exception as value:
         print (str(value))

   def CreateColumn(name, columnname, columndef):
      try:
         SQL="ALTER TABLE " + name + " ADD COLUMN " + columnname + " " + columndef
         cursor.execute(SQL)
      except Exception as value:
         print (str(value))

   CreateTable('tblFunds','id','INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL')
   CreateColumn('tblFunds','colDate','TEXT')
   CreateColumn('tblFunds','colName','TEXT')
   CreateColumn('tblFunds','colKurs','TEXT')
   CreateColumn('tblFunds','colVarde','TEXT')
   CreateColumn('tblFunds','colDiff','TEXT')

   CreateTable('tblDiff','id','INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL')
   CreateColumn('tblDiff','colDate','TEXT')
   CreateColumn('tblDiff','colTotalValue','TEXT')
   CreateColumn('tblDiff','colTotalDiff','TEXT')



########################################################################################################


def AddDBValues(varName, varFundsKurs, varValue, varDiff):

   import datetime

   now = datetime.datetime.now()
   colDate = now.strftime("%Y-%m-%d")

   connection = sqlite3.connect(DBfile)
   cursor = connection.cursor()

   cursor.execute("""INSERT INTO tblFunds (colDate, ColName, ColKurs, ColVarde, ColDiff) VALUES (?,?,?,?,?)""", (colDate, varName, varFundsKurs, varValue, varDiff))

   print ("Adding data - " + colDate + ", " + varName + ", "  + str(varFundsKurs) + ", " + str(varValue) + ", " + str(varDiff))

   connection.commit()
   connection.close()

#####################################################################################################

def AddDBDiff(varTotal, varDiff):

   import datetime

   now = datetime.datetime.now()
   colDate = now.strftime("%Y-%m-%d")

   connection = sqlite3.connect(DBfile)
   cursor = connection.cursor()

   cursor.execute("""INSERT INTO tblDiff (colDate, colTotalValue, colTotalDiff) VALUES (?,?,?)""", (colDate, varTotal, varDiff))

   print ("Adding data - " + colDate + ", " + str(varTotal) + ", " + str(varDiff))

   connection.commit()
   connection.close()


#####################################################################################################

def GetDiffStat():
   # Returning Dates, Value of ALL funds together, and Difference Up or Down

   connection = sqlite3.connect(DBfile)
   cursor = connection.cursor()

   # Get all Values (Diff)
   cursor.execute("""Select colTotalDiff from tblDiff;""")
   row = cursor.fetchall()

   # Inserts Tuple (of all values) into first element of List
   varAllList = []
   varDiffTuples = tuple(float(item[0]) for item in row)
   varAllList.append(varDiffTuples)

   #Get All Dates
   cursor.execute("""Select colDate from tblDiff;""")
   row = cursor.fetchall()

   # Inserts Tuple (of all values) into first element of List
   varDatesList = []
   varDatesTuples = tuple(str(item[0]) for item in row)
   # varDatesList.append(varDatesTuples)

   # Get all Values (TotalValues)
   cursor.execute("""Select colTotalValue from tblDiff;""")
   row = cursor.fetchall()

   # Inserts Tuple (of all values) with spacing of 0.5
   varValuesList = []

   for i, item in enumerate(row):
      Dates = (float(i)+0.5, float(item[0]))
      varValuesList.append(Dates)

   connection.commit()
   connection.close()

   return varDatesTuples, varAllList, varValuesList

#####################################################################################################

def GetAllFunds(argFunds):
   # Returning Dates, Value of ALL funds together, and Difference Up or Down

   connection = sqlite3.connect(DBfile)
   cursor = connection.cursor()

   # Inserts Tuple (of all values) into first element of List
   varAllList = []


   for i in argFunds:
      # Get all Values from this fund
      cursor.execute("""Select colDiff from tblFunds where colName=?;""", (str(i),))
      row = cursor.fetchall()

      varFundsTuples = tuple(float(item[0].replace(",",".")) for item in row)
      varAllList.append(varFundsTuples)


   connection.commit()
   connection.close()

   return varAllList


#####################################################################################################

def SendMail(varMailAddress, smtpServer, fromAddress):
   import sys, smtplib, MimeWriter, base64, StringIO

   message = StringIO.StringIO()
   writer = MimeWriter.MimeWriter(message)
   writer.addheader('Subject', 'Fond-Statistik')
   writer.startmultipartbody('mixed')

   # start off with a text/plain part
   part = writer.nextpart()
   body = part.startbody('text/plain')
   body.write('Here comes the statistics')

   # now add an image part
   part = writer.nextpart()
   part.addheader('Content-Transfer-Encoding', 'base64')
   body = part.startbody('image/png')
   base64.encode(open('/tmp/graph.png', 'rb'), body)

   # finish off
   writer.lastpart()

   # send the mail
   smtp = smtplib.SMTP(smtpServer)
   smtp.sendmail(fromAddress, varMailAddress, message.getvalue())
   smtp.quit()

#####################################################################################################

def SendMailNew(varMailAddress, mailServer, fromAddress):
   # Send an HTML email with an embedded image and a plain text message for
   # email clients that don't want to display the HTML.

   from email.MIMEMultipart import MIMEMultipart
   from email.MIMEText import MIMEText
   from email.MIMEImage import MIMEImage

   # Define these once; use them twice!
   strFrom = fromAddress
   strTo = varMailAddress

   # Create the root message and fill in the from, to, and subject headers
   msgRoot = MIMEMultipart('related')
   msgRoot['Subject'] = 'Fond Statistik'
   msgRoot['From'] = strFrom
   msgRoot['To'] = strTo
   msgRoot.preamble = 'This is a multi-part message in MIME format.'

   # Encapsulate the plain and HTML versions of the message body in an
   # 'alternative' part, so message agents can decide which they want to display.
   msgAlternative = MIMEMultipart('alternative')
   msgRoot.attach(msgAlternative)

   msgText = MIMEText('Your mail-client doesnt support HTML')
   msgAlternative.attach(msgText)

   # We reference the image in the IMG SRC attribute by the ID we give it below
   msgText = MIMEText('<b>Funds Statistic</b><br><br>Summary<br><img src="cid:image1"><br>All Funds<br><img src="cid:image2"><br>End!', 'html')
   msgAlternative.attach(msgText)

   # Attach Graph
   fp = open('/tmp/graph.png', 'rb')
   msgImage = MIMEImage(fp.read())
   fp.close()

   # Define the image's ID as referenced above
   msgImage.add_header('Content-ID', '<image1>')
   msgRoot.attach(msgImage)

   # Attach Graph2
   fp = open('/tmp/graph2.png', 'rb')
   msgImage = MIMEImage(fp.read())
   fp.close()

   # Define the image's ID as referenced above
   msgImage.add_header('Content-ID', '<image2>')
   msgRoot.attach(msgImage)

   # Send the email (this example assumes SMTP authentication is required)
   import smtplib
   smtp = smtplib.SMTP()
   smtp.connect(mailServer)
   smtp.sendmail(strFrom, strTo, msgRoot.as_string())
   smtp.quit()



#####################################################################################################

def GenChart(argDates, argDiffs, argValues, argType=1):
# If argType=1 - create chart with diff-value (up/down) and argValue=value
# If argType=2 - create chart with all argDiffs, argValues correspond to names o funds

   # METHOD 1 - Creating Chart
   from reportlab.graphics.shapes import Drawing
   from reportlab.graphics.charts.barcharts import VerticalBarChart
   from reportlab.graphics.charts.linecharts import HorizontalLineChart
   from reportlab.graphics.charts.lineplots import LinePlot

   from reportlab.graphics.shapes import Drawing,colors
   from reportlab.graphics.widgets.markers import makeMarker

   from reportlab.graphics.charts.axes import XCategoryAxis,XValueAxis,YValueAxis
   from reportlab.graphics.charts.textlabels import Label
   from reportlab.graphics.charts.legends import Legend

   # Method 2 - Creating Chart
   #import cairo
   #width, height = (500, 400)
   #surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
   #dataSet = (
   #('dataSet 1', ((0, 1), (1, 3), (2, 2.5))),
   #('dataSet 2', ((0, 2), (1, 4), (2, 3))),
   #('dataSet 3', ((0, 5), (1, 1), (2, 0.5))),
   #)
   #options = {
   #  'legend': {'hide': True},
   #  'background': {'color': '#f0f0f0'},
   #}
   #import pycha.bar
   #chart = pycha.bar.VerticalBarChart(surface, options)
   #chart.addDataset(dataSet)
   #chart.render()
   #surface.write_to_png('output.png')

   if argType == 1:

      # Get DATA for Charts

      d=Drawing(800,500)

      lab = Label()
      lab.setOrigin(100,500)
      lab.boxAnchor = 'ne'
      lab.dx = 0
      lab.dy = -20
      lab.boxStrokeColor = colors.black
      lab.fontName = 'Times-Bold'
      lab.setText('Fondkurs')


      # Adding X-axis labels
      #data = [(10, 20, 30, 40), (15, 22, 37, 42)]
      #xAxis = XCategoryAxis()
      #xAxis.setPosition(75, 75, 300)
      #xAxis.configure(data)
      #xAxis.categoryNames = ['Beer', 'Wine', 'Meat', 'Cannelloni']
      #xAxis.labels.boxAnchor = 'n'
      #xAxis.labels[3].dy = -15
      #xAxis.labels[3].angle = 30
      #xAxis.labels[3].fontName = 'Times-Bold'

      # Chart A - Stapeldiagram
      charta=VerticalBarChart()
      # Test: charta.data=[(-74.18, -74.18, -74.18)]
      charta.data=argDiffs

      charta.width=700
      charta.height=360
      charta.x=20
      charta.y=60
      charta.barWidth=5
      charta.categoryAxis.labels.angle = 270
      charta.valueAxis.valueMax = -100
      charta.valueAxis.valueMax = 20

      # Adding names on horizontal Axis
      # Test: catNames = ('Jan', 'Feb')
      catNames = argDates
      charta.categoryAxis.categoryNames = catNames
      charta.categoryAxis.labels.boxAnchor = 'n'
      charta.categoryAxis.labels.dy = -30

      # Chart B - Linjediagram
      # chartb=HorizontalLineChart()
      chartb=LinePlot()

      # chartb.data=[[(0.5,27000),(1.5,23000),(2.5,22000),(3.5,30000),(4.5,40000)]]
      chartb.data=[argValues]

      chartb.width=charta.width
      chartb.height=charta.height
      chartb.x=charta.x
      chartb.y=chartb.y
      chartb.lines[0].strokeColor = colors.blue
      chartb.lines[0].strokeWidth = 2

      chartb.lines[0].symbol = makeMarker('Circle')
      chartb.lineLabelFormat = '%2.0f'


      # For adding Secondary Axis
      chartb.xValueAxis.valueMin = 0
      noOfBars=len(argValues)
      chartb.xValueAxis.valueMax = noOfBars
      chartb.yValueAxis.valueMin = 0
      chartb.yValueAxis.valueMax = 100000
      chartb.xValueAxis.visible=False
      chartb.yValueAxis.visible=False #Hide 2nd plot its Yaxis

      y2Axis = YValueAxis() #Replicate 2nd plot Yaxis in the right
      y2Axis.setProperties(chartb.yValueAxis.getProperties())
      y2Axis.setPosition(charta.x+charta.width,charta.y,charta.height)
      y2Axis.tickRight=5
      y2Axis.tickLeft=0
      y2Axis.labels.dx = 50 #Make labels to the right
      y2Axis.configure(chartb.data)
      y2Axis.visible=True


      swatches = Legend()
      swatches.alignment = 'right'
      swatches.x = 40
      swatches.y = 460
      swatches.deltax = 60
      swatches.dxTextSpace = 10
      swatches.columnMaximum = 4
      items = [(colors.red, '% Avkastning'), (colors.blue, 'Varde')]
      swatches.colorNamePairs = items


      d.add(lab)
      d.add(charta)
      d.add(chartb)
      d.add(y2Axis)
      d.add(swatches, 'legend')

      d.save(fnRoot='/tmp/graph', formats=['png'])

   # Second Type of Chart with all Funds with several lines
   if argType == 2:

      # Get DATA for Charts

      d=Drawing(800,500)

      lab = Label()
      lab.setOrigin(100,500)
      lab.boxAnchor = 'ne'
      lab.dx = 0
      lab.dy = -20
      lab.boxStrokeColor = colors.black
      lab.fontName = 'Times-Bold'
      lab.setText('Alla Fonder')


      # Chart Fund - Linjediagram
      chartFund=LinePlot()

      # Count number of Funds fed
      varNumFunds=len(argDiffs)
      varNumDates=len(argDates)

      # Create a List of colors
      varColors=[colors.blue, colors.red, colors.orange, colors.black]

      varDataList=[]

      # Loop through the number of Funds (one line each) creating color
      for a in range(varNumFunds):
         # Add Color to each Fund
         chartFund.lines[a].strokeColor = varColors[a]
         chartFund.lines[a].strokeWidth = 2
         chartFund.lines[a].symbol = makeMarker('Circle')

         # Create loop of tuples(0.5,value) and uncreasing from varDiffs inside a List
         varDataTuple=list((float(i)+1.5, argDiffs[a][i]) for i in range(0, varNumDates))
         varDataList.append(varDataTuple)


      # Example
      #chartFund.data=[[(1.5,320),(2.5,150),(3.5,200)],[(1.5,50),(2.5,20),(3.5,80)]]
      chartFund.data=varDataList

      chartFund.width=700
      chartFund.height=300
      chartFund.x=20
      chartFund.y=60
      chartFund.lineLabelFormat = '%2.0f'



      # Add X-values (dates)
      # chartFund.xValueAxis.valueSteps = [1.5, 2.5, 3.5]
      # Make for loop creating List of [1.5 and increasing]
      chartFund.xValueAxis.valueSteps = [float(i)+1.5 for i in range(varNumDates)]
      chartFund.xValueAxis.labelTextFormat = varDates


      swatches = Legend()
      swatches.alignment = 'right'
      swatches.x = 40
      swatches.y = 460
      swatches.deltax = 60
      swatches.dxTextSpace = 10
      swatches.columnMaximum = 4

      # items = [(colors.red, '% Avkastning'), (colors.blue, 'Varde')]
      # Make foor loop getting colors and Names of Funds (argValues)
      items = [(varColors[i], argValues[i]) for i in range(varNumFunds)]

      swatches.colorNamePairs = items


      d.add(lab)
      d.add(chartFund)
      d.add(swatches, 'legend')

      d.save(fnRoot='/tmp/graph2', formats=['png'])


#####################################################################################################



# Main Software
if not os.path.isfile(DBfile):
   print("Creating DB")
   CreateDB()

# Fetch and add HTML values to DB
for fund in fundList:
    fundResult = FetchSkandia(fund[0], fund[1], fund[2], fund[3])
    AddDBValues(fundResult[0], fundResult[1], fundResult[2], fundResult[3])

# Get Diff (up or down in %), and KRONOR
varMainDiff = float(0)
varMainValue = float(0)
for fund in fundList:
    fundResult = FetchSkandia(fund[0], fund[1], fund[2], fund[3])
    varMainDiff += float(fundResult[3])
    varMainValue += float(fundResult[2])

# Add and logs the difference
AddDBDiff(varMainValue, varMainDiff)

# Get details from DB to generate Chart
varDates, varDiffs, varValues = GetDiffStat()

#Generate chart and put in /tmp/graph.png
GenChart(varDates, varDiffs, varValues, 1)

# Return values for each Fund
varFundValues=GetAllFunds(varFunds)
# Generate chart and put in /tmp/graph2.png
GenChart(varDates, varFundValues, varFunds, 2)

# E-mail graph
SendMailNew(mail_address, mailServer, fromAddress)

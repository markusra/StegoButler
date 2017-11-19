# Imports
import subprocess
import timeit
import xlwt
from xlrd import open_workbook
from xlutils.copy import copy
import os
from progressbar import *

# Globals
messageFolder       = "messageFiles/"
messageFiles        = ["text1.txt"]

coverFolder         = "images/"
coverFileSizes      = ["", "@0,8x", "@0,6x", "@0,4x", "@0,2x"]
coverFiles          = ["beach", "candy", "car", "eagle", "fruit", "hong_kong", "man", "sculpture", "skyscraper",
                      "vegetables"]

stegoFolder         = "stegFiles/"

options             = [["0_0", " --nocompress --noencrypt"], ["0_1", " --nocompress --encrypt --password=stegoIsFun"], ["1_0", " --compress --noencrypt"], ["1_1", " --compress --encrypt --password=stegoIsFun"]]

cols                = ["File Name", "Message File Type", "Cover File Size", "Message File Size", "Stego File Size",
                     "Embedding Rate", "Compression", "Encryption", "Stego Detected", "Estimated Hidden Data"]

cols2               = ["File Name", "Message File Type", "Cover File Size", "Message File Size",
                     "Embedding Rate", "Compression", "Encryption"]

numberOfTotalFiles = len(coverFiles) * len(coverFileSizes) * len(messageFiles) * 4
numberOfStegoFiles = numberOfTotalFiles

# Method for generating the stego files
def generateStegoFiles():
    global numberOfStegoFiles

    rowID = 0
    rowID2 = 0

    # Initiate the progress bar
    pbarValue = 0
    widgets = [FormatLabel('Processed: %(value)d file(s) (in: %(elapsed)s)')]
    pbar = ProgressBar(widgets=widgets, maxval=numberOfTotalFiles).start()

    # Initiate the spreadsheet
    doc = xlwt.Workbook()
    sheet = doc.add_sheet("Data")
    sheet2 = doc.add_sheet("NoStego")

    writeToExcel(sheet, 0, cols, cols)
    writeToExcel(sheet2, 0, cols2, cols2)

    print "Start generating " + str(numberOfTotalFiles) + " stegofiles..."
    print "--------------------------------------------------------------"

    # Create the stego files directory if it does not exist
    if not os.path.exists(stegoFolder):
        os.makedirs(stegoFolder)

    for cf in coverFiles:
        for cfSize in coverFileSizes:
            for mf in messageFiles:
                for opt in options:
                    coverFile = cf + cfSize + ".png"
                    stegoFile = cf + cfSize + "_" + mf.split(".")[0] + "_" + opt[0] + ".png"

                    # Run OpenStego with varying options
                    command = "java -jar openstego.jar --embed --algorithm=RandomLSB --messagefile=" + messageFolder \
                              + mf + " --coverfile=" + coverFolder + coverFile + " --stegofile=" + stegoFolder \
                              + stegoFile + opt[1]
                    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    start_time = timeit.default_timer()
                    out, error = p.communicate()

                    # Spreadsheet values
                    fileName = stegoFile.split(".")[0]
                    fileType = mf.split(".")[1]
                    coverFileSize = float(os.stat(coverFolder + coverFile).st_size)
                    messageFileSize = float(os.stat(messageFolder + mf).st_size)
                    embeddingRate = float("{0:.4f}".format(messageFileSize / coverFileSize))
                    compression = int(opt[0].split("_")[0])
                    encryption = int(opt[0].split("_")[1])

                    if (len(error) != 0):
                        print "=> Error: Image size not enough to embed the data"

                        numberOfStegoFiles -= 1

                        # Write to spreadsheet
                        rowID2 += 1
                        writeToExcel(sheet2, rowID2, cols2, [fileName, fileType, coverFileSize, messageFileSize,
                                                    embeddingRate, compression, encryption])

                    else:
                        print "Generated '" + stegoFile + "' after " + "{0:.2f}".format(timeit.default_timer() - start_time) \
                              + " seconds"

                        # Additional spreadsheet values
                        stegoFileSize = float(os.stat(stegoFolder + stegoFile).st_size)
                        stegoDetected = 0
                        estimatedHiddenData = "-"

                        # Write to spreadsheet
                        rowID += 1
                        writeToExcel(sheet, rowID, cols, [fileName, fileType, coverFileSize, messageFileSize, stegoFileSize,
                                                embeddingRate, compression, encryption, stegoDetected, estimatedHiddenData])


                    # Update progressbar
                    pbarValue += 1
                    pbar.update(pbarValue)

    # Save the spreadsheet
    doc.save("data.xls")
    pbar.finish()
    print "\nAll stegofiles generated!"

# Method for analyzing the stego files
def analyzeStegoFiles():
    print "\n\n--------------------------------------------------------------"
    print "Start analyzing " + str(numberOfStegoFiles) + " stegofiles..."
    print "--------------------------------------------------------------"

    # Initiate the progress bar
    pbarValue = 0
    widgets = [FormatLabel('Analyzed: %(value)d file(s) (in: %(elapsed)s)')]
    pbar = ProgressBar(widgets=widgets, maxval=numberOfStegoFiles).start()

    # Run StegExpose
    command = "java -jar StegExpose.jar stegFiles"
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for out in iter(p.stdout.readline, ''):
        fileName = out.strip().split(" ")[0]
        hiddeDataAmount = out.strip().split(" ")[9]


        print "Stegonography detected in '" + fileName + "'"

        # Open the spreadsheet
        readBook = open_workbook("data.xls")
        wb = copy(readBook)
        sh = wb.get_sheet("Data")

        for row in range(1, numberOfStegoFiles + 1):
            # Update the spreadsheet with additional values
            if str(readBook.sheet_by_index(0).cell(row, 0).value) == fileName.split(".")[0]:
                sh.write(row, 8, 1)
                sh.write(row, 9, int(hiddeDataAmount))
                print "=> Spreadsheet updated\n"

        wb.save('data.xls')

        # Update progressbar
        pbarValue += 1
        pbar.update(pbarValue)

    pbar.finish()

def writeToExcel(sheet, rowNr, cols, values):
    row = sheet.row(rowNr)
    for index, col in enumerate(cols):
        row.write(index, values[index])

if __name__ == '__main__':
    start_time = timeit.default_timer()

    # Generate stego files
    generateStegoFiles()

    # Analyze stego files
    analyzeStegoFiles()

    print "\n\nTotal elapsed time: {0:.2f} seconds".format(timeit.default_timer() - start_time)
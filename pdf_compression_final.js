const PDFServicesSdk = require('@adobe/pdfservices-node-sdk');
const fs = require("fs");
const path = require("path");

function pdfCompression(filePath, chatID) {
    try {
        // Credential Verification Adobe Object.
        const credentials =  PDFServicesSdk.Credentials
        .servicePrincipalCredentialsBuilder()
        .withClientId(process.env.PDF_CLIENT)
        .withClientSecret(process.env.PDF_SECRET)
        .build();

        // Creating A Compression Operation Instance Using Credentials And Passing File Object.
        const executionContext = PDFServicesSdk.ExecutionContext.create(credentials);
        const compressPDF = PDFServicesSdk.CompressPDF;
        const compressPDFOperation = compressPDF.Operation.createNew();

        // Taking PDF File As An Input, Passing To CreateFile() Object.
        const pdfFile = PDFServicesSdk.FileRef.createFromLocalFile(filePath);
        compressPDFOperation.setInput(pdfFile);

        // Setting Compression Options.
        const compressionOptions = new compressPDF.options.CompressPDFOptions.Builder()
            .withCompressionLevel(PDFServicesSdk.CompressPDF.options.CompressionLevel.HIGH)
            .build();
        compressPDFOperation.setOptions(compressionOptions);

        // Creating The Output File Path.
        const outputFilePath = path.join(__dirname, `${chatID}-comp.pdf`);

        // Executing The Operation And Logging Errors.
        const logFilePath = path.join(__dirname, "errors.log");

        function logErrors(error) {
            const timeStamp = new Date().toISOString();
            const logMessage = `${timeStamp} - ERROR: ${error}\n`;

            // Appending Errors To Log File.
            fs.appendFile(logFilePath, logMessage, err => {
                if (err) {
                    console.error("Error Writing To Log File: ", err);
                }
            });
        }

        compressPDFOperation.execute(executionContext)
            .then(result => result.saveAsFile(outputFilePath))
            .catch(err => {
                if (err instanceof PDFServicesSdk.Error.ServiceApiError ||
                    err instanceof PDFServicesSdk.Error.ServiceUsageError) {
                    logErrors(err);
                } else {
                    logErrors(err);
                }
            });

    } catch (err) {
        console.log("Exception Occurred: ", err);
    }
}

// Check if enough arguments are passed
if (process.argv.length < 4) {
    console.error("Usage: node script.js <pdfFilePath> <chatID>");
    process.exit(1);
}

// Extracting command-line arguments
const pdfFilePath = process.argv[2];
const chatID = process.argv[3];

// Call the pdfCompression function with command-line arguments
pdfCompression(pdfFilePath, chatID);

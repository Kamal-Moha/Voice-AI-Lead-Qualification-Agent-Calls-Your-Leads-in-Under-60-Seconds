function doPost(e) {
  try {
    // Get the active spreadsheet and the specific sheet to write to.
    // It defaults to the first sheet, "Sheet1". Change if your sheet has a different name.
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");

    // Parse the JSON data sent from the Python script.
    const postData = JSON.parse(e.postData.contents);

    // Extract the data from the parsed JSON object.
    const toolCalls = JSON.stringify(postData.tool_calls); // Stringify the list for sheet compatibility
    const toolResults = JSON.stringify(postData.tool_call_results); // Stringify the list
    const summary = postData.summary;

    // Append a new row to the sheet with the extracted data.
    sheet.appendRow([toolCalls, toolResults, summary]);

    // Return a success response to the Python script.
    return ContentService
      .createTextOutput(JSON.stringify({ "status": "success", "message": "Row added." }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    // If an error occurs, return an error message for debugging.
    return ContentService
      .createTextOutput(JSON.stringify({ "status": "error", "message": error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

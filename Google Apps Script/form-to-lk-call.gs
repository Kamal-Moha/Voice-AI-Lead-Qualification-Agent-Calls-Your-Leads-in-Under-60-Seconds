function onSubmit(e) {
  // Get the response that was just submitted.
  // The event object 'e' is the most reliable way to get the current response.
  var itemResponses = e.response.getItemResponses();
  
  // Create an empty object to hold our data.
  var payload = {};

  // Loop through all the question-answer pairs from the submission.
  for (var i = 0; i < itemResponses.length; i++) {
    var question = itemResponses[i].getItem().getTitle();
    var answer = itemResponses[i].getResponse();

    // Assign the answer to the correct key in our payload object.
    if (question === "Name") {
      payload.name = answer;
    } else if (question === "Business Description") {
      payload.story = answer;
    } else if (question === "Phone Number") {
      payload.phone = answer;
    }
  }

  // Define the options for the webhook request.
  var options = {
    "method": "post",
    "contentType": "application/json",
    // Convert the JavaScript object to a JSON string.
    "payload": JSON.stringify(payload)
  };

  // Log the payload for debugging (optional).
  console.log("Sending payload:", JSON.stringify(payload, null, 2));

  // Send the data to the webhook URL.
  // Use the URL from the LK-Call-Initiator FastAPI. Specifically the 'call-phone' endpoint
  UrlFetchApp.fetch("<LK-Call-Initiator/call-phone>", options);
}

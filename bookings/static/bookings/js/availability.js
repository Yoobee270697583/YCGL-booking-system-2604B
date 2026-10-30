// Save the elements with user input to global constants for use later in the script
const dateInput = document.getElementById("id_date");
const startInput = document.getElementById("id_start_time");
const endInput = document.getElementById("id_end_time");
const box = document.getElementById("availability");

// Prepare a dict(ionary) of status messages in arrays, with the corresponding css classes to style them appropriately with bootstrap
const messages = {
  free: ["success", "No clash. That time is free to apply for."],
  booked: ["danger", "The clubroom is already booked at that time."],
  blackout: ["danger", "The clubroom is closed on that date."],
  order: ["warning", "The end time needs to be after the start time."],
  window: ["danger", "Applications are not open for that week."],
};

// Function to "show" or display one of the messages above to the user
// Updates the div that has the id="availability", currently saved as a variable called "box"
function show(state, text) {
  const entry = messages[state];
  // Strips css classes and tag text-content if the state passed in doesn't match any of the keys in messages
  if (!entry) {
    box.className = "";
    box.textContent = "";
    return;
  }
  // Adds or changes a message styled with bootstrap to box, as defined above by the 'messages = {}' dict
  box.className = "alert alert-" + entry[0] + " py-2";
  box.textContent = text || entry[1];
}

// Function to asynchronously check if the time the user has entered is available
async function checkAvailability() {
  // Build a query from the date, start time and end time that the user currently has selected
  const params = new URLSearchParams({
    date: dateInput.value,
    start: startInput.value,
    end: endInput.value,
  });

  try {
    // Send a GET request with the user's date & times to the 'check' view, and wait for the response
    const response = await fetch(box.dataset.url + "?" + params);
    // Wait for the data requested by the line above, then build an object from it, which comes in as JSON
    const data = await response.json();

    // Call the show function from earlier
    show(data.state, data.message);
  } catch (error) {
    // If the request fails or the reply isn't valid JSON, clear the message box so a stale message isn't left showing
    show("");
  }
}
// Attach checkAvailability to the "change" event of the three relevant fields in the form (dateInput, startInput, endInput) 
// so that it runs whenever any of them are changed
[dateInput, startInput, endInput].forEach(function (input) {
  input.addEventListener("change", checkAvailability);
});

// Run once when the page loads, so that the message box is correct from the beginning, no matter what is entered in the fields
checkAvailability();
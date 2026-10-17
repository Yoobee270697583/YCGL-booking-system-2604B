const dateInput = document.getElementById("id_date");
const startInput = document.getElementById("id_start_time");
const endInput = document.getElementById("id_end_time");
const box = document.getElementById("availability");

const messages = {
  free: ["success", "No clash. That time is free to apply for."],
  booked: ["danger", "The clubroom is already booked at that time."],
  blackout: ["danger", "The clubroom is closed on that date."],
  order: ["warning", "The end time needs to be after the start time."],
  window: ["danger", "Applications are not open for that week."],
};

function show(state, text) {
  const entry = messages[state];
  if (!entry) {
    box.className = "";
    box.textContent = "";
    return;
  }
  box.className = "alert alert-" + entry[0] + " py-2";
  box.textContent = text || entry[1];
}

async function checkAvailability() {
  const params = new URLSearchParams({
    date: dateInput.value,
    start: startInput.value,
    end: endInput.value,
  });
  try {
    const response = await fetch(box.dataset.url + "?" + params);
    const data = await response.json();
    show(data.state, data.message);
  } catch (error) {
    show("");
  }
}

[dateInput, startInput, endInput].forEach(function (input) {
  input.addEventListener("change", checkAvailability);
});
checkAvailability();
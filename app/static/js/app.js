document.addEventListener("DOMContentLoaded", function () {
  const rfidInput = document.getElementById("rfid_input");
  const miniTableBody = document.querySelector(".recent-logs tbody");

  let lastRFID = null;
  let lastScanTime = 0;
  let isProcessing = false;

  function sendRFIDData(rfid_number) {
    const formData = new FormData();
    formData.append("rfid_number", rfid_number);

    fetch("/process-rfid/", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          updateStudentInfo(data.data);
          updateRecentLogs(data.data.recent_logs);

          if (data.data.type === "login") {
            showLoginMessage(data.data);
          } else if (data.data.type === "logout") {
            showLogoutMessage(data.data);
          }
        } else {
          showUnregisteredCardError();
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        showUnregisteredCardError();
      })
      .finally(() => {
        isProcessing = false;
      });
  }

  rfidInput.addEventListener("keyup", function (event) {
    if (event.key === "Enter" || event.keyCode === 13) {
      const rfidNumber = rfidInput.value.trim();
      const currentTime = Date.now();

      if (rfidNumber && (rfidNumber !== lastRFID || (currentTime - lastScanTime >= 2000))) {
        // Only process if a different RFID or 3 seconds have passed
        lastRFID = rfidNumber;
        lastScanTime = currentTime;
        sendRFIDData(rfidNumber);
      }

      rfidInput.value = ""; // Clear the input
    }
  });

  rfidInput.focus();  // Ensure the RFID input field has focus on load
  function updateStudentInfo(studentData) {
    console.log(studentData); // Check if studentData is logged correctly

    const profilePicture = document.querySelector(".profile-picture img");
    const studentNameElement = document.getElementById("student-name");
    const studentCourseElement = document.getElementById("student-course");

    const completeUrl = studentData.picture;
    profilePicture.src = studentData.picture
        ? completeUrl
        : "https://bootdey.com/img/Content/avatar/avatar7.png";

    const middleNameInitial = studentData.middle_name ? studentData.middle_name.charAt(0) + '.' : '';
    const suffix = studentData.suffix ? ' ' + studentData.suffix : '';

    // Update the name and course below the profile picture
    studentNameElement.textContent = `${studentData.first_name} ${middleNameInitial} ${studentData.last_name}${suffix}`;
    studentCourseElement.textContent = studentData.course || 'No course available';

    const profileTable = document.querySelector(".profile-table");
    profileTable.innerHTML = `
      
      
        <tr>
            <th> <ion-icon name="alarm-sharp"></ion-icon> &nbsp;TIME </th>
        </tr>

        <tr>
         <td>${studentData.time}</td>
        </tr>

        <tr>
        <th><ion-icon name="keypad-sharp"></ion-icon>&nbsp;TYPE </th>
        </tr>

        <tr>
         <td>${studentData.type === "login" ? "Login" : "Logout"}</td>
        </tr>

        <tr>
         <th> <ion-icon name="calendar-sharp"></ion-icon>&nbsp;DATE </th>
        </tr>

        <tr>
            <td>${studentData.date}</td>
        </tr>
    `;

    rfidInput.value = "";
    rfidInput.focus();
}

function updateRecentLogs(logs) {
  miniTableBody.innerHTML = ''; // Clear the mini table body
  logs.forEach(log => {
      // Use default image if the student has no picture
      const defaultPicture = '/path/to/default-image.jpg';
      const pictureUrl = log.student.picture ? log.student.picture : defaultPicture;

      // Create a row for the mini table
      const row = document.createElement("tr");
      row.innerHTML = `
          <td><img src="${pictureUrl}" alt="Profile Picture" class="student-pic"></td>
      `;
      miniTableBody.appendChild(row); // Append the row to the mini table
  });
}


  // Functions to show Toastify messages for login and logout
  function showLoginMessage(studentData) {
    const message = `${studentData.first_name} ${studentData.last_name} entered PIT at ${studentData.time}`;
    Toastify({
      text: message,
      duration: 1000,
      close: true,
      gravity: "top",
      position: "center",
      stopOnFocus: true,
      style: {
        background: "blue",
        color: "white",
        padding: "20px",
        fontSize: "30px",
        minHeight: "50px",
        fontWeight: "bold",
      },
    }).showToast();
  }
  
  function showLogoutMessage(studentData) {
    const message = `${studentData.first_name} ${studentData.last_name} left PIT at ${studentData.time}`;
    Toastify({
      text: message,
      duration: 1000,
      close: true,
      gravity: "top",
      position: "center",
      stopOnFocus: true,
      style: {
        background: "orange",
        color: "white",
        padding: "20px",
        fontSize: "30px",
        minHeight: "50px",
        fontWeight: "bold",
      },
    }).showToast();
  }
  
  function showUnregisteredCardError() {
    Toastify({
      text: "Unregistered card. Contact Christian Badilla.",
      duration: 1000,
      close: true,
      gravity: "top",
      position: "center",
      stopOnFocus: true,
      style: {
        background: "red",
        color: "white",
        padding: "20px",
        fontSize: "30px",
        minHeight: "50px",
        fontWeight: "bold",
      },
    }).showToast();

    rfidInput.value = "";
    rfidInput.focus();
  }

  rfidInput.addEventListener("keyup", function (event) {
    if (event.key === "Enter" || event.keyCode === 13) {
      const rfidNumber = rfidInput.value.trim();
      if (rfidNumber) {
        sendRFIDData(rfidNumber);
      }
    }
  });

  rfidInput.focus();  // Ensure the RFID input field has focus on load

  // Periodically update recent logs
  setInterval(() => {
    fetch("/process-rfid/", {
      method: "POST",
      body: new FormData() // Send an empty form data to fetch recent logs
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === "success") {
        updateRecentLogs(data.data.recent_logs);
      }
    })
    .catch(error => console.error("Error fetching recent logs:", error));
  }, 5000);  // Update every 5 seconds
});

// Function to update the time and date
function updateTime() {
  const now = new Date();
  const timeString = now.toLocaleTimeString();
  
  // Format the date to "Month Day, Year" format
  const dateString = now.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric"
  });

  document.getElementById("current-time").innerText = `TIME: ${timeString}`;
  document.getElementById("current-date").innerText = `DATE: ${dateString}`;
}


setInterval(updateTime, 1000);
window.onload = updateTime;

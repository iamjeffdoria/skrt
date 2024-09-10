document.addEventListener("DOMContentLoaded", function () {
  const rfidInput = document.getElementById("rfid_input");
  const miniTableBody = document.querySelector(".recent-logs tbody");

  // Function to send RFID data to the server
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
          updateRecentLogs(data.data.recent_logs);  // Use recent_logs from the response

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
        setTimeout(() => {
          isProcessing = false;
        }, 2000);
      });
  }

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
            <th colspan="3">  <i class="fa fa-id-card" aria-hidden="true"></i> &nbsp; STUDENT ID</th>
        </tr>
        <tr>
            <td colspan="3">${studentData.student_id}</td>
        </tr>
        <tr>
            <th colspan="3"><i class="fa fa-users" aria-hidden="true"></i> &nbsp; NAME </th>
        </tr>
        <tr>
            <td colspan="3">${studentData.first_name} ${middleNameInitial} ${studentData.last_name}${suffix}</td>
        </tr>

        <tr>
            <th> <ion-icon name="alarm-sharp"></ion-icon> &nbsp;TIME </th>
            <th><ion-icon name="keypad-sharp"></ion-icon>&nbsp;TYPE </th>
            <th> <ion-icon name="calendar-sharp"></ion-icon>&nbsp;DATE </th>
        </tr>
        <tr>
            <td>${studentData.time}</td>
            <td>${studentData.type === "login" ? "Login" : "Logout"}</td>
            <td>${studentData.date}</td>
        </tr>
    `;

    rfidInput.value = "";
    rfidInput.focus();
}

  // Function to update recent logs
  function updateRecentLogs(logs) {
    miniTableBody.innerHTML = '';  // Clear the current table content
    logs.forEach(log => {
        const row = document.createElement("tr");
        const logDateTime = new Date(log.time);
        const formattedDateTime = logDateTime.toLocaleDateString() + ' ' + logDateTime.toLocaleTimeString();
        
        row.innerHTML = `
            <td>${formattedDateTime}</td>
            <td>${log.student.first_name} ${log.student.middle_name || ''} ${log.student.last_name}</td>
            <td>${log.type.charAt(0).toUpperCase() + log.type.slice(1)}</td>
        `;
        miniTableBody.appendChild(row);
    });
}

  // Functions to show Toastify messages for login and logout
  function showLoginMessage(studentData) {
    const message = `${studentData.first_name} ${studentData.last_name} entered PIT at ${studentData.time}`;
    Toastify({
      text: message,
      duration: 3000,
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
      duration: 3000,
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
      duration: 2000,
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
  const dateString = now.toISOString().split("T")[0];

  document.getElementById("current-time").innerText = `TIME: ${timeString}`;
  document.getElementById("current-date").innerText = `DATE: ${dateString}`;
}

setInterval(updateTime, 1000);
window.onload = updateTime;

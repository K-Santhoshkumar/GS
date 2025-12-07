// customer_login.js

function showMessage(message, type = "info") {
  // Remove existing message
  const existingMessage = document.querySelector(".popup-message");
  if (existingMessage) {
    existingMessage.remove();
  }

  // Create message element
  const messageDiv = document.createElement("div");
  messageDiv.className = `popup-message ${type}`;
  messageDiv.textContent = message;

  // Add to page
  document.body.appendChild(messageDiv);

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (messageDiv.parentNode) {
      messageDiv.remove();
    }
  }, 5000);
}

function sendOtp(event) {
  event.preventDefault();
  const email = document.getElementById("email").value;

  if (!email) {
    showMessage("Please enter your email address", "error");
    return;
  }

  // Get CSRF token from cookie
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  fetch("/users/customer/send-otp/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken") || "",
    },
    body: JSON.stringify({
      email: email,
      purpose: "LOGIN",
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Hide send OTP button and show OTP input
        document.querySelector(".btn-send-otp").style.display = "none";
        document.getElementById("otp-section").style.display = "block";
        showMessage(
          "OTP sent successfully! Please check your email.",
          "success"
        );
      } else {
        showMessage(data.message || "Failed to send OTP", "error");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showMessage("An error occurred while sending OTP", "error");
    });
}

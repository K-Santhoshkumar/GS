function showMessage(message, type) {
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
  const phone = document.getElementById("phone").value.trim();

  if (!phone) {
    showMessage("Please enter your phone number", "error");
    return;
  }
  if (!/^\+?[0-9]{10,15}$/.test(phone)) {
    showMessage("Please enter a valid phone number", "error");
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
      purpose: "SIGNUP",
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Hide send OTP button and show OTP input
        document.querySelector(".btn-send-otp").style.display = "none";

        const otpDiv = document.createElement("div");
        otpDiv.className = "otp-input-section";
        otpDiv.innerHTML = `
        <label for="otp_code">Enter OTP</label>
        <input type="text" id="otp_code" name="otp_code" placeholder="Enter 6-digit OTP" required maxlength="6" class="otp-input">
        <button type="submit" class="btn-verify-otp" onclick="verifyOtp(event)">Verify OTP & Register</button>
      `;
        document
          .querySelector(".register-form")
          .insertBefore(otpDiv, document.querySelector(".terms-text"));
        showMessage("OTP sent successfully!", "success");
      } else {
        showMessage(data.message || "Failed to send OTP", "error");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showMessage("An error occurred while sending OTP", "error");
    });
}

function verifyOtp(event) {
  event.preventDefault();
  const email = document.getElementById("email").value;
  const otpCode = document.getElementById("otp_code").value;

  if (!otpCode) {
    showMessage("Please enter the OTP", "error");
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

  // Submit the form with OTP data
  const form = document.querySelector(".register-form");
  const formData = new FormData(form);
  formData.append("otp_code", otpCode);

  fetch("/users/customer/register/", {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken") || "",
    },
    body: formData,
  })
    .then((response) => {
      if (response.redirected) {
        window.location.href = response.url;
      } else {
        return response.text();
      }
    })
    .then((data) => {
      if (data) {
        // If not redirected, parse the HTML response for messages
        const parser = new DOMParser();
        const doc = parser.parseFromString(data, "text/html");
        const messages = doc.querySelectorAll(".messages .alert");
        if (messages.length > 0) {
          showMessage(messages[0].textContent.trim(), "error");
        } else {
          showMessage("Registration failed. Please try again.", "error");
        }
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showMessage("An error occurred during registration", "error");
    });
}

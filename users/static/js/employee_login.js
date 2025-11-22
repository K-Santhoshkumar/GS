function sendOtp(event) {
  event.preventDefault();
  const email = document.getElementById("email").value;

  if (!email) {
    alert("Please enter your email address");
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

  fetch("/users/employee/send-otp/", {
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
        alert("OTP sent successfully! Please check your email.");
      } else {
        alert(data.message || "Failed to send OTP");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("An error occurred while sending OTP");
    });
}

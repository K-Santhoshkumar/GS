function showMessage(message, type) {
  const existingMessage = document.querySelector(".popup-message");
  if (existingMessage) existingMessage.remove();

  const div = document.createElement("div");
  div.className = `popup-message ${type}`;
  div.textContent = message;

  document.body.appendChild(div);

  setTimeout(() => div.remove(), 5000);
}

function sendOtp(event) {
  event.preventDefault();
  const email = document.getElementById("email").value.trim();

  if (!email) return showMessage("Please enter your email address", "error");

  function getCookie(name) {
    let cookie = null;
    const cookies = document.cookie.split(";");
    cookies.forEach((c) => {
      const trimmed = c.trim();
      if (trimmed.startsWith(name + "="))
        cookie = decodeURIComponent(trimmed.slice(name.length + 1));
    });
    return cookie;
  }

  fetch("/users/broker/send-otp/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken") || "",
    },
    body: JSON.stringify({ email, purpose: "LOGIN" }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        document.querySelector(".btn-send-otp").style.display = "none";
        document.getElementById("otp-section").style.display = "block";
        showMessage("OTP sent successfully!", "success");
      } else {
        showMessage(data.message || "Failed to send OTP", "error");
      }
    })
    .catch(() => showMessage("Error sending OTP", "error"));
}

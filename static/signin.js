const checkEnter = (event) => {
  if (event.key === "Enter") {
    signin();
  }
}

const signin = () => {
  var email = document.getElementById("email").value;
  var password = document.getElementById("password").value;

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (emailRegex.test(email) && password.trim() !== "") {
    window.location.href = "home.html";
  } else {
    alert("Invalid email or password");
  }
  document.getElementById("loginForm").reset();
  document.getElementById("email").focus();
} 

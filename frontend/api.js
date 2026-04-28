const modal = document.getElementById("auth-modal");
const closeBtn = document.querySelector(".close-btn");
const form = document.getElementById("auth-form");
const title = document.getElementById("modal-title");
const errorMsg = document.getElementById("error-message");

let currentAction = ""; 
const BACKEND_URL = "http://127.0.0.1:8000"; // URL mặc định của uvicorn

document.getElementById("btn-show-login").addEventListener("click", () => {
    modal.style.display = "flex";
    title.innerText = "Login to Lumina";
    currentAction = "login";
    errorMsg.innerText = "";
});

document.getElementById("btn-show-signup").addEventListener("click", () => {
    modal.style.display = "flex";
    title.innerText = "Create Account";
    currentAction = "signup";
    errorMsg.innerText = "";
});

closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
});

form.addEventListener("submit", async (e) => {
    e.preventDefault(); 
    errorMsg.innerText = "Đang kết nối...";
    
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    
    try {
        const response = await fetch(`${BACKEND_URL}/${currentAction}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            if (currentAction === "login") {
                localStorage.setItem("lumina_token", data.access_token);
                alert("✅ Đăng nhập thành công!");
                modal.style.display = "none";
            } else {
                alert("✅ Đăng ký thành công! Vui lòng bấm Login để đăng nhập.");
                modal.style.display = "none";
            }
        } else {
            errorMsg.innerText = "❌ " + (data.detail || "Sai thông tin");
        }
    } catch (error) {
        errorMsg.innerText = "❌ Không tìm thấy Backend! Nhớ bật Uvicorn nhé.";
        console.error(error);
    }
});

// Đóng Modal khi người dùng click ra ngoài vùng tối (overlay)
window.addEventListener("click", (event) => {
    // Kiểm tra xem nơi người dùng click có chính xác là cái nền tối (modal) hay không
    if (event.target === modal) {
        modal.style.display = "none";
    }
});
const BACKEND_URL = "http://127.0.0.1:8000";

function validateEmail(email) {
    const re = /^[a-z0-9](\.?[a-z0-9]){4,}@gmail\.com$/;
    return re.test(String(email).toLowerCase());
}

function clearAllErrors(type) {
    const errorFields = document.querySelectorAll(`#scene-${type} .field-error`);
    const generalError = document.getElementById(`${type}-general-error`);
    const inputs = document.querySelectorAll(`#scene-${type} .form-input`);
    errorFields.forEach(f => f.innerText = "");
    if (generalError) generalError.innerText = "";
    inputs.forEach(i => i.classList.remove("input-error"));
}

async function handleAuth(e, type) {
    e.preventDefault(); 
    clearAllErrors(type);

    const emailInput = document.getElementById(`${type}-email`);
    const emailError = document.getElementById(`${type}-email-error`);
    const generalError = document.getElementById(`${type}-general-error`);
    let hasError = false;

    // A. KIỂM TRA ĐỊNH DẠNG TẠI FRONTEND
    if (!validateEmail(emailInput.value.trim())) {
        emailError.innerText = "❌ Email không hợp lệ (phải là @gmail.com)!";
        emailInput.classList.add("input-error");
        hasError = true;
    }

    if (type === "signup") {
        const pass = document.getElementById("signup-password").value;
        const confirmInput = document.getElementById("signup-confirm-password");
        const confirmError = document.getElementById("signup-confirm-password-error");
        if (pass !== confirmInput.value) {
            confirmError.innerText = "❌ Mật khẩu không khớp!";
            confirmInput.classList.add("input-error");
            hasError = true;
        }
    }

    if (hasError) return;

    // B. GỬI DỮ LIỆU THẬT LÊN SERVER (Đã sửa lỗi placeholder)
    try {
        const payload = {
            email: emailInput.value.trim(),
            password: document.getElementById(`${type}-password`).value
        };
        
        if (type === "signup") {
            payload.username = document.getElementById("signup-username").value.trim();
        }

        // Map "signin" to "login" endpoint for backend compatibility
        const endpoint = type === "signin" ? "login" : type;
        const response = await fetch(`${BACKEND_URL}/${endpoint}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            if (type === "signup") {
                // Đăng ký thành công -> Tự động đăng nhập
                localStorage.setItem("lumina_token", data.access_token);
                localStorage.setItem("currentUser", JSON.stringify({ 
                    email: payload.email,
                    username: payload.username
                }));
                transitionManager.updateAuthUI();
                transitionManager.transitionTo('dashboard');
            } else {
                // Đăng nhập thành công -> Lưu token và vào Dashboard
                localStorage.setItem("lumina_token", data.access_token);
                // Lưu thêm thông tin user để transitions.js nhận diện đã auth
                localStorage.setItem("currentUser", JSON.stringify({ email: payload.email }));
                transitionManager.updateAuthUI();
                transitionManager.transitionTo('dashboard');
            }
        } else {
            const detail = data.detail || "Thao tác thất bại";
            
            // Tự động đưa lỗi về đúng ô bị sai
            if (detail.includes("Email") || detail.includes("email")) {
                emailError.innerText = "❌ " + detail;
                emailInput.classList.add("input-error");
            } else if (detail.includes("User name") || detail.includes("username") || detail.includes("Tên đăng nhập")) {
                const uError = document.getElementById("signup-username-error");
                const uInput = document.getElementById("signup-username");
                if (uError) uError.innerText = "❌ " + detail;
                if (uInput) uInput.classList.add("input-error");
            } else {
                generalError.innerText = "❌ " + detail;
            }
        }
    } catch (err) {
        console.error("Lỗi:", err);
        generalError.innerText = "❌ Lỗi kết nối server! Hãy chắc chắn uvicorn đang chạy.";
    }
}

// Gắn sự kiện (Đảm bảo ID trong HTML của bạn đúng là signup-form và signin-form)
document.getElementById("signup-form").addEventListener("submit", (e) => handleAuth(e, "signup"));
document.getElementById("signin-form").addEventListener("submit", (e) => handleAuth(e, "signin"));
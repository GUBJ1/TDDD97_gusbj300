var welcomeview;
var profileview;
const passwordMinLength = 6;
const password ="";
var token;
var browsingEmail;
let socket;

displayView = function(view){
    document.getElementById("displayWindow").innerHTML = view.innerHTML;

};
window.onload = function(){
    welcomeview = document.getElementById("welcomeview");
    profileview = document.getElementById("profileview");
    var savedToken = localStorage.getItem("token");

    if (savedToken) {
        token = savedToken;

        displayView(profileview);
        showInfo();
        enableWallDragAndDrop();
        connectSocket();
    } else {
        displayView(welcomeview);
    }
};

function connectSocket() {
    socket = new WebSocket("ws://localhost:5000/ws?token=" + encodeURIComponent(token));
    socket.onmessage = handleSocketMessage;
}

function handleSocketMessage(event) {
    let data;

    try {
        data = JSON.parse(event.data);
    } catch (error) {
        console.error("Invalid WebSocket message:", event.data);
        return;
    }

    if (data.type === "force_logout") {
        token = null;
        localStorage.removeItem("token");
        sessionStorage.removeItem("token");

        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.close();
        }
        socket = null;
        displayView(welcomeview);

        const msg = document.getElementById("signInMessage");
        if (msg) {
            msg.textContent = "You were signed out because your account was used somewhere else.";
        }

        return;
    }
}

function signUp() {
    var signUpMessage = document.getElementById("signUpMessage");
    var email = document.getElementById("signUpEmail").value.trim();
    var firstName = document.getElementById("firstName").value.trim();
    var familyName = document.getElementById("familyName").value.trim();
    var gender = document.getElementById("gender").value.trim();
    var city = document.getElementById("city").value.trim();
    var country = document.getElementById("country").value.trim();
    var password = document.getElementById("signUpPassword").value;
    var repeatPassword = document.getElementById("repeatPassword").value;

    if (!email || !firstName || !familyName || !gender || !city || !country || !password || !repeatPassword) {
        signUpMessage.innerHTML = "You forgot to enter required credentials";
        return;
    }

    var emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailPattern.test(email)) {
        signUpMessage.innerHTML = "Incorrect email format";
        return;
    }

    if (password.length < 6) {
        signUpMessage.innerHTML = "Password is too short";
        return;
    }

    if (password !== repeatPassword) {
        signUpMessage.innerHTML = "Passwords do not match";
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/signUp", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
            
            if (xhr.status == 201){
                message = "User succesfully created!"
                document.getElementById("signUpMessage").innerHTML = message;
            } else if (xhr.status == 400){
                message = "You are missing, or entered incorrect input"
                document.getElementById("signUpMessage").innerHTML = message;
            } else if (xhr.status == 409){
                message = "A user with that email already exists"
                document.getElementById("signUpMessage").innerHTML = message;            
            } else
                message = "Unexpected error, user could not be created"
                document.getElementById("signUpMessage").innerHTML = message;
        } 
    };

    xhr.send(JSON.stringify({email: email, password: password, firstName: firstName, familyName: familyName, gender: gender, city: city, country: country
    }));
}

function signIn(){
    var username = document.getElementById("logInEmail").value;
    var password = document.getElementById("password").value;

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/signIn", true);
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4){

            if (xhr.status == 200){
                token = xhr.getResponseHeader("Authorization");

                connectSocket();
                
                localStorage.setItem("token", token);
                displayView(profileview);
                showInfo();
            } else if (xhr.status == 400){
                message = "You forgot to enter required credentials"
                document.getElementById("signInMessage").innerHTML = message;
            } else if (xhr.status == 401){
                message = "You entered a incorrect email or password"
                document.getElementById("signInMessage").innerHTML = message;
            } else {
                message = "unexpected error, could not sign in"
                document.getElementById("signInMessage").innerHTML = message; 
            }
               
        } 
    };

    xhr.send(JSON.stringify({email: username, password: password}));
}
        
function showPanel(panelNumber){
    document.getElementById("panel1").style.display = "none";
    document.getElementById("panel2").style.display = "none";
    document.getElementById("panel3").style.display = "none";
    document.getElementById("panel" + panelNumber).style.display = "block";

    let buttons = document.querySelectorAll("#tabs button");
    buttons.forEach(btn => btn.classList.remove("active"));
    buttons[panelNumber - 1].classList.add("active");

    if (panelNumber === 1) {
        browsingEmail = null;
        document.getElementById("otherEmail").value = "";
    }

}

function changePassword() {
    var oldPassword = document.getElementById("old_password").value;
    var newPassword = document.getElementById("new_password").value;
    var rptNewPassword = document.getElementById("rpt_new_password").value;
    var passwordMessage = document.getElementById("passwordMessage");

    if (newPassword.length < passwordMinLength) {
        passwordMessage.innerHTML = "New password too short!";
        return;
    }

    if (newPassword !== rptNewPassword) {
        passwordMessage.innerHTML = "Passwords do not match!";
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/changePassword", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Authorization", token);
    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
            if (xhr.status == 200){
                message = "password was succesfully changed!"
                document.getElementById("passwordMessage").innerHTML = message;

                document.getElementById("old_password").value = "";
                document.getElementById("new_password").value = "";
                document.getElementById("rpt_new_password").value = "";
            } else if (xhr.status == 400){
                message = "Ditta gamla lösenord är fel, eller så är ditt nya för kort"
                document.getElementById("passwordMessage").innerHTML = message;
            } else if (xhr.status == 401){
                message = "Missing credentials (token error)"
                document.getElementById("passwordMessage").innerHTML = message;                
            } else if (xhr.status == 500){
                message = "Server error"
                document.getElementById("passwordMessage").innerHTML = message;
            } else {
                message = "unexpected error"
                document.getElementById("passwordMessage").innerHTML = message;
            }
        }
    };

    xhr.send(JSON.stringify({oldPassword: oldPassword, newPassword: newPassword}));
}

function signOut() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/signOut", true);
    xhr.setRequestHeader("Authorization", token);

    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
            if (xhr.status == 200){
                if (socket) {
                    socket.close();
                    socket = null;
                }
                token = null;
                localStorage.removeItem("token");
                displayView(welcomeview);
            } else if (xhr.status == 400){
                message = "lowkey servererror"
                document.getElementById("passwordMessage").innerHTML = message;    
            } else if (xhr.status == 401){
                message = "Invalid token, you are cooked"
                document.getElementById("passwordMessage").innerHTML = message;
            } else {
                message = "Unexpected error"
                document.getElementById("passwordMessage").innerHTML = message;
            }
        }
    };
    xhr.send();
}

function showInfo() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/getUserDataByToken", true);
    xhr.setRequestHeader("Authorization", token);
    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
            if (xhr.status == 200){ 
                const response = JSON.parse(xhr.responseText);
                var user = response.data;

                document.getElementById("profileCity").innerHTML = user.city;
                document.getElementById("profileFirstName").innerHTML = user.firstName;
                document.getElementById("profileFamilyName").innerHTML = user.familyName;
                document.getElementById("profileGender").innerHTML = user.gender;
                document.getElementById("profileEmail").innerHTML = user.email;
                document.getElementById("profileCountry").innerHTML = user.country;
            } else if (xhr.status == 401){
                token = null;
                localStorage.removeItem("token");

                if (socket) {
                    socket.close();
                    socket = null;
                }

                displayView(welcomeview);
            }

        }
    };

    xhr.send(); 
}

function postToMyWall() {
    const content = document.getElementById("wallInput").value.trim();
    if (!content) return;

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/postMessage", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Authorization", token);
    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
            if (xhr.status == 201){
                document.getElementById("wallInput").value = "";
                reloadWall();
            } else if (xhr.status == 400){
                message = "Cant post empty messages"
                document.getElementById("ownWallMessage").innerHTML = message;
            } else if (xhr.status == 401){
                token = null;
                localStorage.removeItem("token");

                if (socket) {
                    socket.close();
                    socket = null;
                }

                displayView(welcomeview);
            } else {
                message = "Unexpected error"
                document.getElementById("ownWallMessage").innerHTML = message;
            }
        }
    };
    xhr.send(JSON.stringify({message: content, receiver: browsingEmail}));
}

function reloadWall() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/getUserMessageByToken", true);
    xhr.setRequestHeader("Authorization", token);
    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
            if (xhr.status == 200){
                const response = JSON.parse(xhr.responseText);
                const wallList = document.getElementById("wallList");
                wallList.innerHTML = "";

                response.data.forEach(msg => {
                    const item = document.createElement("div");
                    item.className = "wallMessage";
                    item.textContent = msg.sender + ": " + msg.message;

                    item.draggable = true;
                    item.addEventListener("dragstart", (event) => {
                    event.dataTransfer.setData("text/plain", msg.message);
                    });
                    wallList.appendChild(item);

                });


            } else if (xhr.status == 401) {
                token = null;
                localStorage.removeItem("token");

                if (socket) {
                    socket.close();
                    socket = null;
                }

                displayView(welcomeview);
            } else {
                message = "Unexpected error"
                document.getElementById("ownWallMessage").innerHTML = message;
            }
        }
    };

    xhr.send();
}

function browse() {
    browsingEmail = document.getElementById("otherEmail").value.trim();
    var browseMessage = document.getElementById("browseMessage");

    if (!browsingEmail) {
        browseMessage.innerHTML = "Please enter an email";
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/getUserDataByEmail?email=" + encodeURIComponent(browsingEmail), true);
    xhr.setRequestHeader("Authorization", token);
    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
            if (xhr.status == 200){
                const response = JSON.parse(xhr.responseText);
                var user = response.data;

                document.getElementById("browseCity").innerHTML = user.city;
                document.getElementById("browseFirstName").innerHTML = user.firstName;
                document.getElementById("browseFamilyName").innerHTML = user.familyName;
                document.getElementById("browseGender").innerHTML = user.gender;
                document.getElementById("browseEmail").innerHTML = user.email;
                document.getElementById("browseCountry").innerHTML = user.country;

                browseMessage.innerHTML = "";
            } else if (xhr.status == 401){
                token = null;
                localStorage.removeItem("token");

                if (socket) {
                    socket.close();
                    socket = null;
                }

                displayView(welcomeview);
            } else if (xhr.status == 404){
                message = "User not found"
                document.getElementById("browseMessage").innerHTML = message;
            } else {
                message = "Unexpected erreor"
                document.getElementById("browseMessage").innerHTML = message;
            }

        }
    };

    xhr.send();
}

function postToOtherWall() {
    var toEmail = document.getElementById("otherEmail").value.trim();
    var content = document.getElementById("otherWallInput").value.trim();
    var browseMessage = document.getElementById("browseMessage");

    if (!toEmail) {
        browseMessage.innerHTML = "Please enter an email first";
        return;
    }

    if (!content) {
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/postMessage", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("Authorization", token);
    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
            if (xhr.status == 201){
                document.getElementById("otherWallInput").value = "";
                browseMessage.innerHTML = "";
                reloadOtherWall();
            } else if (xhr.status == 400){
                message = "Cant post empty messages"
                document.getElementById("browseMessage").innerHTML = message;
            } else if (xhr.status == 401){
                token = null;
                localStorage.removeItem("token");

                if (socket) {
                    socket.close();
                    socket = null;
                }

                displayView(welcomeview);
            } else {
                message = "Unexpected error"
                document.getElementById("browseMessage").innerHTML = message;
            }
        }
    };

    xhr.send(JSON.stringify({receiver: toEmail, message: content}));
}

function reloadOtherWall() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/getUserMessageByEmail?email=" + encodeURIComponent(browsingEmail), true);
    xhr.setRequestHeader("Authorization", token);

    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
            if (xhr.status == 200){
                var response = JSON.parse(xhr.responseText);
                const wallList = document.getElementById("otherWallList");
                wallList.innerHTML = "";

                response.data.forEach(msg => {
                    const item = document.createElement("div");
                    item.className = "wallMessage";
                    item.textContent = msg.sender + ": " + msg.message;
                    wallList.appendChild(item);
                });
            } else if (xhr.status == 401){
                token = null;
                localStorage.removeItem("token");

                if (socket) {
                    socket.close();
                    socket = null;
                }

                displayView(welcomeview);              
            } else if (xhr.status == 404){
                message = "User not found, cant post message"
                document.getElementById("browseMessage").innerHTML = message;                
            } else {
                message = "Unexpected error"
                document.getElementById("browseMessage").innerHTML = message;                

            }


        }
    };

    xhr.send();
}

function enableWallDragAndDrop() {
    const postBox = document.getElementById("wallInput");

    postBox.addEventListener("dragover", (event) => {
        event.preventDefault();
    });

    postBox.addEventListener("drop", (event) => {
        event.preventDefault();
        const draggedText = event.dataTransfer.getData("text/plain");
        postBox.value = draggedText;
    });
}
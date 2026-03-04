var welcomeview;
var profileview;
const passwordMinLength = 8;
const password ="";
var token;


displayView = function(view){
    document.getElementById("displayWindow").innerHTML = view.innerHTML;

};
window.onload = function(){
    welcomeview = document.getElementById("welcomeview");
    profileview = document.getElementById("profileview");
    displayView(welcomeview);
};

function signUp(form){

    const signUpMessage = document.getElementById("signUpMessage");

    var signUpEmail = document.getElementById("signUpEmail").value;
    var firstName = document.getElementById("firstName").value;
    var familyName = document.getElementById("familyName").value;
    var gender = document.getElementById("gender").value; 
    var city = document.getElementById("city").value;
    var country = document.getElementById("country").value;
    var gender = document.getElementById("gender").value;
    var signUpPassword = document.getElementById("signUpPassword").value;
    var gender = document.getElementById("gender").value;

    var repeatPassword = document.getElementById("repeatPassword").value;


    if (signUpPassword.length < passwordMinLength){
        console.log("Too short");
        signUpMessage.textContent = "Password is too short";
    }
    else if (signUpPassword != repeatPassword){
        console.log("Does not match")
        signUpMessage.textContent = "Passwords doesnt match";
    }
    else {
        var newUser = {
            "email":signUpEmail,
            "password":signUpPassword,
            "firstname":firstName,
            "familyname":familyName,
            "gender":gender,
            "city":city,
            "country":country
        }
        var newUserProfile = serverstub.signUp(newUser);
        var message = document.getElementById("message");

        message.innerHTML = newUserProfile.message;
        console.log("User is from:", city.value);
    }
}
function signIn(){
    var username = document.getElementById("logInEmail").value;
    var password = document.getElementById("password").value;

    var user = serverstub.signIn(username, password);

    if (user.success == true){
        token = user.data
        console.log("Token:", token);
        displayView(profileview);
        //showInfo();

    }
}
function showPanel(panelNumber){
    document.getElementById("panel1").style.display = "none";
    document.getElementById("panel2").style.display = "none";
    document.getElementById("panel3").style.display = "none";
    document.getElementById("panel" + panelNumber).style.display = "block";

    let buttons = document.querySelectorAll("#tabs button");
    buttons.forEach(btn => btn.classList.remove("active"));

    buttons[panelNumber - 1].classList.add("active");

}

function changePassword(){
    var oldPassword = document.getElementById("old_password").value;
    var newPassword = document.getElementById("new_password").value;
    var rptNewPassword = document.getElementById("rpt_new_password").value;

    if (newPassword.length < passwordMinLength) {
        passwordMessage.innerHTML = "New password too short!";
    } else if (newPassword != rptNewPassword){
        passwordMessage.innerHTML = "Passwords does not match!";
    } else {
        let response = serverstub.changePassword(token, oldPassword, newPassword);
        if (!response.succsess){
            passwordMessage.innerHTML = response.message
        }
    }
}
function signOut(){
    var result = serverstub.signOut(token)
    console.log(result.message)
    displayView(welcomeview)
}
function showInfo(){
    var result = serverstub.getUserDataByToken(token);
    console.log("hej");

    if (result.success == true){
    var user = result.data;
    document.getElementById("profileCity").innerHTML = user.city;
    document.getElementById("profileFirstName").innerHTML = user.firstname;
    document.getElementById("profileFamilyName").innerHTML = user.familyname;
    document.getElementById("profileGender").innerHTML = user.gender;
    document.getElementById("profileEmail").innerHTML = user.email;
    document.getElementById("profileCountry").innerHTML = user.country;
    }

    else {
        console.log(result.message);
        return;
    }
}
function postToMyWall() {
    const content = document.getElementById("wallInput").value.trim();
    if (!content) return;

    const res = serverstub.postMessage(token, content, null); // null = min vägg
    if (!res.success) {
        console.log(res.message);
        return;
    }

    document.getElementById("wallInput").value = "";
    reloadWall();
}


function reloadWall() {
    const res = serverstub.getUserMessagesByToken(token);
    if (!res.success) {
        console.log(res.message);
        return;
    }
    const wallList = document.getElementById("wallList");
    wallList.innerHTML = "";

    res.data.forEach(msg => {
        const item = document.createElement("div");
        item.className = "wallMessage";
        item.textContent = msg.writer + ": " + msg.content;
        wallList.appendChild(item);
    });
}

function browse(){
    var email = document.getElementById("otherEmail")
    var userInfo = serverstub.getUserDataByEmail(token, email.value);

    if (userInfo.success == true){

    var user = userInfo.data;
    document.getElementById("browseCity").innerHTML = user.city;
    document.getElementById("browseFirstName").innerHTML = user.firstname;
    document.getElementById("browseFamilyName").innerHTML = user.familyname;
    document.getElementById("browseGender").innerHTML = user.gender;
    document.getElementById("browseEmail").innerHTML = user.email;
    document.getElementById("browseCountry").innerHTML = user.country;
    console.log("funkar");
    }

    else{
        browseMessage.innerHTML = userInfo.message;
    }
}

function postToOtherWall() {
    var toEmail = document.getElementById("otherEmail").value.trim();
    const content = document.getElementById("otherWallInput").value.trim();
    console.log("test 1");
    if (!content) return;
    console.log("test 2");

    const res = serverstub.postMessage(token, content, toEmail);
    console.log("token:", token, "content:", content, "to email:", toEmail);
    if (!res.success) {
        console.log(res.message);
        return;
    }
    document.getElementById("wallInput").value = "";

}

function reloadOtherWall() {
    console.log("testar knapp");
    var email = document.getElementById("otherEmail");
    const res = serverstub.getUserMessagesByEmail(token, email.value);
    if (!res.success) {
        console.log(res.message);
        return;
    }
    const wallList = document.getElementById("otherWallList");
    wallList.innerHTML = "";

    res.data.forEach(msg => {
        const item = document.createElement("div");
        item.className = "wallMessage";
        item.textContent = msg.writer + ": " + msg.content;
        wallList.appendChild(item);
    });
}
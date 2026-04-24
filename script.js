let lat=0, lon=0, currentEmail=""

// -------- TYPING --------
let keyTimes=[], lastKeyTime=0
let keyDownTime={}, holdTimes=[]

// -------- MOUSE --------
let lastX=0,lastY=0,lastTime=0
let speeds=[], clicks=0

document.addEventListener("keydown", e=>{
let now=Date.now()
if(lastKeyTime) keyTimes.push(now-lastKeyTime)
lastKeyTime=now
keyDownTime[e.key]=now
})

document.addEventListener("keyup", e=>{
if(keyDownTime[e.key]){
holdTimes.push(Date.now()-keyDownTime[e.key])
}
})

document.addEventListener("mousemove", e=>{
let now=Date.now()
if(lastTime){
let dx=e.clientX-lastX
let dy=e.clientY-lastY
let dt=now-lastTime
speeds.push(Math.sqrt(dx*dx+dy*dy)/dt)
}
lastX=e.clientX
lastY=e.clientY
lastTime=now
})

document.addEventListener("click", ()=>clicks++)

// -------- LOCATION --------
navigator.geolocation.getCurrentPosition(pos=>{
lat=pos.coords.latitude
lon=pos.coords.longitude
})

// -------- BEHAVIOUR --------
function getData(){
let avgGap=keyTimes.length?keyTimes.reduce((a,b)=>a+b)/keyTimes.length:0
let speed=avgGap?1000/avgGap:0
let hold=holdTimes.length?holdTimes.reduce((a,b)=>a+b)/holdTimes.length:0
let mouse=speeds.length?speeds.reduce((a,b)=>a+b)/speeds.length:0

return {
typing_speed:speed,
typing_gap:avgGap,
hold_time:hold,
mouse_speed:mouse,
clicks:clicks,
lat:lat,
lon:lon
}
}

// -------- REGISTER --------
function registerUser(){
fetch("/register",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
email:email.value,
password:password.value,
secret:secret.value,
answer:answer.value,
...getData()
})
})
.then(r=>r.json())
.then(d=>alert(d.message||d.error))
}

// -------- LOGIN --------
function loginUser(){

currentEmail = email.value

fetch("/login",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
email: email.value,
password: password.value,
...getData()
})
})
.then(r=>r.json())
.then(d=>{

if(d.error){
alert(d.error)
return
}

// ✅ SUCCESS
if(d.status==="success"){
localStorage.setItem("email", email.value)   // 🔥 ADD THIS
localStorage.setItem("trust", d.trust)
location="/dashboard"
}

// ⚠️ VERIFY FLOW
else{
questionBox.style.display="block"
question.innerText=d.question
}

})
}

// -------- VERIFY --------
function verifyAnswer(){
fetch("/verify",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
email:currentEmail,
answer:ans.value
})
})
.then(r=>r.json())
.then(d=>{
if(d.status==="success"){
location="/dashboard"
}else{
otpBox.style.display="block"
fetch("/send-otp",{method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({email:currentEmail})})
}
})
}

// -------- OTP --------
function verifyOTP(){
fetch("/verify-otp",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
email:currentEmail,
otp:otp.value
})
})
.then(r=>r.json())
.then(d=>{
if(d.status==="success"){
location="/dashboard"
}else{
alert("Wrong OTP ❌")
}
})
}
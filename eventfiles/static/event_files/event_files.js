window.onload=function(){
    const fileName = document.getElementById("fileInput");
    const submit=  document.getElementById('submitBtn');
    fileName.addEventListener("change", (e) => {
        document.getElementById("uploadFile").value = e.target.files[0].name;
        submit.className ='button';
    });

    document.getElementById('uploadBtn').addEventListener('click', () => {
        document.getElementById('fileInput').click()
    })
}
    function CustomConfirm(){
	this.render = function(dialog,event_id,file_id){
        const winW = window.innerWidth;
        const winH = window.innerHeight;
        const dialogoverlay = document.getElementById('dialogoverlay');
        const dialogbox = document.getElementById('dialogbox');
        dialogoverlay.style.display = "block";
        dialogoverlay.style.height = "100%";
        dialogbox.style.left = "-20%";
        dialogbox.style.top = "25%";
        dialogbox.style.display = "block";
        document.getElementById('dialogboxhead').innerHTML = "File Delete";
        document.getElementById('dialogboxbody').innerHTML = `Are you sure you want to ${dialog}?`;
        document.getElementById('dialogboxfoot').innerHTML = ` <span><button class="YesNoButton"><a class="DeleteRef" href="${event_id}/delete/${file_id}"> Yes </a></button> <button class="YesNoButton" onclick=Confirm.no()>Cancel</button></span>`;
	}
	this.no = function(){
		document.getElementById('dialogbox').style.display = "none";
		document.getElementById('dialogoverlay').style.display = "none";
	}
}
const Confirm = new CustomConfirm();



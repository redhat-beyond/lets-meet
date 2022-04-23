window.onload=function(){
    const fileName = document.getElementById("uploadBtn");
    fileName.addEventListener("change", (e) => {
	document.getElementById("uploadFile").value = e.target.files[0].name;
    });
}



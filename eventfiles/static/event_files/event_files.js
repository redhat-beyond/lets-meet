window.onload=function(){
    const fileName = document.getElementById("fileInput");
    fileName.addEventListener("change", (e) => {
	document.getElementById("uploadFile").value = e.target.files[0].name;
    });

    document.getElementById('uploadBtn').addEventListener('click', () => {
  document.getElementById('fileInput').click()
})
}



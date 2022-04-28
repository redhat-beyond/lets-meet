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



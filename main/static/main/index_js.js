
function eventCreation() {
    Swal.fire({
        heightAuto: false,
        title: '<strong style="color: white; text-decoration: underline;">Add New Event:</strong>',
        background: "url(https://images.unsplash.com/photo-1565061326832-cd738486b695?ixlib=rb-1.2.1&ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&auto=format&fit=crop&w=934&q=80) center, center",
        html:
            '<label style="color: white;"> Event Title:</label><input type="text" id="swal-input1" name="companyName" class="swal2-input" style="color: white;" required>' +
            '<label style="color: white;"> Date and Time:</label>' +
            '<div class="md-form mx-5 my-5">' +
              '<input placeholder="Selected date" type="date" class="form-control time-date-ghost">' +
              '<input placeholder="Selected time" type="time" class="form-control timepicker time-date-ghost">' +
            '</div><br>' +
            '<label style="color: white;"> location:</label><input type="text" id="swal-input3" name="quantity" style="color: white; min-width: 100%;" class="swal2-input" required>' +
            '<label style="color: white;"> Description:</label><textarea style="color: white; min-width: 100%;" class="swal2-input"> </textarea>',
        showCloseButton: true,
        focusConfirm: false,
        confirmButtonText: '<i class="fa fa-thumbs-up""></i> Great!',
        confirmButtonAriaLabel: 'Thumbs up, great!',
    })
}

function presentTamir() {
    Swal.fire({
      heightAuto: false,
      background: "url(https://images.unsplash.com/photo-1515825838458-f2a94b20105a?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=776&q=80)",
      title: '<strong style="color: white"><u>Tamir Sror</u></strong>',
      width: 800,
      html: "<h2 style='color: white'>I'm a 3rd year Computer Science Student <br> and a software developer</h2>" + 
            "<ul style='font-size: 1.4em; color: white;'>" +    
                "<li> I did a few projects similer to what is required in our course, </li>" + 
                "<li> I did a few other courses that required team work. </li>" + 
            "</ul>",
      showCloseButton: true,
      focusConfirm: false,
      confirmButtonText: '<i class="fa fa-thumbs-up""></i> Great!',
      confirmButtonAriaLabel: 'Thumbs up, great!',
    })
}

function presentYael() {
    Swal.fire({
      heightAuto: false,
      background: "url(https://images.unsplash.com/photo-1608534430161-593a93055096?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=874&q=80) center, center",
      title: '<strong style="color: white"><u>Yael Davidov</u></strong>',
      width: 800,
      html: "<h2 style='color: white'>I'm a 4rd year Computer Science Student </h2>" + 
            "<ul style='font-size: 1.2em; color: white'>" +    
                "<li> I did a few courses that are relavent to the work we are going to do such as" +
                     "java script and computer comunications. </li>" + 
                "<li> I have worked in a few teams in other courses </li>" +
            "</ul>",
      showCloseButton: true,
      focusConfirm: false,
      confirmButtonText: '<i class="fa fa-thumbs-up""></i> Great!',
      confirmButtonAriaLabel: 'Thumbs up, great!',
    })
}

function presentRon() {
    Swal.fire({
      heightAuto: false,
      background: "url(https://images.unsplash.com/photo-1635924010446-c2a9851859af?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80)",
      title: '<strong style="color: white"><u>Ron Hachmon</u></strong>',
      width: 800,
      html: "<h2 style='color: white'>I'm a 3rd year Computer Science Student</h2>",
      showCloseButton: true,
      focusConfirm: false,
      confirmButtonText: '<i class="fa fa-thumbs-up""></i> Great!',
      confirmButtonAriaLabel: 'Thumbs up, great!',
    })
}

function presentRavid() {
    Swal.fire({
      heightAuto: false,
      background: "url(https://images.unsplash.com/photo-1627661020066-166c2350cf94?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=870&q=80)",
      title: '<strong style="color: white"><u>Ravid Yael</u></strong>',
      width: 800,
      html: "<h2 style='color: white'>I'm a 2rd year Computer Science Student</h2>",
      showCloseButton: true,
      focusConfirm: false,
      confirmButtonText: '<i class="fa fa-thumbs-up""></i> Great!',
      confirmButtonAriaLabel: 'Thumbs up, great!',
    })
}

function presentYoav() {
    Swal.fire({
      heightAuto: false,
      background: "url(https://images.unsplash.com/photo-1642414392606-d6415f5a9088?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80) center, center",
      title: '<strong style="color: white"><u>Yoav Balikov</u></strong>',
      width: 800,
      html: "<h2 style='color: white;'>I'm a 3rd year Computer Science Student </h2>" +
            "<ul style='font-size: 1.2em; color: white;'>" +
                "<li> Age: 25 </li>" + 
                "<li> Skills: C, C++, Java, Java script, HTML, CSS and SQL </li>" +
            "</ul>",
      showCloseButton: true,
      focusConfirm: false,
      confirmButtonText: '<i class="fa fa-thumbs-up""></i> Great!',
      confirmButtonAriaLabel: 'Thumbs up, great!',
    })
}

function presentDan() {
    Swal.fire({
      heightAuto: false,
      background: "url(https://images.unsplash.com/photo-1638368012876-5812dd95d7cc?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=782&q=80) center, center",
      title: '<strong style="color: white"><u>Dan Inon</u></strong>',
      width: 800,
      html: "<h2 style='color: white'>I'm a 2rd year Computer Science Student</h2>",
      showCloseButton: true,
      focusConfirm: false,
      confirmButtonText: '<i class="fa fa-thumbs-up""></i> Great!',
      confirmButtonAriaLabel: 'Thumbs up, great!',
    })
}

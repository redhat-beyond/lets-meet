
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

function present(name, image_url, title, attributes) {
    list_text = ""
    
    attributes.forEach(item => {
        list_text += "<li> " + item + " </li>";
    })
        
    
    Swal.fire({
      heightAuto: false,
      background: "url(" + image_url + ")",
      title: '<strong style="color: white;"><u>' + name + '</u></strong>',
      width: 800,
      html: "<h2 style='color: white'>" + title + "</h2>" +
            "<ul style='font-size: 1.4em; color: white;'>" + list_text + "</ul>", 
      showCloseButton: true,
      focusConfirm: false,
      confirmButtonText: '<i class="fa fa-thumbs-up""></i> Great!',
      confirmButtonAriaLabel: 'Thumbs up, great!',
    })
}

function presentTamir() {
    present("Tamir Sror", "https://images.unsplash.com/photo-1515825838458-f2a94b20105a?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=776&q=80", 
           "I'm a 3rd year Computer Science Student <br> and a software developer", ["I did a few projects similar to what is required in our course.", "I did a few other courses that required teamwork."])
}

function presentYael() {
    present("Yael Davidov", "https://images.unsplash.com/photo-1608534430161-593a93055096?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=874&q=80", 
           "I'm a 4th year Computer Science Student", ["I did a few courses that are relevant to the work we are going to do such as javascript and computer communications"])
}

function presentRon() {
    present("Ron Hachmon", "https://images.unsplash.com/photo-1635924010446-c2a9851859af?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80", 
           "I'm a 3rd year Computer Science Student", [])
}

function presentRavid() {
    present("Ravid Yael", "https://images.unsplash.com/photo-1627661020066-166c2350cf94?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=870&q=80", 
           "I'm a 2rd year Computer Science Student", [])
}

function presentYoav() {
    present("Yoav Balikov", "https://images.unsplash.com/photo-1642414392606-d6415f5a9088?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80", 
           "I'm a 3rd year Computer Science Student", [])
}

function presentDan() {
    present("Dan Inon", "https://images.unsplash.com/photo-1638368012876-5812dd95d7cc?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=782&q=80", 
           "I'm a 3rd year Computer Science Student", [])
}

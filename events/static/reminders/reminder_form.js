$(document).ready(function(){
	$("#reminder_form_attribute").hide()

	$("#add_alert").click(
		function() {
			$("#reminder_form_attribute").toggle();
		}
	)
});


function delete_event(event_id) {
	Swal.fire({
        heightAuto: false,
		icon: 'warning',
		title: '<h1>Are you sure?</h1>',
		html: "<h3>You won't be able to revert this!<h3>",
		showCancelButton: true,
		confirmButtonColor: '#3085d6',
		cancelButtonColor: '#d33',
		confirmButtonText: '<h5>Yes, delete it!</h5>',
		cancelButtonText: '<h5>Cancel</h5>'
	  }).then((result) => {
		if (result.isConfirmed) {
			$.get("/event/delete_event/" + event_id, {}, function(data, status) {
				if (data.result === "success") {
					Swal.fire({
						icon: 'success',
						title: '<h1>Deleted!</h1>',
						html: '<h3>Your file has been deleted.</h3>'
					})

					document.location.href = "/main/";
				}
				else {
					Swal.fire({
						icon: 'error',
						title: '<h1>Meeting Deletion Failed</h1>',
						html: '<h3>Sorry you are not the creator of this meeting. You cant delete is.</h3>'
					})
				}
			});
		}
	  })
}

$(document).ready(function(){
	$("#reminder_form_attribute").hide()

	$("#add_alert").click(
		function() {
			$("#reminder_form_attribute").toggle();
		}
	)
});


function delete_event(event_id) {
	$.get("/event/delete_event/" + event_id, {}, function(data, status) {
		if (data.result === "success") {
			alert("yes");
		}
		else {
			alert("no");
		}
	});
}
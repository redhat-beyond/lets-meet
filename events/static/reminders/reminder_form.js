$(document).ready(function(){
	$("#reminder_form_attribute").hide()

	$("#add_alert").click(
		function() {
			$("#reminder_form_attribute").toggle();
		}
	)
});

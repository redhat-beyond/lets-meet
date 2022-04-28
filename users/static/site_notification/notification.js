let get_notification = "";
let seen_notification = "";


function build_table() {
	const id = "#notification-table";

	let header = "<tr>";
		header += "<th class='message' style='text-align: center;' colspan='3'>message</th>";
		header += "</tr>";

	$(id).empty();
	$(id).append(header);

	$.get(get_notification, {}, function(data, status) {

		$("#notification-badge").text(data.length);  // change the icon to the amount of notification

		data.forEach((element, index) => {
			let line = "<tr id=row" + String(element.id);
				line += ">";
				line += "<td class='message' colspan='2'>" + element.messages + "</td>";
				line += "<td class='remove_btn' onclick=remove_from_list('#row" + String(element.id) + "')> dismiss </td>";
				line += "</tr>";

			$(id).append(line);
		});
		
	})
}

function remove_from_list(id) {
	let notification_counter = $("#notification-badge").text() - 1;

	if (notification_counter === 0) {
		notification_counter = "";
	}

	$("#notification-badge").text(notification_counter);  // remove a notification counter
	$(id).remove();

	const url = seen_notification;
	console.log(url.slice(0, -1) + id.slice(-1));
	$.get(url.slice(0, -1) + id.slice(-1), {});           // send a seen notification to django
}

function openNav() {
	const width = "400px";
	document.getElementById("notification_bar").style.width = width;
	document.getElementById("main").style.marginRight = width;
	document.body.style.backgroundColor = "rgba(0,0,0,0.4)";
}

function closeNav() {
	document.getElementById("notification_bar").style.width = "0";
	document.getElementById("main").style.marginRight= "0";
	document.body.style.backgroundColor = "white";
}

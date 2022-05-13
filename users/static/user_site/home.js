
function set_line(current_date) {
	const d = new Date();

	date_list = current_date.split("/");
	day = date_list[0];
	month = date_list[1];
	year = date_list[2];

	if (String(year) === String(d.getFullYear()) && String(month) === String(d.getMonth() + 1) && String(day) === String(d.getDate())) {
		
		document.querySelector(".dayview-now-marker").style.visibility = "visible";
		document.querySelector(".dayview-now-marker").style.top =
		(document
			.querySelector(".dayview-gridcell-container")
			.getBoundingClientRect().height / 24) *
			(d.getHours() + d.getMinutes() / 60) + "px";
	}
	else {
		document.querySelector(".dayview-now-marker").style.top = "0px";
		document.querySelector(".dayview-now-marker").style.visibility = "hidden";
	}
}

function get_time_height(hours, minutes) {
	return Math.round((961 / 24) * (hours + minutes / 60) / 9.8);
}

function move(id) {
	document.location.href = "/event/update/" + id;
}

function day_view(date) {
	let day_events = "";
	$.get("/get_day_events/" + date, {}, function(data, status) {
		data.forEach(element => {
			let start_hour =  get_time_height(parseInt(element.start_hour), parseInt(element.start_minute));
			let end_hour =  get_time_height(parseInt(element.end_hour), parseInt(element.end_minute));

			if (start_hour === end_hour) {
				end_hour += 3;
			}

			console.log(element.date_time_start);
			console.log(element.date_time_end);

			day_events += "                        "
			day_events += '<div class="dayview-cell" style="grid-row: ' + String(start_hour) + ' / ' + String(end_hour) + '; background-color: ' + element.color + ' " onclick=move(' + element.id + ')>'
			day_events += "                        "
			day_events += '    <div class="dayview-cell-title">' + element.title + '</div>'
			day_events += "                        "
			day_events += '    <div class="dayview-cell-time"> ' + element.date_time_start + ' - ' + element.date_time_end + '</div>'
			day_events += "                        "
			day_events += '    <div class="dayview-cell-desc">' + element.description + '</div>'
			day_events += "                        "
			day_events += '</div>'
		});

		// /event/meeting/
		const html_text = 
			' <a href="/event/create/' + date + '" id="plus_link"> <i class="fa fa-plus-circle" aria-hidden="true"></i> <span class="tooltiptext">Create New Event</span></a>' +
			' <a href="/event/create/' + date + '" id="date_plus_link"> <i class="fa fa-calendar-plus-o" aria-hidden="true"></i> <span class="tooltiptext">Create New Meeting</span></a>' +
			'<div class="dayview-container">' +
			'    <div class="dayview-timestrings">' +
			'        <div class="dayview-timestrings">' +
			get_hours() +
			'        </div>' +
			'    </div>' +
			'    <div class="dayview-grid-container">' + 
			'        <div class="dayview-grid">' +
			'            <div class="dayview-grid-tiles">' +
			get_grid() +
			'            </div>' +
			'            <div class="dayview-now-marker"></div>' +
			'            <div class="dayview-grid-marker-start"></div>' +
			'            <div class="dayview-gridcell-container">' +
			'                <div class="dayview-gridcell">' +
			day_events +
			'                </div>' +
			'            </div>' +
			'            <div class="dayview-grid-marker-end"></div>' +
			'        </div>' +
			'    </div>' +
			'</div>'
		
		Swal.fire({
			title: "<strong style='color:white'><u>" + date + "</u></strong>",
			width: '40rem',
			background: "linear-gradient(#292E49, #536976)",
			html: html_text,
			showCloseButton: true,
			showConfirmButton: false,
		})

		set_line(date);
	})
}

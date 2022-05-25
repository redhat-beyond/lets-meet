
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

function delete_event(event_id) {

	Swal.fire({
        heightAuto: false,
		title: 'Are you sure?',
		text: "You won't be able to revert this!",
		icon: 'warning',
		showCancelButton: true,
		confirmButtonColor: '#3085d6',
		cancelButtonColor: '#d33',
		confirmButtonText: 'Yes, delete it!'
	  }).then((result) => {
		if (result.isConfirmed) {
			$.get("/event/delete_event/" + event_id, {}, function(data, status) {
				if (data.result === "success") {
					Swal.fire(
						'Deleted!',
						'Your file has been deleted.',
						'success'
					)

					$("#item" + String(event_id)).remove();
					$("#event" + String(event_id)).remove();
				}
				else {
					Swal.fire({
						icon: 'error',
						title: 'Meeting Deletion Failed',
						text: 'Sorry you are not the creator of this meeting. You cant delete is.'
					})
				}
			});
		}
	  })
}

function create_events(events, isOptionalDate) {
	let day_events = "";

	events.forEach(element => {
		let start_hour =  get_time_height(parseInt(element.start_hour), parseInt(element.start_minute));
		let end_hour =  get_time_height(parseInt(element.end_hour), parseInt(element.end_minute));

		if (start_hour === end_hour) {
			end_hour += 3;
		}

		day_events += "                        "
		day_events += '<div id="item' + element.id + '" class="dayview-cell" style="grid-row: ' + String(start_hour) + ' / ' + String(end_hour) + '; '

		if (isOptionalDate) {
			day_events += ' background-color: transparent; outline: 4px solid ' + element.color + '; color: black;" >';
		}
		else {
			day_events += 'background-color: ' + element.color + ' " >';
		}

		day_events += "                        "
		day_events += '    <div id="event_title" class="dayview-cell-title" onclick=move(' + element.id + ')>' + element.title + '</div>'
		day_events += "                        "
		day_events += '    <div id="event_date" class="dayview-cell-time" onclick=move(' + element.id + ')> ' + element.date_time_start + ' - ' + element.date_time_end + '</div>'

		if (!isOptionalDate) {
			day_events += '    <div class="dayview-cell-time" style="padding-left: 5px;"> <i class="fa fa-trash-o" aria-hidden="true" id="delete_event" onclick="delete_event(' + element.id + ')"></i></div>'
		}

		day_events += "                        "
		day_events += '    <div class="dayview-cell-desc">' + element.description + '</div>'
		day_events += "                        "
		day_events += '</div>'
	});

	return day_events;
}

function day_view(date) {
	$.get("/get_day_events/" + date, {}, function(data, status) {
		let day_events = create_events(data["events"], false);
		let day_meetings = create_events(data["meetings"], false);
		let day_optional_dates = create_events(data["optional_dates"], true);

		const html_text = 
			' <a href="/event/create/' + date + '" id="plus_link"><i class="fa fa-plus-circle" aria-hidden="true"></i></a>' +
			' <a href="/event/meeting/' + date + '" id="date_plus_link"><i class="fa fa-calendar-plus-o" aria-hidden="true"></i></a>' +
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
			day_meetings +
			day_optional_dates +
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

		tippy('#plus_link', {
			content: 'Create New Event',
		});
		tippy('#date_plus_link', {
			content: 'Create New Meeting',
		});
		tippy('#delete_event', {
			content: 'Delete Event',
		});
		tippy('#event_title', {
			content: 'Edit Event',
		});
		tippy('#event_date', {
			content: 'Edit Event',
		});
	})
}

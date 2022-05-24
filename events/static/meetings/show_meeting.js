let index = 0;
let existent_participants_length = 0;
let show_meeting_url = "";
let delete_participant_url = "";
let token = "";
let add_participant_url = "";

function delete_participant(id, username) {
    $.get(delete_participant_url.slice(0, -1) + id, {}, function(data, status) {
        if (data.result === "success") {
            Swal.fire({
                icon: 'success',
                title: '<h1>Deleted!</h1>',
                html: '<h3>' + username + ' has been deleted.</h3>'
            })

        }
        else {
            Swal.fire({
                icon: 'error',
                title: '<h1>Meeting Participant Deletion Failed</h1>',
                html: '<h3>' + data.result +'</h3>'
            })
        }
    })
}

function add_participant_row() {

    if (existent_participants_length + index < 10) {
        const id = "form-" + index;
        let participant_row =  "<div class='par' id=" + id +">";
            participant_row += "        <table style='width: 100%;'>";
            participant_row += "            <tr id='tr" + index + "'>";
            participant_row += "                <td><input type='email' placeholder='Participant email' class='participant_email' name='participants-" + index + "-participant_email' id='id_participants-" + index + "-participant_email'></td>";
            participant_row += "                <td id='del_btn" + index + "'><i class='fa fa-times close_btn' aria-hidden='true' onclick='remove_participant_row(" + index + ")'></i></td>";
            participant_row += "            </tr>";
            participant_row += "        </table>";
            participant_row += "</div>";

        $("#save").before(participant_row);
        index++;
        $("#id_participants-TOTAL_FORMS").val(index);

        $("#save").show();

    }
}

function remove_participant_row(row_index) {

    $("#form-" + row_index).remove();

    if (index === 1) {
        $("#save").hide();
    }

    for (let i = row_index; i < index; i++) {
        if (i != 0) {
            $("#form-" + i).attr('id', 'form-' + (i - 1));
            $("#del_btn" + i).remove();
            $('#tr' + i).append("            <td id='del_btn" + (i - 1) + "'><i class='fa fa-times close_btn' aria-hidden='true' onclick='remove_participant_row(" + (i - 1) + ")'></i></td>");
            $("#tr" + i).attr('id', 'tr' + (i - 1));
            $("#id_participants-" + i + "-participant_email").attr('id', 'id_participants-' + (i - 1) +  '-participant_email').attr('name', 'participants-' + (i - 1) +  '-participant_email');
        }
    }

    index --;
    $("#id_participants-TOTAL_FORMS").val(index);
}

function get_rows(data, is_creator) {
    let rows = "<div class='meeting_participants'>";
    existent_participants_length = data.length;
    data.forEach(element => {
        let row =  "<div class='par'>";
            row += "    <table class='participants' id='" + element.id + "'>";
            row += "        <tr>";
            row += "            <td colspan='2' style='font-weight: bold;'>" +  element.user_id__username + "</td>";

            if (is_creator) {
                row += "            <td rowspan='3'><i class='fa fa-times close_btn' aria-hidden='true' onclick='delete_participant(" + element.id + ", \"" + element.user_id__username +"\")'></i></td>";
            }

            row += "        </tr>";
            row += "        <tr>";
            row += "            <td width=70%>" + element.user_id__email + "</td>";

            if (element.user_id__phone_number !== null) {
                row += "            <td width=25%>" + element.user_id__phone_number + "</td>";
            }

            row += "        </tr>";
            row += "    </table>";
            row += "</div>";

        rows += row;
    })
    rows += "</div>";

    return rows;
}

function show_participants(is_creator) {

    $.get(show_meeting_url, {}, function(data, status) {
        index = 0;
        let html_text =  get_rows(data, is_creator);
        let add_btn = "<div id='meeting-participants-form-list' class='new_participants'>";
            add_btn += "    <form method='POST' id='participant_form' action='" + add_participant_url + "'>";
            add_btn += '        ' + token;
            add_btn += "        <input type='hidden' name='participants-TOTAL_FORMS' value='0' id='id_participants-TOTAL_FORMS'>";
            add_btn += "        <input type='hidden' name='participants-INITIAL_FORMS' value='0' id='id_participants-INITIAL_FORMS'>";
            add_btn += "        <input type='hidden' name='participants-MIN_NUM_FORMS' value='0' id='id_participants-MIN_NUM_FORMS'>";
            add_btn += "        <input type='hidden' name='participants-MAX_NUM_FORMS' value='10' id='id_participants-MAX_NUM_FORMS'>";
            add_btn += "        <input type='submit' id='save' class='save_btn' name='submit' value='Save' />";
            add_btn += "    </form>";
            add_btn += "</div>";
            add_btn += "<div style='position: absolute; top: 30px; left: 30px;'>";
            add_btn += "  <i class='fa fa-plus-circle plus_btn' aria-hidden='true' onclick='add_participant_row()' id='add'></i>";
            add_btn += "</div>";

        if (is_creator) {
            html_text += add_btn;
        }

        Swal.fire({
            title: "<h1 style='font-size: 2.5rem; color: black;'>Meeting Participants</h1>",
            html: html_text,
            closeButtonHtml: '<div style="font-weight: bold; color: black; font-size: 25px;">&times;</div>',
            width: "700px",
            background: "linear-gradient(#fff, #0575E6)",
            showCloseButton: true,
            showConfirmButton: false,
        })


        $("#save").hide();
    })
}

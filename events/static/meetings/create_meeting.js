let total_meeting_dates_forms;
let total_participant_forms;
const addMoreOptionalDatesBtn = document.getElementById('add-more-optional-meeting-dates')
addMoreOptionalDatesBtn.addEventListener('click', add_optional_meeting_dates_form)
const addMoreBtn = document.getElementById('add-more-meeting-participants')
addMoreBtn.addEventListener('click', add_participant_form)


function add_optional_meeting_dates_form(event) {
    if(event){
        event.preventDefault()
    }
    add_form('optional-meeting-dates', 'optional_meetings')
}

function add_participant_form(event) {
    if(event){
        event.preventDefault()
    }
    add_form('meeting-participants', 'participants')
}

function add_form(form_name, form_prefix){
    const totalNewFroms = document.getElementById(`id_${form_prefix}-TOTAL_FORMS`)
    if(totalNewFroms.getAttribute('value') == 10){
        return 
    }
    const currentForms= document.getElementsByClassName(`${form_name}-form`)
    const currentFormCount = currentForms.length
    const formList = document.getElementById(`${form_name}-form-list`)
    const copyEmptyFormElement = document.getElementById(`empty-${form_name}-form`).cloneNode(true)
    copyEmptyFormElement.setAttribute('class', `${form_name}-form`)
    copyEmptyFormElement.setAttribute('id', `form-${currentFormCount}`)
    const regex = new RegExp('__prefix__', 'g')
    copyEmptyFormElement.innerHTML = copyEmptyFormElement.innerHTML.replace(regex, currentFormCount)
    totalNewFroms.setAttribute('value', currentFormCount + 1)
    formList.append(copyEmptyFormElement)
}

function set_total_meeting_forms() {
    const totalNewOptionalDatesFroms = document.getElementById('id_optional_meetings-TOTAL_FORMS')
    totalNewOptionalDatesFroms.setAttribute('value', total_meeting_dates_forms)
}

function set_total_participant_forms() {
    const totalNewParticipantFroms = document.getElementById('id_participants-TOTAL_FORMS')
    totalNewParticipantFroms.setAttribute('value', total_participant_forms)
}

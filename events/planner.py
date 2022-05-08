from email import message
from events.models import OptionalMeetingDates, PossibleParticipant, Event, EventParticipant
from main.utilities import send_mail_notification
from reminders.models import Reminder, ReminderType


class EventPlanner():

    def __init__(self, event_id):
        self.participants_ids_that_can_meet = []
        self.participants_ids_that_can_not_meet = []
        self.all_meeting_participants = EventParticipant.objects.get_an_event_participants_without_creator(event_id)

    def update_which_participants_can_and_cant_meet(self, chosen_meeting):
        self.participants_ids_that_can_meet = PossibleParticipant.objects.get_all_date_participants(chosen_meeting)
        self.participants_ids_that_can_not_meet = list(set(self.all_meeting_participants).difference(self.participants_ids_that_can_meet))

    def find_meeting(self, event_id):
        """ Find a meeting date with all the participants if possible.
            The planner will look over all the possible dates and
            will check if there is a possible date that works for everyone
        """

        chosen_meeting = None
        """ maybe we can use get_all_possible_participants and convert the returning string to set
        instead of creating new query set as "get_all_possible_participants_of_event" in line 23 """
        participants_ids_that_can_meet = PossibleParticipant.objects.get_all_possible_participants_of_event(event_id)
        for possible_date in OptionalMeetingDates.objects.get_all_event_dates(event_id):
            participants_amount = PossibleParticipant.objects.get_all_date_participants(possible_date).count()
            if participants_ids_that_can_meet.count() == participants_amount:
                chosen_meeting = possible_date
                break

        # There is no perfect meeting available, Plan B then
        # Find the meeting with the least unavailable participant possible

        if not chosen_meeting:
            meeting_with_max_participants = None
            max_participant_meeting = None

            for possible_date in OptionalMeetingDates.objects.get_all_event_dates(event_id):
                participants_amount = PossibleParticipant.objects.get_all_date_participants(possible_date).count()
                if not max_participant_meeting or max_participant_meeting < participants_amount:
                    max_participant_meeting = participants_amount
                    meeting_with_max_participants = possible_date

            chosen_meeting = meeting_with_max_participants
        self.update_which_participants_can_and_cant_meet(chosen_meeting)
        return chosen_meeting

    def execute_choice(self, chosen_meeting):
        """ after a specific event has been selected
            remove all possible meeting,
            remove all possible participant for each date,
            remove all event participant that not take part in the event,
            change the event date and time to the chosen meeting
        """
        event_id = chosen_meeting.event_creator_id.event_id.id  # get the event id
        original_event = Event.objects.get(id=event_id)         # get the original event object

        # change the date of the event using the chosen meeting dates
        original_event.date_time_start = chosen_meeting.date_time_start
        original_event.date_time_end = chosen_meeting.date_time_end
        original_event.save()
        PossibleParticipant.objects.remove_all_event_participants(event_id)
        OptionalMeetingDates.objects.remove_all_possible_dates(event_id)

        # Delete all participants who do not take part in the meeting
        for participant in self.participants_ids_that_can_not_meet:
            EventParticipant.objects.remove_participant_from_event(event_id, participant.user_id)

    def run(self, event):
        """ run the planner in an event.
            Find the best possible date for the meeting,
            then excute the choice and change the DB rows accordingly.
        """
        chosen_meeting = self.find_meeting(event)

        if not chosen_meeting:
            return None  # return an exception-> "someting went wrong"
        else:
            self.execute_choice(chosen_meeting)

    @staticmethod
    def send_timeout_voting_notification_email_for_participats():
        pass

    @staticmethod
    def send_email_about_algorithm_results_to_the_creator():
        pass

    @staticmethod
    def calc_last_notifiction(voting_timeout):
        return None

    @staticmethod
    def creating_meeting_reminders(meeting_creator, voting_timeout, meeting_id): # how do we save the meeting id
        # this function will be call from the view of the meeting, after all the validation have paased
        last_notification_time = EventPlanner.calc_last_notifiction(voting_timeout)
        Reminder(
            participant_id=meeting_creator, datetime=voting_timeout,
            method=ReminderType.ALGORITHM_RESULTS
        ).save()
        Reminder(
            participant_id=meeting_creator, datetime=last_notification_time,
            method=ReminderType.EXPIRATION_VOTING_TIME
        ).save()
        Reminder(
            participant_id=meeting_creator, datetime=voting_timeout,
            method=ReminderType.MEETING_VOTE
        ).save()


# i think we should save somewhere the event_id in the reminder,
# so we could know which participants belong to this meeting

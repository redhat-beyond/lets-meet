import email
from functools import reduce
from django.utils import timezone
from datetime import datetime, timedelta
from reminders.models import Reminder, ReminderType
from events.models import OptionalMeetingDates, PossibleParticipant, Event, EventParticipant
from main.utilities import send_mail_notification, time_format, create_notification


class EventPlanner():

    def __init__(self, event_id):
        self.event_id = event_id
        self.chosen_meeting = None
        self.participants_ids_that_can_meet = []
        self.participants_ids_that_can_not_meet = []
        self.all_meeting_participants = EventParticipant.objects.get_an_event_participants_without_creator(self.event_id)

    def update_which_participants_can_and_cant_meet(self, chosen_meeting):
        self.participants_ids_that_can_meet = PossibleParticipant.objects.get_all_date_participants(chosen_meeting)
        self.participants_ids_that_can_not_meet = list(set(self.all_meeting_participants).difference(self.participants_ids_that_can_meet))

    def find_meeting(self):
        """ Find a meeting date with all the participants if possible.
            The planner will look over all the possible dates and
            will check if there is a possible date that works for everyone
        """

        chosen_meeting = None
        participants_ids_that_can_meet = PossibleParticipant.objects.get_all_possible_participants_of_event(self.event_id)
        for possible_date in OptionalMeetingDates.objects.get_all_event_dates(self.event_id):
            participants_amount = PossibleParticipant.objects.get_all_date_participants(possible_date).count()
            if participants_ids_that_can_meet.count() == participants_amount:
                chosen_meeting = possible_date
                break

        # There is no perfect meeting available, Plan B then
        # Find the meeting with the least unavailable participant possible

        if not chosen_meeting:
            meeting_with_max_participants = None
            max_participant_meeting = None

            for possible_date in OptionalMeetingDates.objects.get_all_event_dates(self.event_id):
                participants_amount = PossibleParticipant.objects.get_all_date_participants(possible_date).count()
                if not max_participant_meeting or max_participant_meeting < participants_amount:
                    max_participant_meeting = participants_amount
                    meeting_with_max_participants = possible_date

            chosen_meeting = meeting_with_max_participants
        self.update_which_participants_can_and_cant_meet(chosen_meeting)
        return chosen_meeting

    def execute_choice(self):
        """ after a specific event has been selected
            remove all possible meeting,
            remove all possible participant for each date,
            remove all event participant that not take part in the event,
            change the event date and time to the chosen meeting
        """
        event_id = self.chosen_meeting.event_creator_id.event_id.id  # get the event id
        original_event = Event.objects.get(id=event_id)              # get the original event object

        # change the date of the event using the chosen meeting dates
        original_event.date_time_start = self.chosen_meeting.date_time_start
        original_event.date_time_end = self.chosen_meeting.date_time_end
        original_event.save()
        PossibleParticipant.objects.remove_all_event_participants(event_id)
        OptionalMeetingDates.objects.remove_all_possible_dates(event_id)

        # Delete all participants who do not take part in the meeting
        for participant in self.participants_ids_that_can_not_meet:
            EventParticipant.objects.remove_participant_from_event(event_id, participant.user_id)

    def run(self):
        """ run the planner in an event.
            Find the best possible date for the meeting,
            then excute the choice and change the DB rows accordingly.
        """
        self.chosen_meeting = self.find_meeting(self.event_id)

        if not self.chosen_meeting:
            print(" in run method-> meeting not found")
            self.send_email_no_suitable_meeting_found(EventParticipant.objects.get_creator_of_event(self.event_id))
        else:
            self.execute_choice()
            self.send_email_about_algorithm_results_to_the_creator()

    def send_email_about_algorithm_results_to_the_creator(self):
        meeting_creator_id = EventParticipant.objects.get_creator_of_event(self.chosen_meeting)
        email_title = f"Meeting {self.chosen_meeting.title} results"
        message = self.get_message(self.chosen_meeting, meeting_creator_id)
        send_mail_notification(email_title, message, meeting_creator_id.user_id)

    @staticmethod    
    def send_email_no_suitable_meeting_found(creator_id):
        email_title = "No suitable meeting found"
        message = "Unfortunately, no participant voted for the meeting and therefore no suitable meeting was found."
        send_mail_notification(email_title, message, creator_id)

    @staticmethod
    def send_timeout_voting_notification_email_for_participants(message, meeting_creator_id):
        meeting_id = meeting_creator_id.event_id
        all_possible_meetings = OptionalMeetingDates.objects.get_all_event_dates(meeting_id)
        all_meeting_participants = EventParticipant.objects.get_an_event_participants_without_creator(meeting_id)
        email_title = "Voting for a meeting is about to end"
        message = (f"The voting for the event {meeting_id.title} is about to end.\n"
                   "Please finish your vote.\n"
                   "If you did not vote for the meeting, you will not be able to attend.")
        for participant in all_meeting_participants:
            # if PossibleParticipant.objects.did_user_vote(all_possible_meetings, participant.user_id):
            send_mail_notification(email_title, message, participant.user_id)
            create_notification(message, participant.user_id)

    def get_message(self, meeting_id, meeting_creator_id):
        participants_who_can_meet = "\n".join(
            [participant.user_id.username for participant in self.participants_ids_that_can_meet]
        )
        participants_who_cant_meet = "\n".join(
            [participant.user_id.username for participant in self.participants_ids_that_can_not_meet]
        )
        message = (f"Hi {meeting_creator_id.user_id.username}! The meeting results are here!!!"
                   f"Meeting title: {meeting_id.title}\n"
                   f"Meeting description: {meeting_id.description}\n" if meeting_id.description != "" else ""
                   f"Meeting location: {meeting_id.location}\n" if meeting_id.location != "" else ""
                   "The chosen meeting date is:\n"
                   f"Strting date: {time_format(meeting_id.date_time_start)}\n"
                   f"Ending date: {time_format(meeting_id.date_time_end)}\n"
                   "The participant that will take part in the meeting:\n"
                   f"{participants_who_can_meet}\n"
                   "The participant that will not take part in the meeting:\n"
                   f"{participants_who_cant_meet}\n")
        return message

    @staticmethod
    def calc_last_notification(voting_timeout):
        # minutes_before_timeout = 15
        # return voting_timeout - timedelta(minutes=minutes_before_timeout)
        minutes_before_timeout = 2
        return voting_timeout - timedelta(minutes=minutes_before_timeout)

    @staticmethod
    def get_timeout(meeting_id):
        def get_max_datetime(datetime1, datetime2):
            if datetime1.date_time_start < datetime2.date_time_start:
                return datetime1
            return datetime2

        possible_dates = OptionalMeetingDates.objects.get_all_event_dates(meeting_id)
        min_possible_date = reduce(get_max_datetime, possible_dates)
        difference = min_possible_date.date_time_start.timestamp() - datetime.now().timestamp()
        print(datetime.fromtimestamp(datetime.now().timestamp() + (difference / 2.0)).replace(tzinfo=timezone.utc))
        return datetime.fromtimestamp(datetime.now().timestamp() + (difference / 2.0)).replace(tzinfo=timezone.utc)

    @staticmethod
    def get_timeout_message(voting_timeout):
        print(" in get_timeout_message: ", (voting_timeout.strftime("%Y-%m-%d %H:%M:%S")))
        time = (voting_timeout.strftime("%Y-%m-%d %H:%M:%S"))
        return ("The meeting has been cerated successfully.\n"
                "A voting email for the meeting was sent to all participants.\n"
                f"Results about the meeting will be sent to you by email on\n{time}")

    @staticmethod
    def send_invite_notification(meeting_id):
        """ send an invite notification using the site notification to all  """
        message = "You have a new meeting"
        all_event_participants = EventParticipant.objects.get_an_event_participants_without_creator(meeting_id)

        for participant in all_event_participants:
            create_notification(message, participant)

    @staticmethod
    def send_meeting_invitation_email_to_participants(meeting_id, meeting_creator):
        email_title = "Invitation to meeting"
        message = (f"You have been invited to attend a meeting created by {meeting_creator.user_id.username}!\n"
                   f"The meeting topic: {meeting_id.title}\n"
                   f"Description: {meeting_id.description}\n" if meeting_id.description != "" else ""
                   "A notice on the website is waiting for you to vote to set a meeting date.")
        all_meeting_participants = EventParticipant.objects.get_an_event_participants_without_creator(meeting_id)
        for participant in all_meeting_participants:
            send_mail_notification(email_title, message, participant.user_id)

    @staticmethod
    def creating_meeting_reminders(meeting_creator, voting_timeout):
        # this function will be call from the view of the meeting, after all the validation have passed
        last_notification_time = EventPlanner.calc_last_notification(voting_timeout)
        Reminder(
            participant_id=meeting_creator, date_time=last_notification_time,
            method=ReminderType.EXPIRATION_VOTING_TIME
        ).save()
        Reminder(
            participant_id=meeting_creator, date_time=voting_timeout,
            method=ReminderType.RUN_ALGORITHM
        ).save()

    @staticmethod
    def invoke_meeting_algorithm(message, meeting_creator_id):
        """ invokes run method of EventPlanner """
        print(" <---in invoke algorithm---> ")
        EventPlanner(meeting_creator_id.event_id).run()

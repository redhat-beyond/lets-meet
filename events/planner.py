from events.models import OptionalMeetingDates, PossibleParticipant, Event


class EventPlanner():

    def run(self, event):
        """ run the planner in an event.
            Find the best possible date for the meeting,
            then excute the choice and change the DB rows accordingly.
        """
        meetings_possibilities = self.find_meeting(event)

        if len(meetings_possibilities) >= 1:
            self.execute_choice(meetings_possibilities[0])

    def find_meeting(self, event_id):
        """ Find a meeting date with all the participants if possible.
            The planner will look over all the possible dates and
            will check if there is a possible date that works for everyone
        """
        results = list()
        all_participants = PossibleParticipant.objects.get_all_possible_participants_count(event_id)
        for possible_date in OptionalMeetingDates.objects.get_all_event_dates(event_id):
            participants_amount = PossibleParticipant.objects.get_all_date_participants(possible_date).count()
            if all_participants == participants_amount:
                results.append(possible_date)
        return results

    def execute_choice(self, chosen_meeting):
        """ after a specific event has been selected
            remove all possible meeting,
            remove all possible participant for each date,
            change the event date and time to the chosen meeting
        """
        event_id = chosen_meeting.event_creator_id.event_id.id  # get the event id
        original_event = Event.objects.get(id=event_id)       # get the original event object

        # change the date of the event using the chosen meeting dates
        original_event.date_time_start = chosen_meeting.date_time_start
        original_event.date_time_end = chosen_meeting.date_time_end
        original_event.save()
        PossibleParticipant.objects.remove_all_event_participants(event_id)
        OptionalMeetingDates.objects.remove_all_possible_dates(event_id)

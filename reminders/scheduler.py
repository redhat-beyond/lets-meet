import logging
from sys import stdout
from datetime import datetime
from threading import Timer, Thread
from django.dispatch import receiver
from events.planner import EventPlanner
from reminders.models import Reminder, ReminderType
from main.utilities import send_reminder_email, create_notification
from django.db.models.signals import post_save, pre_delete, post_delete


class UserAlertScheduler():
    """
    User Alert Scheduler is our implementation of a reminder scheduler when the user wants to be
    notified at a specific time.

    The User Alert Scheduler is dependent on the DB and registered to save and delete events,
    - When the user adds a new reminder the scheduler will add the new reminder if his time is lower
      than the time in the current reminder.
    - When the user deletes a reminder the scheduler will change his current reminder if it was
      the same reminder and schedule the next reminder in line.

    ** Because the scheduler is only relevant when there is an action in the DB and will not be called
       from outside of the class, each method defined is private and static.
       In addition this is a Singleton object and will be created once at the start of the reminder app.

    The current methods which the scheduler support are reminder_email and send_site_notification.
    Other functions can be added to the _get_function method that takes an enum
    ReminderType is defined in the Reminder model.
    Each function needs to be as follows: function_name(message, <user>).
    <user> is the user model defined in our User model.

    This scheduler also has a logger object, because it is a complicated implementation there can be a lot
    of errors and missed calls, so a logger has been placed with info and debug calls.
    """

    __logger = None              # the logger object of the class
    __instance = None            # the instance of the class
    __current_timer = None       # the current reminder timer the scheduler is running
    __current_reminder = None    # the current reminder the scheduler is working on

    def __new__(self):
        """
        __new__ is used because we want to make the scheduler a singletone
        there is an __instance object and it is checked every time if it has been initialized
        if so the __instance will be returned otherwise this is the first time and it will be initialized
        """

        if not UserAlertScheduler.__instance:
            UserAlertScheduler.__logger = self.define_logger()

            UserAlertScheduler.__logger.debug("creating a new instance of UserAlertScheduler")
            UserAlertScheduler.__instance = super(UserAlertScheduler, self).__new__(self)

        return UserAlertScheduler.__instance

    @staticmethod
    def define_logger(file=stdout, log_level=logging.WARNING):
        """ define the __logger object.
            file: where the logger will log all his message. default is stdout
            logger level: define which types of logger message will show up. default Warning """

        log_format = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filemode=file, level=log_level, format=log_format)
        return logging.getLogger(__name__)

    @staticmethod
    def __clean_up(self):
        """ remove late reminders.
            Each reminder that has been scheduled is deleted at the end of the action
            if there are reminders that the scheduler didn't schedule before his initialization
            then they are a late reminders, reminders that should have been scheduled but
            there time has passed, in this case the schedule will delete them all """

        UserAlertScheduler.__logger.info("in clean up")

        for reminder in Reminder.objects.order_by('date_time'):

            # check each reminder time against the current time

            if UserAlertScheduler.__get_time_difference(reminder.date_time) < 0:
                Reminder.objects.get(id=reminder.id).delete()

    @staticmethod
    def __get_time_difference(date_time):
        """ return the time difference between the given date_time to our current time """

        return date_time.timestamp() - datetime.now().timestamp()

    @staticmethod
    def _get_args(reminder):
        """ get the date time, message, method type and user id from the reminder object """

        message = reminder.messages
        method_type = reminder.method
        date_time = reminder.date_time
        user_id = reminder.participant_id

        return date_time, message, method_type, user_id

    @staticmethod
    def _get_function(method_type):
        """ get the functions to invoke using the method type given """

        function_to_invoke = list()

        if method_type in (ReminderType.EMAIL, ReminderType.WEBSITE_EMAIL):
            function_to_invoke.append(send_reminder_email)

        if method_type in (ReminderType.WEBSITE, ReminderType.WEBSITE_EMAIL):
            function_to_invoke.append(create_notification)

        if method_type == ReminderType.RUN_ALGORITHM:
            function_to_invoke.append(EventPlanner.invoke_meeting_algorithm)

        if method_type == ReminderType.EXPIRATION_VOTING_TIME:
            function_to_invoke.append(EventPlanner.send_timeout_voting_notification_email_for_participants)

        return function_to_invoke

    @staticmethod
    def __add_alert(reminder=None):
        """ add a new alert.
            the schedule will check against his current reminder if the reminder
            given has a better time then his own, if so the scheduler will stop
            the timer and replace the current reminder with the newly given reminder.

            reminder: a reminder object as defined in the Reminder model,
                      if nothing is given as the reminder object then
                      the reminder will be selected as the minimum date_time of all reminders """

        UserAlertScheduler.__logger.info("in add alert.")
        UserAlertScheduler.__logger.debug(f"reminder value in: {reminder}")

        # the reminder given is None, get the next reminder from the DB using the date_time field
        if not reminder:
            reminder = Reminder.objects.get_next_reminder()

            UserAlertScheduler.__logger.debug(f"reminder value after if: {reminder}")

            if not reminder:  # the DB is empty, end the function
                UserAlertScheduler.__logger.debug("The DB is empty, there isn't a task waiting.")
                return None

        # get all the arguments from the reminder object
        _, message, method_type, user_id = UserAlertScheduler._get_args(reminder)
        functions = UserAlertScheduler._get_function(method_type)

        UserAlertScheduler.__current_reminder = reminder

        # start a new daemon thread for setting the current timer with the new reminder arguments
        if UserAlertScheduler.__current_timer is not None and UserAlertScheduler.__current_timer.is_alive():
            UserAlertScheduler.__current_timer.cancel()

        Thread(target=UserAlertScheduler.__create_timer, args=(functions, message, user_id), daemon=True).start()

        UserAlertScheduler.__logger.debug((
            "new Timer has been started. ",
            f"message: {message} - {user_id} - {UserAlertScheduler.__current_reminder.date_time}"
        ))

    @staticmethod
    def __create_timer(functions, message, user_id):
        """ create the timer object.
            The scheduler needs a timer object that will go off when a specific time has been reached
            "Timer" is a class defined in Python's own threading library that gets a time and a method to invoke.
            This function set the current timer to be a new timer object with
                time: the difference of the reminder time and the current time
                target: the function given using the _get_function class
                args: the argument that the function gets, a message and the user_id object

            ** this function is run using a different thread because the timer itself
               can cause a few problems with the migrate and the current thread running it.
        """

        UserAlertScheduler.__current_timer = Timer(
            UserAlertScheduler.__get_time_difference(UserAlertScheduler.__current_reminder.date_time),
            UserAlertScheduler.__alert_user,
            args=(functions, message, user_id)
        )
        UserAlertScheduler.__current_timer.start()  # start the timer object

    @staticmethod
    def __remove_alert(reminder_id):
        """ remove the reminder with a reminder_id from the queue.
            The scheduler will check if the reminder given is the current reminder
            if so the scheduler will remove it and the current timer,
            and will set a new reminder with its own timer according to the add_alert function
        """

        UserAlertScheduler.__logger.info("in remove alert")

        if UserAlertScheduler.__current_reminder:

            if UserAlertScheduler.__current_reminder.id == reminder_id:

                if UserAlertScheduler.__current_timer:
                    if UserAlertScheduler.__current_timer.is_alive():  # check if the timer is still running
                        UserAlertScheduler.__current_timer.cancel()
                        UserAlertScheduler.__current_reminder = None
                        UserAlertScheduler.__current_timer = None

                        UserAlertScheduler.__logger.debug(
                            f"removed the current reminder. last reminder: {Reminder.objects.get(id=reminder_id)}"
                        )
                    else:
                        UserAlertScheduler.__logger.warning(
                            (f"the reminder {UserAlertScheduler.__current_reminder}"
                             " is the current reminder but has no timer")
                        )

    @staticmethod
    def __modifie_alert(reminder):
        """ modifie the reminder in the queue.
            The scheduler will check if the given reminder is the current reminder object
                if so the scheduler will check if the time has been changed,
                if the time has been increased then the scheduler will try to add a new reminder instead
                otherwise, the remainder will be changed in the scheduler to the reminder object given
        """

        UserAlertScheduler.__logger.info("in modifie alert")

        if reminder != UserAlertScheduler.__current_reminder:
            UserAlertScheduler.__logger.debug(
                f"The two reminders are not the same.\n{UserAlertScheduler.__current_reminder} vs {reminder}"
            )

            next_reminder = None

            if reminder.date_time < UserAlertScheduler.__current_reminder.date_time:
                next_reminder = reminder

            UserAlertScheduler.__logger.debug(f"a new reminder is added: {next_reminder}")

        else:
            UserAlertScheduler.__current_reminder = reminder

            UserAlertScheduler.__logger.debug(f"the current reminder has been modified: {reminder}")

    @staticmethod
    def __alert_user(methods, *args, **kwargs):
        """ alert the user when the time of the reminder has been reached.

            methods: the functions to invoke
            other arguments: such as message and user_id """

        UserAlertScheduler.__logger.info("in alert user")

        UserAlertScheduler.__logger.debug("starting to loop over all the functions")
        UserAlertScheduler.__logger.debug(f"args: {args} || kwargs: {kwargs}")

        try:
            for method in methods:
                method(*args, **kwargs)
        except Exception as error:
            UserAlertScheduler.__logger.warning(
                f"Exception happend when executing method of {UserAlertScheduler.method}\n {error}"
            )

        # Potential Send Signal - a signal can be sent for alerting that the timer has ended

        UserAlertScheduler.__logger.debug("deleting the current task from the DB.")

        # remove the current reminder from the db
        current_reminder_instance = Reminder.objects.get(id=UserAlertScheduler.__current_reminder.id)

        if current_reminder_instance:
            current_reminder_instance.delete()

    @staticmethod
    @receiver(post_save, sender=Reminder)
    def __check_after_saving(sender, instance, **kwargs):
        """ add a new alert.
            The scheduler will check if the current reminder object has been set
            - if not then the scheduler will call add an alert
            - otherwise the instance (reminder) will be checked if it is the current reminder
              if so the user has changed something in the reminder as a result the scheduler
              will call modify alert instead.

            ** this is a function that implements the signal post save
               as a result this function takes the arguments sender, instance, **kwargs exactly
               without change in the names or order of the variables,
               any changes can cause an exception.
        """

        UserAlertScheduler.__logger.info("in check after saving")
        UserAlertScheduler.__logger.debug("post save")
        UserAlertScheduler.__logger.debug(f"instance: {instance}")

        if UserAlertScheduler.__current_reminder:
            if UserAlertScheduler.__current_reminder.id == instance.id:
                UserAlertScheduler.__logger.debug(
                    f"the reminder has been changed: {UserAlertScheduler.__current_reminder} vs {instance}"
                )
                UserAlertScheduler.__modifie_alert(instance)

            elif UserAlertScheduler.__current_reminder.date_time < instance.date_time:
                UserAlertScheduler.__logger.debug("end post: the timer time hasn't been changed")
                return None

        UserAlertScheduler.__logger.debug(f"set new alert: {instance}")

        UserAlertScheduler.__add_alert(instance)

    @staticmethod
    @receiver(pre_delete, sender=Reminder)
    def __check_before_delete(sender, instance, **kwargs):
        """ remove the alert from the queue.
            The scheduler will call remove alert to check if the instance (reminder)
            is in fact the current reminder, and will schedule a new reminder if need be.

            ** this is a function that implements the signal pre delete
               as a result this function takes the arguments sender, instance, **kwargs exactly
               without change in the names or order of the variables,
               any changes can cause an exception.
        """

        UserAlertScheduler.__logger.info("in check before delete")
        UserAlertScheduler.__logger.debug("pre delete")

        UserAlertScheduler.__logger.debug(f"removing the reminder: {instance}")
        UserAlertScheduler.__remove_alert(instance.id)

    @staticmethod
    @receiver(post_delete, sender=Reminder)
    def __check_after_delete(sender, instance, **kwargs):
        """ set a new reminder if the current reminder is None

            The scheduler delete each reminder at the end of his time
            as a result a pre delete signal is being called, the scheduler check
            that the reminder is the current reminder and set it to None
            Then the post delete signal is called and the scheduler will schedule a new reminder
            after the deletion of the last reminder.

            ** this is a function that implements the signal pre save
               as a result this function takes the arguments sender, instance, **kwargs exactly
               without change in the names or order of the variables,
               any changes can cause an exception.
        """

        UserAlertScheduler.__logger.info("in check after delete")
        UserAlertScheduler.__logger.debug("post delete")

        if not UserAlertScheduler.__current_reminder:
            UserAlertScheduler.__logger.debug(
                "current task and current timer are None, the last reminder has been deleted."
            )
            UserAlertScheduler.__logger.debug("search a new reminder to insert")

            UserAlertScheduler.__add_alert()

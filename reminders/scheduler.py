import sys
import logging
from datetime import datetime
from threading import Timer, Thread
from django.dispatch import receiver
from main.utilities import mail, notifie
from reminders.models import Reminder, ReminderType
from django.db.models.signals import pre_save, pre_delete, post_delete


class UserAlertScheduler():

    __logger = None
    __instance = None
    __current_task = None
    __current_timer = None

    def __new__(self):
        if UserAlertScheduler.__instance is None:
            UserAlertScheduler.__logger = self.define_logger()

            UserAlertScheduler.__logger.debug("creating a new instance of UserAlertScheduler")
            UserAlertScheduler.__instance = super(UserAlertScheduler, self).__new__(self)

        return UserAlertScheduler.__instance

    @staticmethod
    def define_logger():
        log_format = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filemode=sys.stdout, level=logging.WARNING, format=log_format)
        return logging.getLogger(__name__)

    def add_alert(self, reminder):
        self.__add_alert(reminder)

    def remove_alert(self, reminder):
        self.__remove_alert(reminder)

    def modifie_alert(self, reminder):
        self.__modifie_alert(reminder)

    def clean_up(self):
        """ remove late reminders """

        self.__logger.info("in clean up")

        for reminder in Reminder.objects.order_by('date_time'):
            if reminder.date_time < 0:
                Reminder.objects.get(id=reminder.id).delete()

    @staticmethod
    def __add_alert(reminder=None):
        """ add a new alert
            reminder: a reminder object,
                      if nothing is given then the reminder will be selected as
                      the minimum date_time of all reminders """

        UserAlertScheduler.__logger.info("in add alert.")
        UserAlertScheduler.__logger.debug(f"reminder value in: {reminder}")

        if reminder is None:
            reminder = Reminder.objects.get_next_reminder()

            UserAlertScheduler.__logger.debug(f"reminder value after if: {reminder}")

            if reminder is None:  # the DB is empty
                UserAlertScheduler.__logger.debug("The DB is empty, there isn't a task waiting.")
                return None

        _, message, method_type, user_id = UserAlertScheduler._get_args(reminder)
        functions = UserAlertScheduler._get_function(method_type)

        UserAlertScheduler.__current_task = reminder

        Thread(target=UserAlertScheduler.__create_timer, args=(functions, message, user_id), daemon=True).start()

        UserAlertScheduler.__logger.debug((
            "new Timer has been started. ",
            f"message: {message} - {user_id} - {UserAlertScheduler.__current_task.date_time}"
        ))

    @staticmethod
    def __create_timer(functions, message, user_id):
        """ create the timer object """

        UserAlertScheduler.__current_timer = Timer(
            UserAlertScheduler.__current_task.date_time.timestamp() - datetime.now().timestamp(),
            UserAlertScheduler.__alert_user,
            args=(functions, message, user_id)  # change to *args, **kwargs
        )
        UserAlertScheduler.__current_timer.start()

    @staticmethod
    def __remove_alert(reminder_id):
        """ remove the reminder with a reminder_id from the queue if possible """

        UserAlertScheduler.__logger.info("in remove alert")

        if UserAlertScheduler.__current_task is not None:
            if UserAlertScheduler.__current_task.id == reminder_id:
                if UserAlertScheduler.__current_timer.is_alive():
                    UserAlertScheduler.__current_timer.cancel()
                    UserAlertScheduler.__current_task = None
                    UserAlertScheduler.__current_timer = None

                    UserAlertScheduler.__logger.debug(
                        f"removed the current reminder. last reminer: {Reminder.objects.get(id=reminder_id)}"
                    )

    @staticmethod
    def __modifie_alert(reminder):
        """ modifie the reminder in the queue if possible """

        UserAlertScheduler.__logger.info("in modifie alert")

        if reminder != UserAlertScheduler.__current_task:
            UserAlertScheduler.__logger.debug(
                f"The two reminders are not the same.\n{UserAlertScheduler.__current_task} vs {reminder}"
            )

            next_reminder = None
            UserAlertScheduler.__current_timer.cancel()

            if reminder.date_time < UserAlertScheduler.__current_task.date_time:
                next_reminder = reminder

            UserAlertScheduler.__logger.debug(f"a new reminder is added: {next_reminder}")

            UserAlertScheduler.__add_alert(next_reminder)

        else:
            UserAlertScheduler.__current_task = reminder

            UserAlertScheduler.__logger.debug(f"the current reminder has been modified: {reminder}")

            # modifie the timer
            UserAlertScheduler.__current_timer.cancel()
            UserAlertScheduler.__add_alert(reminder)
    
    @staticmethod
    def _get_args(reminder):
        """ get the date time, message method type and user id from the reminder object """

        message = reminder.messages
        method_type = reminder.method
        date_time = reminder.date_time
        user_id = reminder.participant_id.user_id

        return date_time, message, method_type, user_id

    @staticmethod
    def _get_function(method_type):
        """ get the functions to invoke using the method type given """

        function_to_invoke = list()

        if method_type == ReminderType.EMAIL or method_type == ReminderType.WEBSITE_EMAIL:
            function_to_invoke.append(mail)

        if method_type == ReminderType.WEBSITE or method_type == ReminderType.WEBSITE_EMAIL:
            function_to_invoke.append(notifie)

        return function_to_invoke

    @staticmethod
    def __alert_user(methods, *args, **kwargs):
        """ alert the user aboue the end of the timer
            methods: the functions to invoke
            # other arguments: message and user_id
            other arguments: *args, **kwargs """

        UserAlertScheduler.__logger.info("in alert user")

        UserAlertScheduler.__logger.debug("starting to loop over all the functions")
        UserAlertScheduler.__logger.debug(f"args: {args} || kwargs: {kwargs}")

        for method in methods:
            method(*args, **kwargs)

        # Potential Send Signal 

        UserAlertScheduler.__logger.debug("deleting the current task from the DB.")

        # remove the current reminder from the db
        Reminder.objects.get(id=UserAlertScheduler.__current_task.id).delete()

    @staticmethod
    @receiver(pre_save, sender=Reminder)
    def __check_before_saving(sender, instance, **kwargs):
        """ add a new alert if possible, otherwise continue with the current alert """

        UserAlertScheduler.__logger.info("in check before saving")
        UserAlertScheduler.__logger.debug("pre save")
        UserAlertScheduler.__logger.debug(f"instance: {instance}")

        if UserAlertScheduler.__current_task is not None:
            if UserAlertScheduler.__current_task.id == instance.id:
                UserAlertScheduler.__logger.debug(
                    f"the reminder has been changed: {UserAlertScheduler.__current_task} vs {instance}"
                )
                UserAlertScheduler.__modifie_alert(instance)

            elif UserAlertScheduler.__current_task.date_time < instance.date_time:
                UserAlertScheduler.__logger.debug("end pre: the timer time hasnt been changed")
                return None

        UserAlertScheduler.__logger.debug(f"set new alert: {instance}")

        UserAlertScheduler.__add_alert(instance)

    @staticmethod
    @receiver(pre_delete, sender=Reminder)
    def __check_before_delete(sender, instance, **kwargs):
        """ remove the alert from the queue if possible """

        UserAlertScheduler.__logger.info("in check before delete")
        UserAlertScheduler.__logger.debug("pre delete")

        UserAlertScheduler.__logger.debug(f"removing the reminder: {instance}")
        UserAlertScheduler.__remove_alert(instance.id)

    @staticmethod
    @receiver(post_delete, sender=Reminder)
    def __check_after_delete(sender, instance, **kwargs):
        """ after removing the instnace, if it was the current reminder then we will schdule a new reminder """

        UserAlertScheduler.__logger.info("in check after delete")
        UserAlertScheduler.__logger.debug("post delete")

        if UserAlertScheduler.__current_task is None:
            UserAlertScheduler.__logger.debug(
                "current task and current timer are None, the last reminder has been deleted."
            )
            UserAlertScheduler.__logger.debug("search a new reminder to insert")

            UserAlertScheduler.__add_alert()

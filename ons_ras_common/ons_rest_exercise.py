"""

   Generic Configuration tool for Micro-Service environment discovery
   License: MIT
   Copyright (c) 2017 Crown Copyright (Office for National Statistics)

   ONSCase wraps routines used to access the case service

"""

class ONSExercise(object):
    """
    This class is designed to take all the work out of accessing the case service. Initially it
    should be able to validate and log events against the case service and also query the event
    service for specific combinations of events. (for example to determine case status)
    """
    def __init__(self, env):
        self._env = env

    def activate(self):
        """"""
        pass

    def get_by_id(self, exercise_id):
        """
        Recover an exercise by exercise_id

        :param exercise_id: The id of the exercise in question
        :return: An exercise record
        """
        exercise = self._env.asyncio.access_endpoint('/collectionexercises/{}'.format(exercise_id))
        if not exercise:
            return 404, {'code': 404, 'text': 'unable to find exercise for this exercise_id'}

        return 200, {'code': 200, 'case': exercise}

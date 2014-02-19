:class:`MotorClient` -- Connection to MongoDB
=============================================

.. currentmodule:: motor

.. autoclass:: MotorClient
  :members:

  .. automethod:: disconnect

  .. describe:: client[db_name] || client.db_name

     Get the `db_name` :class:`MotorDatabase` on :class:`MotorClient` `client`.

     Raises :class:`~motor.errors.InvalidName` if an invalid database name is used.
     Raises :class:`~motor.errors.InvalidOperation` if connection isn't opened yet.

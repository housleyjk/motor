:class:`MotorReplicaSetClient` -- Connection to MongoDB replica set
=======================================================================

.. currentmodule:: motor

.. autoclass:: motor.MotorReplicaSetClient
  :members:

  .. describe:: client[db_name] || client.db_name

     Get the `db_name` :class:`MotorDatabase` on :class:`MotorReplicaSetClient` `client`.

     Raises :class:`~motor.errors.InvalidName` if an invalid database name is used.
     Raises :class:`~motor.errors.InvalidOperation` if connection isn't opened yet.

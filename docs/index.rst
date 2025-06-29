==========
aiolimiter
==========

Introduction
============

An efficient implementation of a rate limiter for asyncio.

This project implements the `Leaky bucket algorithm`_, giving you precise
control over the rate a code section can be entered.

It was first developed `as an answer on Stack Overflow`_.

Installation
------------

.. code-block:: bash

   $ pip install aiolimiter

The library requires Python |requires-python| or newer.

Requirements
------------

- Python >= |requires-python|


Usage
=====

Typical use
-----------

Create an instance of the :class:`aiolimiter.AsyncLimiter` class, specifying
the maximum capacity that can be acquired in one minute::

    from aiolimiter import AsyncLimiter

    async def main():
        limiter = AsyncLimiter(100)

then use this object as an :ref:`asynchronous context manager
<async-context-managers>`, so with :keyword:`async with`, to enclose a section
you want to control the rate of execution of::

    async with limiter:
        # this section will, at most, be entered 100 times / minute

You can also call the :meth:`AsyncLimiter.acquire` async method directly::

    await limit.acquire()  # blocks until there is capacity

or you can simply test if there is space first by calling
:meth:`AsyncLimiter.has_capacity`::

   if limit.has_capacity():
       # reject a request due to rate limiting

.. note::
    You want to create ``AsyncLimiter`` instances *per asyncio loop*.

    Re-using a limiter across asyncio loops is not supported and can lead to
    undefined behaviour. `AsyncLimiter` issues a `RuntimeWarning` and clears
    its internal bookkeeping of waiting tasks when it detects it is being
    reused across loops, but no guarantees are being made for how well this
    will work.

Varying capacity requests
-------------------------

Note that you can count some requests as 'heavier' or 'lighter' by increasing or
decreasing the amount of capacity you work with::

   await limit.acquire(10)
   if limit.has_capacity(0.5):

Do be careful with this though; when mixing capacity amounts, small capacity
requests tend to get run before large blocks of capacity when at or close to the
maximum rate, because there is a greater likelihood that there is enough free
capacity for a smaller request before there is space for a larger one.

Bursting
--------

The rate limit only kicks in once capacity has been reached::

   >>> import asyncio, time
   >>> from aiolimiter import AsyncLimiter
   >>> limiter = AsyncLimiter(4, 8)
   >>> async def task(id):
   ...     await asyncio.sleep(id * 0.01)
   ...     async with limiter:
   ...         print(f'{id:>2d}: Drip! {time.time() - ref:>5.2f}')
   ...
   >>> tasks = [task(i) for i in range(10)]
   >>> ref = time.time(); result = asyncio.run(asyncio.wait(tasks))
    0: Drip!  0.00
    1: Drip!  0.01
    2: Drip!  0.02
    3: Drip!  0.03
    4: Drip!  2.05
    5: Drip!  4.05
    6: Drip!  6.05
    7: Drip!  8.06
    8: Drip! 10.06
    9: Drip! 12.07

For the first 4 tasks, plenty of capacity was available so they were allowed
the limited section in quick succession. Once capacity has been reached, however
tasks have to wait until enough time has passed to free up capacity.

The maximum burst size is equal to the :attr:`AsyncLimiter.max_rate` value, if
you don't want to permit bursts, set the maximum rate to 1 and set *time_period*
to the minimum time between acquisitions::

   >>> limiter = AsyncLimiter(1, 1.5)  # no bursts, allow entry every 1.5 seconds
   >>> tasks = [task(i) for i in range(5)]
   >>> ref = time.time(); result = asyncio.run(asyncio.wait(tasks))
    0: Drip!  0.00
    1: Drip!  1.52
    2: Drip!  3.03
    3: Drip!  4.54
    4: Drip!  6.05

API
===

.. automodule:: aiolimiter
   :members:


Documentation
=============

https://aiolimiter.readthedocs.io/


License
=======

``aiolimiter`` is offered under the MIT license.


Source code
===========

The project is hosted on GitHub_

Please file an issue in the `bug tracker`_ if you have found a bug
or have some suggestions to improve the library.


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _Leaky bucket algorithm: https://en.wikipedia.org/wiki/Leaky_bucket
.. _as an answer on Stack Overflow: https://stackoverflow.com/a/45502319/100297
.. _bug tracker: https://github.com/mjpieters/aiolimiter/issues
.. _GitHub: https://github.com/mjpieters/aiolimiter

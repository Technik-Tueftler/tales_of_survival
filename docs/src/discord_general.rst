general
==========================
This page shares general information about Discord implementation and usage. 

.. _limitations_for_selects:

Limitations for selects
---------------------------
Due to limitations of the Discord API, it is not possible to have more than 
25 options in a select menu. This means that if there are more than 25 options 
available for a select menu, only the first 25 will be displayed. 

The following image shows an example of this. Only 25 characters can be 
displayed in the orange frame, even though there may be 50 in the database. 

.. image:: ../images/dc_limit_select.png
    :width: 400
    :alt: Selection view for character with orange frame.

I am currently still looking for a solution to this limitation. 
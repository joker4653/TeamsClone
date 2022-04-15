* channels_create_v1:
    - assumed that channel creator becomes the owner of the channel.
    - assumed that two channels with the same name can be created, even by the
      same owner.


* channel_messages_v1
    - Raise an input error when the auth_user_id does not refer to a user that does not exist

* auth/logout/v1
    - If a certain session_id is not present in a users sessions list, program will not raise an error, and will simply move to next instruction.

* channel/removeowner/v1
    - The original owner (creator) of a channel can be removed by subsequent owners.

* notifications/get/v1
    - Re. tagging: If a message that already has a tag is edited and the tag remains, a new notification is sent.

* user/stats/v1
    - When a user is removed, their stats relating to channels/dms joined and messages
    sent are left in the same state as they were in prior to removal. This seems like the 
    most complete way to leave it; also not overly important as a removed user cannot
    have a valid token so their user_stats cannot be retreived anyway.

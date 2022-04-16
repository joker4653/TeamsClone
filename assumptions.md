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
    - If a user shares a message, this counts as sending a new message and hence the
    number of messages that they have sent will increase. This means that the total
    number of messages sent in Seams will also increase when a user shares a message.

* users/stats/v1
    - for num_users_who_have_joined_at_least_one_channel_or_dm, assumed that a user
    who has joined only one channel and then leaves that channel would not be included
    in the count i.e. this variable refers to users who are currently in at least one
    channel or dm.
    - sharing a message counts as sending a new message and so the number of messages
    that exists will increase when a user shares a message.

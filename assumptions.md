* channels_create_v1:
    - assumed that channel creator becomes the owner of the channel.
    - assumed that two channels with the same name can be created, even by the
      same owner.


* channel_messages_v1
    - Raise an input error when the auth_user_id does not refer to a user that does not exist
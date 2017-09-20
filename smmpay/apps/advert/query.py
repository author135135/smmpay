DISCUSSION__NEW_MESSAGES_COUNT = """
    SELECT COUNT(*)
    FROM `advert_discussion_message` LEFT JOIN `advert_discussion_message_view`
    ON `advert_discussion_message`.`id` = `advert_discussion_message_view`.`message_id`
    WHERE `advert_discussion_message`.`discussion_id` = `advert_discussion`.`id`
    AND `advert_discussion_message`.`sender_id` != `advert_discussion_user`.`id`
    AND `advert_discussion_message_view`.`id` IS NULL
"""

DISCUSSIONMESSAGE__IS_VIEWED = """
    SELECT `advert_discussion_message_view`.`viewed`
    FROM `advert_discussion_message_view`
    WHERE `advert_discussion_message_view`.`message_id` = `advert_discussion_message`.`id`
    AND `advert_discussion_message_view`.`user_id` = %s
"""

ADVERT__NEW_MESSAGES_COUNT = """
    SELECT COUNT(*)
    FROM `advert_discussion` 
    JOIN `advert_discussion_message` 
	ON `advert_discussion`.`id` = `advert_discussion_message`.`discussion_id`
	JOIN `advert_discussion_user`
	ON `advert_discussion_message`.`sender_id` = `advert_discussion_user`.`id`
    LEFT JOIN `advert_discussion_message_view`
    ON `advert_discussion_message`.`id` = `advert_discussion_message_view`.`message_id`
    WHERE `advert_discussion`.`advert_id` = `advert_advert`.`id`
    AND `advert_discussion_user`.`user_id` != `advert_advert`.`author_id`
    AND `advert_discussion_message_view`.`id` IS NULL
"""

ADVERT__IN_FAVORITE = """
    SELECT COUNT(*)
    FROM `advert_favorite_advert`
    WHERE `advert_favorite_advert`.`advert_id` = `advert_advert`.`id` 
    AND `advert_favorite_advert`.`user_id` = %s
"""


TemplatesBroadcast = {
    "hello_msg": {
        'bakery': {"template": "order_intro_2910", "broadcast": "order_ack"},
        'grocery': {"template": "order_intro_2910", "broadcast": "order_ack"},
        'personal_care': {"template": "order_intro_2910", "broadcast": "order_ack"},
        'dairy': {"template": "order_intro_2910", "broadcast": "order_ack"}

    },
    'order_detail_msg': {
        'bakery':  {"template": "order_details_0211_2", "broadcast": "order_summary"},
        'grocery': {"template": "order_details_0211_2", "broadcast": "order_summary"},
        'dairy': {"template": "order_details_0211_2", "broadcast": "order_summary"},

        # 'personal_care': {"template": "delivery_tomorrow", "broadcast": "delivery_notification"},

    },
    "delivery_tomorrow_msg": {
        'bakery':    {"template": "delivery_tomorrow", "broadcast": "delivery_notification"},
        'grocery': {"template": "delivery_tomorrow", "broadcast": "delivery_notification"},
        'personal_care': {"template": "delivery_tomorrow", "broadcast": "delivery_notification"},
        'dairy': {"template": "delivery_tomorrow", "broadcast": "delivery_notification"},

    },
    "delivery_today_msg": {
        'bakery':    {"template": "delivery_today", "broadcast": "delivery_notification"},
        'grocery': {"template": "delivery_today", "broadcast": "delivery_notification"},
        'personal_care': {"template": "delivery_today", "broadcast": "delivery_notification"},
        'dairy': {"template": "delivery_today", "broadcast": "delivery_notification"},

    },
    "payment_remainder_msg": {
        'bakery': {"template": "payment_reminder_2", "broadcast": "payment_reminder"},
        'grocery': {"template": "payment_reminder_2", "broadcast": "payment_reminder"},
        'personal_care': {"template": "payment_reminder_2", "broadcast": "payment_reminder"},
        'dairy': {"template": "payment_reminder_2", "broadcast": "payment_reminder"},


    },
    "feedback_prepay": {
        'bakery': {"template": "feedback_prepaid", "broadcast": "feedback"},
        'grocery': {"template": "feedback_prepaid", "broadcast": "feedback"},
        'personal_care': {"template": "feedback_prepaid", "broadcast": "feedback"},
        'dairy': {"template": "feedback_prepaid", "broadcast": "feedback"}

    },

     "feedback_postpay": {
        'bakery': {"template": "feedback_postpaid", "broadcast": "feedback"},
        'grocery': {"template": "feedback_postpaid", "broadcast": "feedback"},
        'personal_care': {"template": "feedback_postpaid", "broadcast": "feedback"},
        'dairy': {"template": "feedback_postpaid", "broadcast": "feedback"}

    },
    'prepay_msg': {
        'bakery':  {"template": "reply_order", "broadcast": "prepay"},
        'grocery': {"template": "reply_order", "broadcast": "prepay"},
        # 'personal_care': {"template": "delivery_tomorrow", "broadcast": "delivery_notification"},
        'dairy': {"template": "reply_order", "broadcast": "prepay"},


    },
    'postpay_msg': {
        'bakery':  {"template": "postpay_0211_1", "broadcast": "postpay"},
        'grocery': {"template": "postpay_0211_1", "broadcast": "postpay"},
        'dairy': {"template": "postpay_0211_1", "broadcast": "postpay"},

        # 'personal_care': {"template": "delivery_tomorrow", "broadcast": "delivery_notification"},

    },
    'order_prepay': {
        'bakery':  {"template": "order_prepaid_notification", "broadcast": "prepay"},
        'grocery': {"template": "order_prepaid_notification", "broadcast": "prepay"},
        'dairy': {"template": "order_prepaid_notification", "broadcast": "prepay"}
    },
    'order_postpay': {
        'bakery':  {"template": "orer_postpay_notification", "broadcast": "postpay"},
        'grocery': {"template": "orer_postpay_notification", "broadcast": "postpay"},
        'dairy': {"template": "orer_postpay_notification", "broadcast": "postpay"}
    },
    'today_prepay': {
        'bakery':  {"template": "delivery_today_prepaid_0212", "broadcast": "prepay"},
        'grocery': {"template": "delivery_today_prepaid_0212", "broadcast": "prepay"},
        'dairy': {"template": "delivery_today_prepaid_0212", "broadcast": "prepay"}
    },
    'today_postpay': {
        'bakery':  {"template": "delivery_today_postpay_011220", "broadcast": "postpay"},
        'grocery': {"template": "delivery_today_postpay_011220", "broadcast": "postpay"},
        'dairy': {"template": "delivery_today_postpay_011220", "broadcast": "postpay"}
    },
    'tomorrow_prepay': {
        'bakery':  {"template": "delivery_tomorrow_prepaid", "broadcast": "prepay"},
        'grocery': {"template": "delivery_tomorrow_prepaid", "broadcast": "prepay"},
        'dairy': {"template": "delivery_tomorrow_prepaid", "broadcast": "prepay"}
    },
    'tomorrow_postpay': {
        'bakery':  {"template": "deliver_tomorrow_postpaid", "broadcast": "postpay"},
        'grocery': {"template": "deliver_tomorrow_postpaid", "broadcast": "postpay"},
        'dairy': {"template": "deliver_tomorrow_postpaid", "broadcast": "postpay"}
    },

     "cancel_prepay": {
        'bakery': {"template": "order_cancelled_prepaid_2", "broadcast": "order_cancelled"},
        'grocery': {"template": "order_cancelled_prepaid_2", "broadcast": "order_cancelled"},
        'personal_care': {"template": "order_cancelled_prepaid_2", "broadcast": "order_cancelled"},
        'dairy': {"template": "order_cancelled_prepaid_2", "broadcast": "order_cancelled"}

    },

    "cancel_postpay": {
        'bakery': {"template": "order_cancelled_postpaid", "broadcast": "order_cancelled"},
        'grocery': {"template": "order_cancelled_postpaid", "broadcast": "order_cancelled"},
        'personal_care': {"template": "order_cancelled_postpaid", "broadcast": "order_cancelled"},
        'dairy': {"template": "order_cancelled_postpaid", "broadcast": "order_cancelled"}

    },
    "confirm_msg": {
        'bakery': {"template": "pending_payment_3", "broadcast": "order_confirm"},
        'grocery': {"template": "pending_payment_3", "broadcast": "order_confirm"},
        'personal_care': {"template": "pending_payment_3", "broadcast": "order_confirm"},
        'dairy': {"template": "pending_payment_3", "broadcast": "order_confirm"}

    }
}

vendor_type = {
    'Organic German Bake Shop': 'bakery',
    'Desi Utpad by Jaya': 'grocery',
    'Miche Artisan Bake': 'bakery',
    'The Womens Company': 'personal_care',
    'desiutpadbyjaya': "grocery",
    'organicgermanbakeshop': 'bakery',
    'micheartisanbakery': 'bakery',
    'mrdairy': 'dairy',
    'Mr. Dairy': 'dairy',
}

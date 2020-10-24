TemplatesBroadcast = {
    "hello_msg": {
        'bakery': {"template": "order_intro_2308", "broadcast": "order_ack"},
        'grocery': {"template": "order_intro_2308", "broadcast": "order_ack"},
        'personal_care': {"template": "order_intro_2308", "broadcast": "order_ack"}
    },
    "payment_remainder_msg": {
        'bakery': {"template": "payment_reminder", "broadcast": "payment_reminder"},
        'grocery': {"template": "payment_reminder", "broadcast": "payment_reminder"},
        'personal_care': {"template": "payment_reminder", "broadcast": "payment_reminder"},

    },
    "feedback_msg": {
        'bakery': {"template": "feed_past", "broadcast": "feedback"},
        'grocery': {"template": "feed_past", "broadcast": "feedback"},
        'personal_care': {"template": "feed_past", "broadcast": "feedback"}
    },
    "delivery_notification_msg": {
        'bakery':    {"template": "delivery_tomorrow", "broadcast": "delivery_notification"},
        'grocery': {"template": "delivery_tomorrow", "broadcast": "delivery_notification"},
        'personal_care': {"template": "delivery_tomorrow", "broadcast": "delivery_notification"},
    }

}


vendor_type = {
    'Organic German Bake Shop': 'bakery',
    'Desi Utpad by Jaya': 'grocery',
    'Miche Artisan Bake': 'bakery',
    'The Womens Company': 'personal_care',
    'desiutpadbyjaya': "bakery"
}

import random
import pandas as pd

# Phrase Banks

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
        "Mon", "Tue", "Tues", "Wed", "Thur", "Thurs", "Fri", "Sat", "Sun",
        "weekday", "weekend", "weekdays", "weekends"]

TIMES = [time for h in range(7, 23)
    for time in (
        f"{h if h <= 12 else h - 12}{'am' if h < 12 else 'pm'}",
        f"{h:02}00"
    )]

GYMS = ["Ang Mo Kio CC", "Bukit Gombak", "Kallang Basin", "Katong", "Bukit Canberra",
        "Bishan", "Bukit Batok", "Sengkang", "Fernvale Square", "Pasir Ris",
        "Enabling Village", "Delta", "Clementi", "Jalan Besar", "Serangoon Central",
        "Toa Payoh West CC", "Yio Chu Kang", "Toa Payoh", "Yishun", "Tampines",
        "Senja-Cashew", "Heartbeat Bedok", "Jurong Lake Gardens", "Choa Chu Kang", "Woodlands",
        "Jurong West", "Jurong East", "Hockey Village Boon Lay"]

VERBS = ["Is", "Would", "Can I know if", "Do you think", "Tell me if"]
ADJECTIVES = ["crowded", "busy", "full", "occupied", "packed"]
INTROS = ["I'd like to know", "Can you tell me", "What's", "Do you know", "Could you share",
          "May I know", "I'm trying to find out", "Would you mind telling me", "Can I find out",
          "Is it possible to know", "I'd appreciate knowing", "Could I get info on",
          "Do you happen to know", "Any idea about", "Just wondering about"
]
TRAFFIC = ["capacity", "crowd", "traffic", "number of people"]

GYM_TITLES = ["", " ActiveSG gym", " Gym", " Centre", " ActiveSG"]


# Generate Queries for Intent 0 (Capacity of Gym)
def generate_capacity_query(num_samples):
    # Templates
    templates = {
        "no_day_no_time": [
            "{intro} the {traffic} at {gym}{title}?",
            "{intro} how {adj} {gym}{title} is?",
            "{intro} what the {traffic} is like at {gym}{title}?",
            "{intro} the current {traffic} for {gym}{title}.",
            "{intro} if you have any info on how {adj} {gym}{title} is.",
            "How {adj} is {gym}{title}?",
            "Give me the {traffic} at {gym}{title}.",
            "What's the estimated {traffic} at {gym}{title}?",
            "I'm trying to check how {adj} {gym}{title} is.",
            "Could you share the {traffic} at {gym}{title}?"
        ],

        "day_only": [
            "{intro} how {adj} {gym}{title} is on {day}?",
            "{intro} the {traffic} at {gym}{title} on {day}.",
            "{intro} what the {traffic} is like at {gym}{title} on {day}.",
            "{intro} how packed {gym}{title} usually is on {day}.",
            "How {adj} is {gym}{title} on {day}?",
            "Give me the {traffic} of {gym}{title} on {day}.",
            "Do you have any idea how {adj} {gym}{title} gets on {day}?",
            "Could I check the {traffic} at {gym}{title} every {day}?",
            "What's the typical {traffic} at {gym}{title} on {day}?",
            "What kind of crowd level does {gym}{title} usually have on {day}?"
        ],

        "time_only": [
            "{intro} how {adj} {gym}{title} is at {time}?",
            "{intro} the {traffic} for {gym}{title} at {time}.",
            "{intro} what the {traffic} is like at {gym}{title} around {time}.",
            "How full does {gym}{title} get around {time}?",
            "How packed does {gym}{title} tend to be at {time}?",
            "Could you share the {traffic} at {gym}{title} during {time}?",
            "I'd like a rough idea of the {traffic} at {gym}{title} for {time}.",
            "What's the estimated {traffic} at {gym}{title} at {time}?",
            "What's the expected {traffic} at {gym}{title} at {time}?",
            "Give me the crowd level of {gym}{title} at {time}."
        ],

        "day_time": [
            "{intro} how {adj} {gym}{title} is on {day} at {time}?",
            "{intro} the {traffic} at {gym}{title} on {day} at {time}.",
            "{intro} what the {traffic} is like at {gym}{title} on {day} at {time}.",
            "{intro} the typical crowd level for {gym}{title} on {day} at {time}.",
            "How {adj} is {gym}{title} on {day} at {time}?",
            "Tell me the {traffic} at {gym}{title} for {day} around {time}.",
            "Please provide the {traffic} at {gym}{title} for {day} around {time}.",
            "Could you show me how {adj} {gym}{title} is on {day} at {time}?",
            "I'd like a quick check on how {adj} {gym}{title} is on {day} at {time}.",
            "What's the usual {traffic} at {gym}{title} if I go on {day} at {time}?"
        ]
    }

    intent_0_queries = []

    for _ in range(num_samples):
        filter = random.choices(
            population=["no_day_no_time", "day_only", "time_only", "day_time"],
            weights=[0.25, 0.25, 0.25, 0.25],
            k=1
        )[0]

        template = random.choice(templates[filter])

        # Combine Random Selection into a Query
        query = template.format(
            intro=random.choice(INTROS),
            verb=random.choice(VERBS),
            adj=random.choice(ADJECTIVES),
            traffic=random.choice(TRAFFIC),
            gym = random.choice(GYMS),
            title = random.choice(GYM_TITLES),
            day=random.choice(DAYS),
            time=random.choice(TIMES),
        )

        intent_0_queries.append(query)

    return intent_0_queries


# Generate Queries for Intent 1 (Least Crowded Gym)
def generate_least_crowded_query(num_samples):
    templates = {
        "no_day_no_time": [
            "{intro} which {title} is the {least_adj}?",
            "{intro} the {title} with the lowest {traffic}.",
            "{intro} what the quietest {title} is.",
            "{intro} which {title} tends to be the least packed.",
            "{intro} the least busy {title} currently.",
            "Which {title} is the least crowded?",
            "What's the {title} with the lowest {traffic}?",
            "Give me the quietest {title}."
        ],
        "day_only": [
            "{intro} which {title} is the {least_adj} on {day}?",
            "{intro} the {title} with the lowest {traffic} on {day}.",
            "{intro} the least crowded {title} this coming {day}.",
            "{intro} what the quietest {title} is on {day}.",
            "Which {title} is usually the least packed on {day}?",
            "Tell me the least busy {title} on {day}.",
            "Give me the quietest {title} for {day}."
        ],
        "time_only": [
            "{intro} which {title} is the {least_adj} at {time}?",
            "{intro} the {title} with the lowest {traffic} at {time}.",
            "{intro} what the least packed {title} is around {time}.",
            "Which {title} tends to be the least crowded at {time}?",
            "Tell me the quietest {title} during {time}."
        ],
        "day_time": [
            "{intro} which {title} is the {least_adj} on {day} at {time}?",
            "{intro} what the least crowded {title} is on {day} at {time}.",
            "{intro} the quietest {title} for {day} around {time}.",
            "Tell me the {title} with the lowest {traffic} at {time} on {day}.",
            "Which {title} is typically the least packed on {day} at {time}?"
        ]
    }

    least_phrases = [
        "least {adj}",
        "most quiet",
        "least packed",
        "least busy",
        "has the lowest {traffic}"
    ]

    intent_1_queries = []

    for _ in range(num_samples):
        filter_type = random.choices(
            population=["no_day_no_time", "day_only", "time_only", "day_time"],
            weights=[0.25, 0.25, 0.25, 0.5],
            k=1
        )[0]

        template = random.choice(templates[filter_type])
        phrase = random.choice(least_phrases)
        least_adj = phrase.format(
            adj=random.choice(ADJECTIVES),
            traffic=random.choice(TRAFFIC)
        )

        query = template.format(
            intro=random.choice(INTROS),
            least_adj=least_adj,
            traffic=random.choice(TRAFFIC),
            day=random.choice(DAYS),
            time=random.choice(TIMES),
            title=random.choice(GYM_TITLES)
        ).strip().capitalize()

        intent_1_queries.append(query)

    return intent_1_queries


# Generate Queries for Intent 2 (Most Crowded Gym)
def generate_most_crowded_query(num_samples):
    templates = {
        "no_day_no_time": [
            "{intro} which {title} is the most {adj}?",
            "{intro} the {title} with the highest {traffic}.",
            "{intro} what the most crowded {title} is.",
            "{intro} which {title} tends to be most packed.",
            "{intro} the busiest {title} currently.",
            "{intro} which {title} has the biggest {traffic}.",
            "Which {title} is the most crowded?",
            "What's the {title} with the most {traffic}?",
            "Give me the most packed {title}."
        ],
        "day_only": [
            "{intro} which {title} is most {adj} on {day}?",
            "{intro} what the crowd level is like across {title} on {day}.",
            "{intro} the busiest {title} on {day}.",
            "{intro} the {title} with the highest {traffic} on {day}.",
            "{intro} which {title} tends to be full on {day}.",
            "Which {title} is the most packed on {day}?",
            "Tell me which {title} is busiest on {day}.",
            "Give me the most crowded {title} this coming {day}."
        ],
        "time_only": [
            "{intro} which {title} is most {adj} at {time}?",
            "{intro} what {title} has the most {traffic} around {time}.",
            "{intro} the busiest {title} at {time}.",
            "{intro} which {title} usually sees the highest {traffic} at {time}.",
            "Which {title} tends to be full at {time}?",
            "Tell me the most packed {title} around {time}.",
            "Give me the busiest {title} at {time}."
        ],
        "day_time": [
            "{intro} which {title} is most {adj} on {day} at {time}?",
            "{intro} the most crowded {title} on {day} at {time}.",
            "{intro} which {title} sees the highest {traffic} on {day} at {time}.",
            "{intro} the busiest {title} for {day} at {time}.",
            "{intro} which {title} is typically most packed on {day} at {time}.",
            "Which {title} is most crowded on {day} at {time}?",
            "Tell me which {title} is busiest at {time} on {day}.",
            "What {title} usually has the biggest {traffic} at {time} on {day}?"
        ]
    }

    intent_2_queries = []

    for _ in range(num_samples):
        filter_type = random.choices(
            population=["no_day_no_time", "day_only", "time_only", "day_time"],
            weights=[0.25, 0.25, 0.25, 0.25],
            k=1
        )[0]

        template = random.choice(templates[filter_type])
        query = template.format(
            intro=random.choice(INTROS),
            adj=random.choice(ADJECTIVES),
            traffic=random.choice(TRAFFIC),
            day=random.choice(DAYS),
            time=random.choice(TIMES),
            title=random.choice(GYM_TITLES)
        )
        intent_2_queries.append(query)

    return intent_2_queries


# Generate Queries for Intent 3 (Best Time to Visit)
def generate_best_time_query(num_samples):
    templates = {
        "no_day": [
            "{intro} the best time to visit {gym}{title}?",
            "{intro} when {gym}{title} is the {least_phrase}.",
            "{intro} what time {gym}{title} usually gets the {least_phrase}.",
            "{intro} the quietest time to go to {gym}{title}.",
            "{intro} when it's not so busy at {gym}{title}.",
            "When is {gym}{title} the {least_phrase}?",
            "What time is it best to go to {gym}{title} if I want to avoid crowds?",
            "I'd like to know the best time slot to visit {gym}{title}.",
            "When does {gym}{title} have the {least_phrase}?",
            "Could you suggest a good time to go to {gym}{title} when it's the {least_phrase}?"
        ],
        "with_day": [
            "{intro} the best time to visit {gym}{title} on {day}?",
            "{intro} when {gym}{title} is the {least_phrase} on {day}.",
            "{intro} what time {gym}{title} gets the {least_phrase} on {day}.",
            "{intro} the quietest time to go to {gym}{title} on {day}.",
            "{intro} when it's not so busy at {gym}{title} on {day}.",
            "When is {gym}{title} the {least_phrase} on {day}?",
            "What time is best to go to {gym}{title} on {day} if I want to avoid crowds?",
            "I'd like to know the best time slot to visit {gym}{title} on {day}.",
            "When does {gym}{title} have the {least_phrase} on {day}?",
            "Could you suggest a good time to go to {gym}{title} on {day} when it's the {least_phrase}?"
        ]
    }

    least_phrases = [
        "least {adj}",
        "most quiet",
        "least packed",
        "least busy",
        "has the lowest {traffic}"
    ]

    intent_3_queries = []

    for _ in range(num_samples):
        filter_type = random.choices(
            population=["no_day", "with_day"],
            weights=[0.5, 0.5],
            k=1
        )[0]
        template = random.choice(templates[filter_type])
        phrase_template = random.choice(least_phrases)
        least_phrase = phrase_template.format(
            adj=random.choice(ADJECTIVES),
            traffic=random.choice(TRAFFIC)
        )

        query = template.format(
            intro=random.choice(INTROS),
            gym=random.choice(GYMS),
            title=random.choice(GYM_TITLES),
            least_phrase=least_phrase,
            day=random.choice(DAYS)
        )
        intent_3_queries.append(query)

    return intent_3_queries

if __name__ == "__main__":
    intent0_samples = generate_capacity_query(250)
    intent1_samples = generate_least_crowded_query(250)
    intent2_samples = generate_most_crowded_query(250)
    intent3_samples = generate_best_time_query(250)

    texts = intent0_samples + intent1_samples + intent2_samples + intent3_samples
    labels = (
        [0] * len(intent0_samples) +
        [1] * len(intent1_samples) +
        [2] * len(intent2_samples) +
        [3] * len(intent3_samples)
    )

    df = pd.DataFrame({"Text": texts, "Label": labels})
    df.to_csv("distilbert-model/Intent_Train_Data.csv", index=False)
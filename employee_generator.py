from faker import Faker
import random
import pandas as pd

fake = Faker()

# ------------------------
# Country Detection Based on Name
# ------------------------

def detect_country_from_name(name):
    indian_names = ['Raj', 'Ankit', 'Priya', 'Amit', 'Neha', 'Rahul', 'Kumar', 'Patel']
    british_names = ['George', 'Harry', 'Oliver', 'Amelia', 'Jack', 'Poppy']
    canadian_names = ['Liam', 'Noah', 'Logan', 'Emma', 'Avery', 'Jackson']

    lower_name = name.lower()
    if any(n.lower() in lower_name for n in indian_names):
        return "IN"
    elif any(n.lower() in lower_name for n in british_names):
        return "UK"
    elif any(n.lower() in lower_name for n in canadian_names):
        return "CA"
    else:
        return "US"  # default fallback

# ------------------------
# Phone Number Generator by Country
# ------------------------

def generate_phone_number_by_country(country_code):
    if country_code == "IN":
        return "+91 " + str(random.choice([6, 7, 8, 9])) + ''.join(random.choices("0123456789", k=9))
    elif country_code == "US":
        return "+1 " + ''.join(random.choices("23456789", k=1)) + ''.join(random.choices("0123456789", k=2)) + '-' + ''.join(random.choices("0123456789", k=3)) + '-' + ''.join(random.choices("0123456789", k=4))
    elif country_code == "UK":
        return "+44 7" + ''.join(random.choices("0123456789", k=9))
    elif country_code == "CA":
        return "+1 " + ''.join(random.choices("204357", k=3)) + '-' + ''.join(random.choices("0123456789", k=3)) + '-' + ''.join(random.choices("0123456789", k=4))
    else:
        return "+999 " + ''.join(random.choices("0123456789", k=10))

# ------------------------
# Predefined Fields
# ------------------------

PREDEFINED_FIELDS = {
    "country": lambda: detect_country_from_name(fake.name()),
    "phone": lambda: generate_phone_number_by_country(detect_country_from_name(fake.name())),
    "name": lambda: fake.name(),
    "email": lambda: fake.email(),
    "address": lambda: fake.address(),
    "job_title": lambda: fake.job(),
    "company": lambda: fake.company(),
    "dob": lambda: fake.date_of_birth(minimum_age=21, maximum_age=60).isoformat(),
    "salary": lambda: str(random.randint(30000, 150000)),
    "skills": lambda: ', '.join(fake.words(nb=5)),
    "experience": lambda: str(random.randint(0, 15)) + " years"
}

# ------------------------
# Smart Generator for Custom Fields
# ------------------------

def generate_fake_value_for_custom_field(field_name, country="US"):
    field_name = field_name.lower()

   
    if "age" in field_name:
        return str(random.randint(18, 60))
    elif "city" in field_name:
        return fake.city()
    elif "state" in field_name:
        return fake.state()
    elif "zip" in field_name or "postal" in field_name:
        return fake.postcode()
    elif "website" in field_name or "url" in field_name:
        return fake.url()
    elif "linkedin" in field_name:
        return f"https://linkedin.com/in/{fake.user_name()}"
    elif "github" in field_name:
        return f"https://github.com/{fake.user_name()}"
    elif "blood" in field_name:
        return random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
    elif "gender" in field_name:
        return random.choice(["Male", "Female", "Other"])
    else:
        return fake.word()

# ------------------------
# Main Generator
# ------------------------

def generate_employee_data(num_rows, selected_fields, custom_fields):
    all_rows = []

    for idx in range(num_rows):
        row = {"S.No": idx + 1}

        # Generate name early for country detection
        name = PREDEFINED_FIELDS["name"]() if "name" in selected_fields else fake.name()
        row["name"] = name if "name" in selected_fields else None
        country = detect_country_from_name(name)

        for field in selected_fields:
            if field == "name":
                continue  # already set
            elif field == "phone":
                row["phone"] = generate_phone_number_by_country(country)
            elif field in PREDEFINED_FIELDS:
                row[field] = PREDEFINED_FIELDS[field]()
            else:
                row[field] = generate_fake_value_for_custom_field(field, country)

        for custom_field in custom_fields:
            if custom_field not in selected_fields:
                row[custom_field] = generate_fake_value_for_custom_field(custom_field, country)

        all_rows.append(row)

    df = pd.DataFrame(all_rows)

    # Keep "S.No" first, then selected/custom fields
    columns_order = ["S.No"]
    if "name" in selected_fields:
        columns_order.append("name")
    for col in selected_fields:
        if col != "name":
            columns_order.append(col)
    for col in custom_fields:
        if col not in selected_fields:
            columns_order.append(col)

    df = df[columns_order]
    return df

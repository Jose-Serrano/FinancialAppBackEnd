from email_validator import validate_email

emails = [
    "test@example.com",
    "invalid-email",
    "another.tést@domain.com",
    "wrong@domain",
    "valid.email@sub.domain.com"
]

for email in emails:
    try:
        valid = validate_email(email)
        print(f"{email} is valid.")
    except Exception as e:
        print(f"{email} is invalid: {e}")

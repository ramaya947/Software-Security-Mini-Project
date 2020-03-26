from flask_sqlalchemy import SQLAlchemy

def deposit_money(user, amount, db):
    try:
        amount = float(amount)
        user_data = db.query.filter_by(username=user).first()
        user_data.balance += amount

        print("Succesfully deposited ${} to {}'s account").format(amount, user)

        return user_data
    except:
        print("ERROR: Could not deposit ${} to {}'s account").format(amount, user)


def send_money(sender, recipient, amount, db):
    try:
        amount = float(amount)
        sender_data = db.query.filter_by(username=sender).first()
        recipient_data = db.query.filter_by(username=recipient).first()

        if sender_data is None or recipient_data is None:
            raise("ERROR: Could not find sender or recipient")

        if sender_data.balance < amount:
            raise("ERROR: Sender has insufficient funds")

        # Add recipient to sender's recents

        if sender_data.recent_contact1 is None:
            sender_data.recent_contact1 = recipient_data.username
        elif sender_data.recent_contact2 is None and sender_data.recent_contact1 != recipient_data.username:
            sender_data.recent_contact2 = recipient_data.username
        elif  sender_data.recent_contact3 is None and sender_data.recent_contact1 != recipient_data.username and sender_data.recent_contact2 != recipient_data.username:
            sender_data.recent_contact3 = recipient_data.username

        sender_data.balance -= amount
        recipient_data.balance += amount

        return (sender_data, recipient_data)
    except:
        print("ERROR: Could not transfer ${} from {} to {} ").format(amount, sender, recipient)


def update_profile_pic(user, url, db):
    try:
        user_data = db.query.filter_by(username=user).first()
        user_data.profile_picture = url

        print("Succesfully updated {}'s profile picture").format(user)
        return user_data
    except:
        print("Could not update {}'s profile picutre.").format(user)


def get_contacts(user):
    recent_contacts = []

    if user.recent_contact1 is not None:
        recent_contacts.append(user.recent_contact1)

    if user.recent_contact2 is not None:
        recent_contacts.append(user.recent_contact2)

    if user.recent_contact3 is not None:
        recent_contacts.append(user.recent_contact3)

    return recent_contacts


def get_contacts_data(contacts, db):
    contacts_data = []

    for contact in contacts: 
        user_data = db.query.filter_by(username=contact).first()
        contacts_data.append({
            "username": user_data.username,
            "profile_picture": user_data.profile_picture
        })

    return contacts_data
        

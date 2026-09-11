import datetime
from backend import database, models

def seed():
    database.init_db()
    db = database.SessionLocal()
    
    # Check if Eleanor Vance already exists
    user = db.query(models.User).filter(models.User.username == "eleanor").first()
    if not user:
        user = models.User(
            username="eleanor",
            password_hash="mockhash123",
            name="Eleanor Vance",
            age=76,
            role="elderly"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user: {user.name} (id={user.id})")

    # Check if Caregiver Sarah Vance exists
    caregiver = db.query(models.User).filter(models.User.username == "sarah").first()
    if not caregiver:
        caregiver = models.User(
            username="sarah",
            password_hash="mockhash123",
            name="Sarah Vance",
            age=45,
            role="caregiver"
        )
        db.add(caregiver)
        db.commit()
        db.refresh(caregiver)
        print(f"Created caregiver user: {caregiver.name} (id={caregiver.id})")

    # Ensure Eleanor is assigned to Sarah
    if user and caregiver and user.caregiver_id != caregiver.id:
        user.caregiver_id = caregiver.id
        db.commit()
        print(f"Linked patient {user.name} to caregiver {caregiver.name}")
    
    # Seed reminders if none exist for user
    if db.query(models.Reminder).filter(models.Reminder.user_id == user.id).count() == 0:
        reminders = [
            models.Reminder(
                user_id=user.id,
                task="Morning Garden Walk",
                reminder_type="activity",
                date="2026-09-11",
                time="07:30 AM",
                status="completed"
            ),
            models.Reminder(
                user_id=user.id,
                task="Morning Blood Pressure Medication (Lisinopril 10mg)",
                reminder_type="medication",
                date="2026-09-11",
                time="08:30 AM",
                status="completed"
            ),
            models.Reminder(
                user_id=user.id,
                task="Cognitive Game: Word Recall",
                reminder_type="activity",
                date="2026-09-11",
                time="10:30 AM",
                status="completed"
            ),
            models.Reminder(
                user_id=user.id,
                task="Afternoon Hydration & Chamomile Tea",
                reminder_type="hydration",
                date="2026-09-11",
                time="02:00 PM",
                status="pending"
            ),
            models.Reminder(
                user_id=user.id,
                task="Evening Family Phone Call with Sarah",
                reminder_type="social",
                date="2026-09-11",
                time="06:30 PM",
                status="pending"
            ),
        ]
        db.add_all(reminders)
        db.commit()
        print(f"Seeded {len(reminders)} reminders.")

    # Seed memories if none exist
    if db.query(models.Memory).filter(models.Memory.user_id == user.id).count() == 0:
        memories = [
            models.Memory(
                user_id=user.id,
                person_name="Maine Childhood Cottage",
                relationship="Place / Vacation",
                information="The family summer cabin in Boothbay Harbor, Maine. Eleanor spent her childhood summers here tending wild hydrangeas with her mother."
            ),
            models.Memory(
                user_id=user.id,
                person_name="Rusty (Golden Retriever)",
                relationship="Pet / Companion",
                information="Eleanor's beloved golden retriever dog Rusty, who accompanied her on morning strolls for over 12 years and loved chasing tennis balls."
            ),
            models.Memory(
                user_id=user.id,
                person_name="Granddaughter Clara",
                relationship="Family / Granddaughter",
                information="Clara was born on a sunny morning in June 2021. Eleanor knitted her very first yellow baby blanket and loves reading fairy tales to her."
            ),
        ]
        db.add_all(memories)
        db.commit()
        print(f"Seeded {len(memories)} memories.")

    # Seed initial game results
    if db.query(models.GameResult).filter(models.GameResult.user_id == user.id).count() == 0:
        now = datetime.datetime.now(datetime.timezone.utc)
        results = [
            models.GameResult(
                user_id=user.id,
                game_name="Word Recall Match",
                score=92.0,
                accuracy=95.0,
                completion_time=492.0,
                difficulty_level=3,
                date=now - datetime.timedelta(hours=2)
            ),
            models.GameResult(
                user_id=user.id,
                game_name="Spatial Tile Ordering",
                score=84.0,
                accuracy=88.0,
                completion_time=760.0,
                difficulty_level=2,
                date=now - datetime.timedelta(days=1)
            ),
            models.GameResult(
                user_id=user.id,
                game_name="Card Memory Match",
                score=90.0,
                accuracy=92.0,
                completion_time=320.0,
                difficulty_level=2,
                date=now - datetime.timedelta(days=2)
            ),
        ]
        db.add_all(results)
        db.commit()
        print(f"Seeded {len(results)} game results.")

    db.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed()

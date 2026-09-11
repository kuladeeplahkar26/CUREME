import datetime
from backend import database, models

def seed():
    """
    Custom seed data script.
    Add your custom users, patients, caregivers, reminders, memories, and game results below.
    """
    database.init_db()
    db = database.SessionLocal()

    try:
        # -------------------------------------------------------------
        # 1. USERS & CAREGIVERS
        # -------------------------------------------------------------
        # Example template:
        # custom_user = models.User(
        #     username="patient1",
        #     password_hash="your_password_hash",
        #     name="Patient Name",
        #     age=70,
        #     role="elderly"
        # )
        # db.add(custom_user)
        # db.commit()
        # db.refresh(custom_user)

        # -------------------------------------------------------------
        # 2. REMINDERS
        # -------------------------------------------------------------
        # reminder = models.Reminder(
        #     user_id=custom_user.id,
        #     task="Take Medication",
        #     reminder_type="medication",
        #     date="2026-09-12",
        #     time="09:00 AM",
        #     status="pending"
        # )
        # db.add(reminder)

        # -------------------------------------------------------------
        # 3. MEMORIES
        # -------------------------------------------------------------
        # memory = models.Memory(
        #     user_id=custom_user.id,
        #     person_name="Family Member",
        #     relationship="Daughter",
        #     information="Lives nearby and visits on weekends."
        # )
        # db.add(memory)

        # -------------------------------------------------------------
        # 4. GAME RESULTS
        # -------------------------------------------------------------
        # result = models.GameResult(
        #     user_id=custom_user.id,
        #     game_name="Card Memory Match",
        #     score=100.0,
        #     accuracy=100.0,
        #     completion_time=180.0,
        #     difficulty_level=1,
        #     date=datetime.datetime.now(datetime.timezone.utc)
        # )
        # db.add(result)

        db.commit()
        print("Seed function executed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error while seeding data: {e}")
        raise
    finally:
        db.close()

def clear_data():
    """
    Helper function to clear all existing tables if you want a completely fresh database.
    """
    database.init_db()
    db = database.SessionLocal()
    try:
        db.query(models.GameResult).delete()
        db.query(models.Memory).delete()
        db.query(models.Reminder).delete()
        db.query(models.User).delete()
        db.commit()
        print("All existing database records cleared successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error clearing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()

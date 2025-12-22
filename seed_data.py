import random

from faker import Faker
from sqlalchemy.orm import Session

from database import Customer, Ticket, TicketStatus, engine

fake = Faker()


def seed_data(num_tickets=10000):
    session = Session(bind=engine)

    # 1. Create some Customers first (e.g., 200)
    print("Generating customers...")
    customers = []
    for _ in range(200):
        c = Customer(name=fake.name(), email=fake.unique.email())
        customers.append(c)

    session.add_all(customers)
    session.commit()  # Commit so they get IDs

    # 2. Create 10000 Tickets
    print(f"Generating {num_tickets} tickets...")
    tickets = []
    for i in range(num_tickets):
        t = Ticket(
            ticket_number=f"TKT-{1000 + i}",
            subject=fake.sentence(nb_words=6),
            description=fake.paragraph(nb_sentences=3),
            status=random.choice(list(TicketStatus)),
            customer_id=random.choice(customers).id,
            created_at=fake.date_time_this_year(),
        )
        tickets.append(t)

    # Use bulk_save_objects for speed with 2000 rows
    session.bulk_save_objects(tickets)
    session.commit()
    print("Done!")


if __name__ == "__main__":
    seed_data()

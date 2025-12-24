import random
from datetime import timedelta

from faker import Faker
from sqlalchemy.orm import Session

from database import Customer, Invoice, Ticket, TicketStatus, engine  # Added Invoice

fake = Faker()


def seed_data(num_tickets=10000, num_invoices=5000):
    session = Session(bind=engine)

    # 1. Create Customers
    print("Generating customers...")
    customers = []
    for _ in range(200):
        c = Customer(name=fake.name(), email=fake.unique.email())
        customers.append(c)

    session.add_all(customers)
    session.commit()  # IDs are generated here

    # 2. Create Tickets
    print(f"Generating {num_tickets} tickets...")
    tickets = []
    for i in range(num_tickets):
        t = Ticket(
            ticket_number=f"TKT-{1000 + i}",
            subject=fake.sentence(nb_words=6),
            description=fake.paragraph(nb_sentences=3),
            status=random.choice(list(TicketStatus)),
            customer_id=random.choice(customers).id,  # Randomly pick a customer
            created_at=fake.date_time_this_year(),
        )
        tickets.append(t)

    session.bulk_save_objects(tickets)

    # 3. Create Invoices
    print(f"Generating {num_invoices} invoices...")
    invoices = []
    for i in range(num_invoices):
        issued_date = fake.date_time_this_year()
        due_date = issued_date + timedelta(days=random.randint(14, 30))

        inv = Invoice(
            invoice_number=f"INV-{fake.unique.bothify(text='#####-??')}",
            amount=random.randint(1000, 50000),
            issued_date=issued_date,
            due_date=due_date,
            customer_id=random.choice(customers).id,  # Randomly pick a customer
        )
        invoices.append(inv)

    session.bulk_save_objects(invoices)
    session.commit()
    print("Done!")


if __name__ == "__main__":
    seed_data()

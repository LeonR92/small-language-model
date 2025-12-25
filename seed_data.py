import random
from datetime import timedelta

from faker import Faker
from sqlalchemy.orm import Session

from database import (
    Customer,
    CustomerDetail,
    Invoice,
    Ticket,
    TicketStatus,
    engine,
)

fake = Faker()


def seed_data(num_tickets=1000, num_invoices=500):
    session = Session(bind=engine)

    # 1. Create Customers & Their Details
    print("Generating 200 customers and their details...")
    customers = []
    for _ in range(200):
        # Create the customer
        new_customer = Customer(name=fake.name(), email=fake.unique.email())

        # Create the detail linked to this customer
        # We can pass the customer object directly to the relationship
        detail = CustomerDetail(
            address=fake.street_address(),
            phone_number=fake.phone_number()[:20],
            country=fake.country(),
            city=fake.city(),
            is_vip=random.choice([0, 1]),
            customer=new_customer,  # SQLAlchemy links the ID automatically
        )

        session.add(new_customer)
        session.add(detail)
        customers.append(new_customer)

    # Commit here so we have actual IDs for the foreign keys below
    session.commit()

    # 2. Create Tickets
    print(f"Generating {num_tickets} tickets...")
    tickets = []
    for i in range(num_tickets):
        t = Ticket(
            ticket_number=f"TKT-{1000 + i}",
            subject=fake.sentence(nb_words=4),
            description=fake.paragraph(nb_sentences=2),
            status=random.choice(list(TicketStatus)),
            customer_id=random.choice(customers).id,
            created_at=fake.date_time_this_year(),
        )
        tickets.append(t)

    # 3. Create Invoices
    print(f"Generating {num_invoices} invoices...")
    invoices = []
    for i in range(num_invoices):
        issued_date = fake.date_time_this_year()
        due_date = issued_date + timedelta(days=random.randint(14, 30))

        inv = Invoice(
            invoice_number=f"INV-{fake.unique.bothify(text='#####-??')}",
            amount=random.uniform(500.0, 10000.0),  # Use uniform for float currency
            issued_date=issued_date,
            due_date=due_date,
            customer_id=random.choice(customers).id,
        )
        invoices.append(inv)

    # Final batch add and commit
    session.add_all(tickets)
    session.add_all(invoices)
    session.commit()
    print("Seeding Complete!")


if __name__ == "__main__":
    seed_data()

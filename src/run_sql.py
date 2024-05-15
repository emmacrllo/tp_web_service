from sqlalchemy import create_engine, text

db_string = "postgresql://root:root@localhost:5432/postgres"

engine = create_engine(db_string)

create_table_statement = text("""
CREATE TABLE IF NOT EXISTS films (
    title text,
    director text,
    year text
)
""")

insert_statement = text("""
    INSERT INTO films (title, director, year) 
    VALUES ('Doctor Strange', 'Scott Derrickson', '2016')
""")

with engine.connect() as connection:
    trans = connection.begin()  
    connection.execute(create_table_statement)
    connection.execute(insert_statement)
    trans.commit()  

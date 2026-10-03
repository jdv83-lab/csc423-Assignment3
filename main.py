import sqlite3

def drop_tables(cursor: sqlite3.Cursor) -> None:

    stmt_fk_off: str = '''
        PRAGMA foreign_keys = OFF;
    '''
    select_drop_tables: str = '''
        SELECT 'DROP TABLE IF EXISTS "' || name || '";' AS command
        FROM sqlite_master 
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%';
    '''

    cursor.execute(stmt_fk_off)
    cursor.execute(select_drop_tables)

    stmt_drop_tables: list[sqlite3.Row] = cursor.fetchall()
    for stmt in stmt_drop_tables:
        cursor.execute(stmt['command'])
    cursor.connection.commit()


def create_tables(cursor: sqlite3.Cursor) -> None:
    stmt_fk_on: str = '''
        PRAGMA foreign_keys = ON;
    '''
    tables: list[str] = []
    create_Staff =   '''
        CREATE TABLE IF NOT EXISTS Staff (
            id                      INTEGER PRIMARY KEY,
            name                    VARCHAR(255),
            departmentName          VARCHAR(255),
            skillID                 INTEGER,
            FOREIGN KEY (skillID)   REFERENCES Skill(id) 
            ON UPDATE CASCADE
            ON DELETE CASCADE
        )
    '''
    tables.append(create_Staff)
    create_Skill =   '''
        CREATE TABLE IF NOT EXISTS Skill (
            id                      INTEGER PRIMARY KEY,
            description             VARCHAR(255),
            chargeOutRate           REAL,

            CHECK (description IN ('Analyst', 'Manager', 'Programmer')),
            CHECK (chargeOutRate >= 15 and chargeOutRate <= 200)
        )
    '''
    tables.append(create_Skill)
    create_Project = '''
        CREATE TABLE IF NOT EXISTS Project (
            id                      INTEGER PRIMARY KEY,
            startDate               DATE,
            endDate                 DATE,
            budget                  REAL,

            CHECK (startDate <= endDate)
        )
    '''
    tables.append(create_Project)
    create_Booking = '''
        CREATE TABLE IF NOT EXISTS Booking (
            staffID                 INTEGER,
            projectID               INTEGER,
            dateWorkedOn            DATE,
            hoursWorked             REAL,

            FOREIGN KEY (staffID)   REFERENCES Staff(id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,

            FOREIGN KEY (projectID) REFERENCES Project(id)
            ON UPDATE CASCADE
            ON DELETE CASCADE,

            PRIMARY KEY (staffID, projectID, hoursWorked, dateWorkedOn),
            CHECK (hoursWorked > 0 AND hoursWorked <= 150)
        )
    '''
    tables.append(create_Booking)

    cursor.execute(stmt_fk_on)
    for table in tables:
        cursor.execute(table)
    cursor.connection.commit()


def populate_tables(cursor: sqlite3.Cursor) -> None:
    inserts: list[str] = []
    insert_Skill = '''
        INSERT INTO Skill
            (description,   chargeOutRate)
        VALUES
            ('Analyst',     50.5),
            ('Programmer',  40.5),
            ('Manager',     35.5),
            ('Manager',     40.5),
            ('Manager',     50.5);
    '''
    inserts.append(insert_Skill)
    insert_Staff = '''
        INSERT INTO Staff 
            (name, departmentName, skillID)
        VALUES
            ('Juan', 'csc', 1),
            ('Juan', 'csc', 2),
            ('Juan', 'csc', 3),
            ('Daniel', 'R&D', 1),
            ('Maria', 'assets', 1);
    '''
    inserts.append(insert_Staff)    
    insert_Project = '''
        INSERT INTO Project
            (startDate,  endDate)
        VALUES
            ('2026-09-01', '2026-10-01'),
            ('2026-09-01', '2026-10-01'),
            ('2026-09-01', '2026-10-01'),
            ('2026-09-01', '2026-10-01'),
            ('2026-09-01', '2026-10-01');
    '''
    inserts.append(insert_Project)
    insert_Booking = '''
        INSERT INTO Booking
            (staffID, projectID, dateWorkedOn, hoursWorked)
        VALUES
            (1, 1, '2026-09-30', 0.1),
            (1, 2, '2026-10-01', 1.0),
            (1, 1, '2026-10-02', 2.0),
            (1, 2, '2026-10-03', 3.0),
            (4, 3, '2026-10-04', 4.0);
    '''
    inserts.append(insert_Booking)

    for insert in inserts:
        cursor.execute(insert)
        cursor.connection.commit()

def reduce_skill_wages(cursor: sqlite3.Cursor, pos: str, 
                       scalar: float) -> None:

    select_skill: str = '''
        SELECT 
            ID, description, chargeOutRate
        FROM Skill
    '''
    update_skill: str = '''
        UPDATE Skill SET
            chargeOutRate = :chargeOutRate
        WHERE 
            id = :id
    '''
    cursor.execute(select_skill)
    skill: list[sqlite3.Row[int, str,float]] = cursor.fetchall()

    changes: dict[str: float | str] = {}
    for row in skill:
        changes['chargeOutRate'] = row['chargeOutRate'] * scalar
        changes['id'] = row['id']
        cursor.execute(update_skill, changes)

    cursor.connection.commit()


def promote_someone(cursor: sqlite3.Cursor, 
                    position: str, promoted_to: str) -> None:
    select_staff: str = '''
        SELECT 
            Staff.id, Staff.name, Skill.description
        FROM Staff
        INNER JOIN Skill ON Staff.skillID = Skill.id;
    '''

    update_staff: str = '''
        UPDATE Staff SET
            skillID = :skillID
        WHERE
            id      = :id
    '''

    cursor.execute('SELECT id FROM Skill WHERE description = ? LIMIT 1;', (promoted_to,))
    promoted_to_ID: int = cursor.fetchone()['id']

    cursor.execute(select_staff)
    staff: list[sqlite3.Row[int, str, int]] = cursor.fetchall()
    change: dict[str, int | str] = {}
    for row in staff:
        if row['description'] == position:
            change['id']   = row['id']
            change['name'] = row['name']
            change['previous_pos'] = row['description']
            change['new_pos'] = promoted_to
            change['skillID'] = promoted_to_ID

            cursor.execute(update_staff, change)
            break
    cursor.connection.commit()

def delete_known_RnD_projects(cursor: sqlite3.Cursor) -> None:
    delete_stmt: str = '''
    DELETE FROM Project WHERE
    id in ( 
    SELECT 
        projectID
    FROM Booking
    INNER JOIN Staff
    ON Booking.staffID = Staff.id
    WHERE Staff.departmentName = 'R&D'
    )
    '''

    cursor.execute(delete_stmt)
    cursor.connection.commit()

def main() -> None:
    con: sqlite3.Connection = sqlite3.connect('data.db')
    con.row_factory = sqlite3.Row
    cursor: sqlite3.Cursor | None = con.cursor()

    drop_tables(cursor)
    create_tables(cursor)
    populate_tables(cursor)

    reduce_skill_wages(cursor, 'Programmer', 0.95)
    promote_someone(cursor, 'Analyst', 'Manager')
    delete_known_RnD_projects(cursor)

    con.close()
    cursor = None

if __name__ == '__main__':
    main()
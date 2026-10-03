PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Staff (
    id                      INTEGER PRIMARY KEY,
    name                    VARCHAR(255),
    departmentName          VARCHAR(255),
    skillID                 INTEGER,
    FOREIGN KEY (skillID)   REFERENCES Skill(id) 
    ON UPDATE CASCADE
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Skill (
    id                      INTEGER PRIMARY KEY,
    description             VARCHAR(255),
    chargeOutRate           REAL,

    CHECK (description IN ('Analyst', 'Manager', 'Programmer')),
    CHECK (chargeOutRate >= 15 and chargeOutRate <= 200)
);

CREATE TABLE IF NOT EXISTS Project (
    id                      INTEGER PRIMARY KEY,
    startDate               DATE,
    endDate                 DATE,
    budget                  REAL,

    CHECK (startDate <= endDate)
);

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
);




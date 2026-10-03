.read scripts/data/asserts/Skill/charge/good.sql

INSERT INTO Staff 
    (name, departmentName, skillID)
VALUES
    ('Juan', 'csc', 1);

.read scripts/data/asserts/Project/end/good.sql

INSERT INTO Booking
    (staffID, projectID, dateWorkedOn, hoursWorked)
VALUES
    (1, 1, CURRENT_DATE, 0.1),
    (1, 1, '2027-01-01', 150);